from fastapi import APIRouter, Depends, HTTPException
from postgrest.exceptions import APIError
from pydantic import BaseModel

from app.auth import CurrentUser, require_roles
from app.db import get_db

router = APIRouter()

SELLERS = ("admin", "sales")
# Error codes raised by our Postgres functions (docs/schema.sql).
DB_ERRORS = {"SB404": 404, "SB409": 409, "SB422": 422}


class LineIn(BaseModel):
    product_id: int | None = None
    quantity: int | None = None


class OrderIn(BaseModel):
    customer_id: int | None = None
    lines: list[LineIn] = []


def money(amount) -> float:
    return round(float(amount), 2)


def db_call(rpc):
    """Run an rpc; our functions' error codes become 404 / 409 / 422 with their message."""
    try:
        return rpc.execute().data
    except APIError as error:
        if error.code in DB_ERRORS:
            raise HTTPException(DB_ERRORS[error.code], f"{error.message}.")
        raise


def order_detail(company_id: int, order_id: int) -> dict:
    """The order with its customer and lines. Lines of a draft carry current stock on hand."""
    rows = (
        get_db()
        .table("sales_orders")
        .select(
            "id, number, customer_id, status, order_date, confirmed_at, customers(name), "
            "order_items(id, product_id, quantity, unit_price, unit_cost, products(sku, name, unit))"
        )
        .eq("id", order_id)
        .eq("company_id", company_id)
        .execute()
        .data
    )
    if not rows:
        raise HTTPException(404, f"Order {order_id} not found.")
    order = rows[0]
    items = sorted(order["order_items"], key=lambda item: item["id"])

    on_hand = {}
    if order["status"] == "draft" and items:
        on_hand = {
            row["product_id"]: row["on_hand"]
            for row in get_db()
            .table("stock_on_hand")
            .select("product_id, on_hand")
            .in_("product_id", [item["product_id"] for item in items])
            .execute()
            .data
        }

    lines = [
        {
            "id": item["id"],
            "product_id": item["product_id"],
            "sku": item["products"]["sku"],
            "name": item["products"]["name"],
            "unit": item["products"]["unit"],
            "quantity": item["quantity"],
            "unit_price": money(item["unit_price"]),
            "unit_cost": money(item["unit_cost"]),
            "line_total": money(item["quantity"] * float(item["unit_price"])),
            "on_hand": on_hand.get(item["product_id"]),
        }
        for item in items
    ]
    return {
        "id": order["id"],
        "number": order["number"],
        "customer_id": order["customer_id"],
        "customer_name": order["customers"]["name"],
        "status": order["status"],
        "order_date": order["order_date"],
        "confirmed_at": order["confirmed_at"],
        "lines": lines,
        "total": money(sum(line["line_total"] for line in lines)),  # before VAT
    }


@router.get("/orders")
def list_orders(user: CurrentUser = Depends(require_roles(*SELLERS))):
    """Every order, newest first, with the total of its lines (before VAT)."""
    orders = (
        get_db()
        .table("sales_orders")
        .select("id, number, status, order_date, customers(name), order_items(quantity, unit_price)")
        .eq("company_id", user.company_id)
        .order("id", desc=True)
        .execute()
        .data
    )
    return [
        {
            "id": order["id"],
            "number": order["number"],
            "customer_name": order["customers"]["name"],
            "order_date": order["order_date"],
            "status": order["status"],
            "total": money(sum(money(item["quantity"] * float(item["unit_price"])) for item in order["order_items"])),
        }
        for order in orders
    ]


@router.post("/orders", status_code=201)
def create_order(body: OrderIn, user: CurrentUser = Depends(require_roles(*SELLERS))):
    """A draft with the next SO number; each line copies the product's current price and cost."""
    if body.customer_id is None:
        raise HTTPException(422, "Pick a customer.")
    created = db_call(
        get_db().rpc(
            "create_order",
            {
                "p_company": user.company_id,
                "p_customer": body.customer_id,
                "p_user": user.id,
                "p_lines": [line.model_dump() for line in body.lines],
            },
        )
    )
    return order_detail(user.company_id, created["id"])


@router.get("/orders/{order_id}")
def get_order(order_id: int, user: CurrentUser = Depends(require_roles(*SELLERS))):
    return order_detail(user.company_id, order_id)
