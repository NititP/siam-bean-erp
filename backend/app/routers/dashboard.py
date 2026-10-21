from fastapi import APIRouter, Depends

from app.auth import CurrentUser, get_current_user
from app.db import get_db
from app.routers.invoices import money

router = APIRouter()


@router.get("/dashboard")
def dashboard(user: CurrentUser = Depends(get_current_user)):
    """The five live numbers from dashboard_numbers, for every role. Money as THB with two decimals."""
    numbers = get_db().rpc("dashboard_numbers", {"p_company": user.company_id}).execute().data
    return {
        "sales_today": money(numbers["sales_today"]),
        "low_stock_count": int(numbers["low_stock_count"]),
        "open_invoices_count": int(numbers["open_invoices_count"]),
        "open_receivables": money(numbers["open_receivables"]),
        "stock_value": money(numbers["stock_value"]),
    }
