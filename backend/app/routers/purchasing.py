from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.auth import CurrentUser, require_roles
from app.db import get_db
from app.routers.orders import db_call, money

router = APIRouter()

BUYERS = ("admin", "warehouse")
PO_COLUMNS = (
    "id, number, supplier_id, status, order_date, received_at, suppliers(name), "
    "po_items(id, product_id, quantity, unit_cost, products(sku, name, unit))"
)


class POLineIn(BaseModel):
    product_id: int | None = None
    quantity: int | None = None
    unit_cost: float | None = None


class PurchaseOrderIn(BaseModel):
    supplier_id: int | None = None
    lines: list[POLineIn] = []


def shaped(po: dict) -> dict:
    """A purchase order with its supplier name and lines, the one shape the API returns."""
    items = sorted(po["po_items"], key=lambda item: item["id"])
    lines = [
        {
            "id": item["id"],
            "product_id": item["product_id"],
            "sku": item["products"]["sku"],
            "name": item["products"]["name"],
            "unit": item["products"]["unit"],
            "quantity": item["quantity"],
            "unit_cost": money(item["unit_cost"]),
            "line_total": money(item["quantity"] * float(item["unit_cost"])),
        }
        for item in items
    ]
    return {
        "id": po["id"],
        "number": po["number"],
        "supplier_id": po["supplier_id"],
        "supplier_name": po["suppliers"]["name"],
        "status": po["status"],
        "order_date": po["order_date"],
        "received_at": po["received_at"],
        "lines": lines,
        "total": money(sum(line["line_total"] for line in lines)),
    }


def purchase_order(company_id: int, po_id: int) -> dict:
    rows = get_db().table("purchase_orders").select(PO_COLUMNS).eq("id", po_id).eq("company_id", company_id).execute().data
    if not rows:
        raise HTTPException(404, f"Purchase order {po_id} not found.")
    return shaped(rows[0])


@router.get("/suppliers")
def list_suppliers(user: CurrentUser = Depends(require_roles(*BUYERS))):
    """Active suppliers, by name."""
    return (
        get_db()
        .table("suppliers")
        .select("id, name, location, lead_time_days, payment_terms_days")
        .eq("company_id", user.company_id)
        .eq("active", True)
        .order("name")
        .execute()
        .data
    )


@router.get("/purchase-orders")
def list_purchase_orders(user: CurrentUser = Depends(require_roles(*BUYERS))):
    """Every purchase order with its lines, newest first."""
    rows = (
        get_db()
        .table("purchase_orders")
        .select(PO_COLUMNS)
        .eq("company_id", user.company_id)
        .order("id", desc=True)
        .execute()
        .data
    )
    return [shaped(row) for row in rows]


@router.post("/purchase-orders", status_code=201)
def create_purchase_order(body: PurchaseOrderIn, user: CurrentUser = Depends(require_roles(*BUYERS))):
    """Save a draft with the next PO number. Everything is checked before the number is taken."""
    db = get_db()
    if body.supplier_id is None:
        raise HTTPException(422, "Pick a supplier.")
    supplier = (
        db.table("suppliers").select("name, active").eq("id", body.supplier_id).eq("company_id", user.company_id).execute().data
    )
    if not supplier:
        raise HTTPException(404, f"Supplier {body.supplier_id} not found.")
    if not supplier[0]["active"]:
        raise HTTPException(422, f"Supplier {supplier[0]['name']} is inactive.")
    if not body.lines:
        raise HTTPException(422, "Add at least one line.")
    for line in body.lines:
        if line.product_id is None:
            raise HTTPException(422, "Pick a product for every line.")
        if line.quantity is None or line.quantity <= 0:
            raise HTTPException(422, "Quantity must be a whole number above 0.")
        if line.unit_cost is None or line.unit_cost < 0:
            raise HTTPException(422, "Unit cost must be 0 or more.")
    product_ids = {line.product_id for line in body.lines}
    found = db.table("products").select("id").eq("company_id", user.company_id).in_("id", list(product_ids)).execute().data
    missing = product_ids - {row["id"] for row in found}
    if missing:
        raise HTTPException(404, f"Product {min(missing)} not found.")

    number = db_call(db.rpc("next_doc_number", {"p_company": user.company_id, "p_type": "PO"}))
    po = (
        db.table("purchase_orders")
        .insert({"company_id": user.company_id, "number": number, "supplier_id": body.supplier_id, "created_by": user.id})
        .execute()
        .data[0]
    )
    db.table("po_items").insert(
        [
            {"po_id": po["id"], "product_id": line.product_id, "quantity": line.quantity, "unit_cost": round(line.unit_cost, 2)}
            for line in body.lines
        ]
    ).execute()
    return purchase_order(user.company_id, po["id"])


@router.post("/purchase-orders/{po_id}/receive")
def receive_purchase_order(po_id: int, user: CurrentUser = Depends(require_roles(*BUYERS))):
    """receive_po adds every line's quantity to stock on hand, once; again is 422."""
    purchase_order(user.company_id, po_id)  # 404 for another company's PO
    return db_call(get_db().rpc("receive_po", {"p_po_id": po_id, "p_user": user.id}))
