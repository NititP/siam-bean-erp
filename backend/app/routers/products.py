from fastapi import APIRouter, Depends, HTTPException
from postgrest.exceptions import APIError
from pydantic import BaseModel

from app.auth import CurrentUser, get_current_user, require_roles
from app.db import get_db

router = APIRouter()

COLUMNS = "id, sku, name, unit, cost, price, reorder_level, active"
UNIQUE_VIOLATION = "23505"


class ProductIn(BaseModel):
    sku: str
    name: str
    unit: str = "kg"
    cost: float
    price: float
    reorder_level: int = 0


class ProductPatch(BaseModel):
    sku: str | None = None
    name: str | None = None
    unit: str | None = None
    cost: float | None = None
    price: float | None = None
    reorder_level: int | None = None


def checked(fields: dict) -> dict:
    """The fields with text trimmed, or 422 saying what to fix."""
    for key in ("sku", "name", "unit"):
        if key in fields:
            fields[key] = (fields[key] or "").strip()
            if not fields[key]:
                raise HTTPException(422, f"{'SKU' if key == 'sku' else key.capitalize()} is required.")
    for key in ("cost", "price"):
        if key in fields and (fields[key] is None or fields[key] < 0):
            raise HTTPException(422, f"{key.capitalize()} must be 0 or more.")
    if "reorder_level" in fields and (fields["reorder_level"] is None or fields["reorder_level"] < 0):
        raise HTTPException(422, "Reorder level must be 0 or more.")
    return fields


def saved(write, sku: str | None):
    """Run an insert or update; a SKU already used is 422 naming it."""
    try:
        return write.execute().data
    except APIError as error:
        if error.code == UNIQUE_VIOLATION:
            raise HTTPException(422, f"SKU {sku} is already used by another product.")
        raise


def with_stock(company_id: int, products: list[dict]) -> list[dict]:
    """Add on_hand and low_stock from the stock_on_hand view to each product."""
    stock = {
        row["product_id"]: row
        for row in get_db()
        .table("stock_on_hand")
        .select("product_id, on_hand, low_stock")
        .eq("company_id", company_id)
        .in_("product_id", [p["id"] for p in products])
        .execute()
        .data
    }
    return [
        {
            **{key: product[key] for key in COLUMNS.split(", ")},
            "cost": round(float(product["cost"]), 2),
            "price": round(float(product["price"]), 2),
            "on_hand": stock[product["id"]]["on_hand"],
            "low_stock": stock[product["id"]]["low_stock"],
        }
        for product in products
    ]


@router.get("/products")
def list_products(include_inactive: bool = False, user: CurrentUser = Depends(get_current_user)):
    """Every role may view products. Stock on hand comes from the stock_on_hand view."""
    query = get_db().table("products").select(COLUMNS).eq("company_id", user.company_id).order("sku")
    if not include_inactive:
        query = query.eq("active", True)
    products = query.execute().data
    return with_stock(user.company_id, products) if products else []


@router.post("/products", status_code=201)
def create_product(body: ProductIn, user: CurrentUser = Depends(require_roles("admin"))):
    fields = checked(body.model_dump())
    rows = saved(get_db().table("products").insert({**fields, "company_id": user.company_id}), fields["sku"])
    return with_stock(user.company_id, rows)[0]


@router.patch("/products/{product_id}")
def edit_product(product_id: int, body: ProductPatch, user: CurrentUser = Depends(require_roles("admin"))):
    """Change only the fields sent."""
    fields = checked(body.model_dump(exclude_unset=True))
    table = get_db().table("products")
    if fields:
        write = table.update(fields).eq("id", product_id).eq("company_id", user.company_id)
        rows = saved(write, fields.get("sku"))
    else:
        rows = table.select(COLUMNS).eq("id", product_id).eq("company_id", user.company_id).execute().data
    if not rows:
        raise HTTPException(404, f"Product {product_id} not found.")
    return with_stock(user.company_id, rows)[0]
