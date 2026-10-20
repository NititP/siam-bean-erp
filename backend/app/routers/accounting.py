from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.auth import CurrentUser, require_roles
from app.db import get_db
from app.routers.invoices import invoice_rows, shaped
from app.routers.orders import db_call

router = APIRouter()

ACCOUNTING = ("admin", "accountant")


class PaymentIn(BaseModel):
    amount: float | None = None


@router.get("/accounting/receivables")
def receivables(user: CurrentUser = Depends(require_roles(*ACCOUNTING))):
    """Open invoices in the shared invoice shape, so the numbers match the invoice pages."""
    return [shaped(row) for row in invoice_rows(user.company_id, status="open")]


@router.post("/invoices/{invoice_id}/payments", status_code=201)
def record_payment(invoice_id: int, body: PaymentIn, user: CurrentUser = Depends(require_roles(*ACCOUNTING))):
    """Record a payment; the invoice becomes paid when payments reach its total. Returns the invoice."""
    if not invoice_rows(user.company_id, invoice_id=invoice_id):
        raise HTTPException(404, f"Invoice {invoice_id} not found.")
    if body.amount is None:
        raise HTTPException(422, "Enter the amount paid.")
    db_call(
        get_db().rpc(
            "record_payment",
            {"p_invoice_id": invoice_id, "p_amount": round(body.amount, 2), "p_user": user.id},
        )
    )
    return shaped(invoice_rows(user.company_id, invoice_id=invoice_id)[0])
