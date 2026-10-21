from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.auth import CurrentUser, require_roles
from app.db import get_db

router = APIRouter()


class StockIn(BaseModel):
    product_id: int
    quantity: int | None = None
    note: str | None = None


@router.post("/stock/in", status_code=201)
def stock_in(body: StockIn, user: CurrentUser = Depends(require_roles("admin", "warehouse"))):
    """Add one positive stock movement. Returns it with the product's new stock on hand."""
    products = (
        get_db()
        .table("products")
        .select("id, sku, unit, active")
        .eq("id", body.product_id)
        .eq("company_id", user.company_id)
        .execute()
        .data
    )
    if not products:
        raise HTTPException(404, f"Product {body.product_id} not found.")
    product = products[0]
    if not product["active"]:
        raise HTTPException(422, f"{product['sku']} is inactive. Reactivate it before stocking in.")
    if body.quantity is None or body.quantity <= 0:
        raise HTTPException(422, "Quantity must be more than 0.")
    note = (body.note or "").strip()
    movement = (
        get_db()
        .table("stock_movements")
        .insert(
            {
                "company_id": user.company_id,
                "product_id": product["id"],
                "quantity": body.quantity,
                "ref_doc": f"STOCK-IN: {note}" if note else "STOCK-IN",
                "created_by": user.id,
            }
        )
        .execute()
        .data[0]
    )
    on_hand = (
        get_db()
        .table("stock_on_hand")
        .select("on_hand")
        .eq("product_id", product["id"])
        .single()
        .execute()
        .data["on_hand"]
    )
    return {
        "id": movement["id"],
        "product_id": product["id"],
        "sku": product["sku"],
        "unit": product["unit"],
        "quantity": movement["quantity"],
        "ref_doc": movement["ref_doc"],
        "on_hand": on_hand,
    }
