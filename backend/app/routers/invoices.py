from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response

from app.auth import CurrentUser, require_roles
from app.db import get_db
from app.invoice_pdf import invoice_pdf

router = APIRouter()

VIEWERS = ("admin", "sales", "accountant")
COLUMNS = (
    "id, number, order_id, issue_date, due_date, subtotal, vat, total, status, "
    "customers(name, tax_id), sales_orders(number), payments(amount, paid_at)"
)


def money(amount) -> float:
    return round(float(amount), 2)


def shaped(row: dict) -> dict:
    """The invoice shape every screen shares (docs/plan.md): paid = sum of payments."""
    paid = money(sum(float(p["amount"]) for p in row["payments"]))
    return {
        "id": row["id"],
        "number": row["number"],
        "order_number": row["sales_orders"]["number"],
        "customer_name": row["customers"]["name"],
        "issue_date": row["issue_date"],
        "due_date": row["due_date"],
        "subtotal": money(row["subtotal"]),
        "vat": money(row["vat"]),
        "total": money(row["total"]),
        "status": row["status"],
        "paid": paid,
        "outstanding": money(float(row["total"]) - paid),
    }


def invoice_rows(company_id: int, invoice_id: int | None = None, status: str | None = None) -> list[dict]:
    """Invoices newest first, raw with their customer, order number and payments."""
    query = get_db().table("invoices").select(COLUMNS).eq("company_id", company_id)
    if invoice_id is not None:
        query = query.eq("id", invoice_id)
    if status is not None:
        query = query.eq("status", status)
    return query.order("id", desc=True).execute().data


@router.get("/invoices")
def list_invoices(user: CurrentUser = Depends(require_roles(*VIEWERS))):
    return [shaped(row) for row in invoice_rows(user.company_id)]


def invoice_detail(company_id: int, invoice_id: int) -> dict:
    """The shared shape plus the order lines, the payments made and the customer's tax ID."""
    rows = invoice_rows(company_id, invoice_id=invoice_id)
    if not rows:
        raise HTTPException(404, f"Invoice {invoice_id} not found.")
    row = rows[0]
    items = (
        get_db()
        .table("order_items")
        .select("id, quantity, unit_price, products(sku, name, unit)")
        .eq("order_id", row["order_id"])
        .order("id")
        .execute()
        .data
    )
    return {
        **shaped(row),
        "customer_tax_id": row["customers"]["tax_id"],
        "lines": [
            {
                "sku": item["products"]["sku"],
                "name": item["products"]["name"],
                "unit": item["products"]["unit"],
                "quantity": item["quantity"],
                "unit_price": money(item["unit_price"]),
                "line_total": money(item["quantity"] * float(item["unit_price"])),
            }
            for item in items
        ],
        "payments": [
            {"amount": money(p["amount"]), "paid_at": p["paid_at"]}
            for p in sorted(row["payments"], key=lambda p: p["paid_at"])
        ],
    }


@router.get("/invoices/{invoice_id}")
def get_invoice(invoice_id: int, user: CurrentUser = Depends(require_roles(*VIEWERS))):
    return invoice_detail(user.company_id, invoice_id)


@router.get("/invoices/{invoice_id}/pdf")
def get_invoice_pdf(invoice_id: int, user: CurrentUser = Depends(require_roles(*VIEWERS))):
    """The tax invoice as a PDF download named after its number, e.g. INV-0001.pdf."""
    invoice = invoice_detail(user.company_id, invoice_id)
    company = get_db().table("companies").select("name, tax_id").eq("id", user.company_id).single().execute().data
    return Response(
        invoice_pdf(invoice, company),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{invoice["number"]}.pdf"'},
    )
