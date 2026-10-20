from fastapi import APIRouter, Depends

from app.auth import CurrentUser, require_roles
from app.routers.invoices import invoice_rows, shaped

router = APIRouter()

ACCOUNTING = ("admin", "accountant")


@router.get("/accounting/receivables")
def receivables(user: CurrentUser = Depends(require_roles(*ACCOUNTING))):
    """Open invoices in the shared invoice shape, so the numbers match the invoice pages."""
    return [shaped(row) for row in invoice_rows(user.company_id, status="open")]
