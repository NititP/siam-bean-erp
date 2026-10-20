from fastapi import APIRouter, Depends

from app.auth import CurrentUser, get_current_user
from app.db import get_db

router = APIRouter()


@router.get("/products")
def list_products(include_inactive: bool = False, user: CurrentUser = Depends(get_current_user)):
    """Every role may view products. Stock on hand comes from the stock_on_hand view."""
    query = (
        get_db()
        .table("products")
        .select("id, sku, name, unit, price, reorder_level, active")
        .eq("company_id", user.company_id)
        .order("sku")
    )
    if not include_inactive:
        query = query.eq("active", True)
    products = query.execute().data

    stock = {
        row["product_id"]: row
        for row in get_db()
        .table("stock_on_hand")
        .select("product_id, on_hand, low_stock")
        .eq("company_id", user.company_id)
        .execute()
        .data
    }
    return [
        {
            **product,
            "price": round(float(product["price"]), 2),
            "on_hand": stock[product["id"]]["on_hand"],
            "low_stock": stock[product["id"]]["low_stock"],
        }
        for product in products
    ]
