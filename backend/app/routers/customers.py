import re

from fastapi import APIRouter, Depends, HTTPException, Query
from postgrest.exceptions import APIError
from pydantic import BaseModel

from app.auth import CurrentUser, require_roles
from app.db import get_db

router = APIRouter()

PAGE_SIZE = 20
COLUMNS = "id, name, tax_id, payment_terms_days, active"
VIEWERS = ("admin", "sales", "accountant")
EDITORS = ("admin", "sales")


class CustomerIn(BaseModel):
    # Missing text defaults to "" so checked() can say which field to fill in.
    name: str = ""
    tax_id: str = ""
    payment_terms_days: int = 0


class CustomerPatch(BaseModel):
    name: str | None = None
    tax_id: str | None = None
    payment_terms_days: int | None = None


def checked(fields: dict) -> dict:
    """The fields with text trimmed, or 422 saying what to fix."""
    for key, label in (("name", "Name"), ("tax_id", "Tax ID")):
        if key in fields:
            fields[key] = (fields[key] or "").strip()
            if not fields[key]:
                raise HTTPException(422, f"{label} is required.")
    if "payment_terms_days" in fields and (fields["payment_terms_days"] is None or fields["payment_terms_days"] < 0):
        raise HTTPException(422, "Payment terms must be 0 days (cash) or more.")
    return fields


def name_contains(q: str) -> str:
    """A regex for names containing q, every character taken literally.

    Not ilike: PostgREST turns every * in an ilike pattern into %, with no escape.
    """
    return re.escape(q)


@router.get("/customers")
def list_customers(
    q: str = "",
    page: int = Query(1, ge=1),
    include_inactive: bool = False,
    user: CurrentUser = Depends(require_roles(*VIEWERS)),
):
    """One page of customers whose name contains q (ignoring case), with the total count."""

    def matching(columns: str):
        query = get_db().table("customers").select(columns, count="exact").eq("company_id", user.company_id)
        if q.strip():
            query = query.filter("name", "imatch", name_contains(q.strip()))
        if not include_inactive:
            query = query.eq("active", True)
        return query

    start = (page - 1) * PAGE_SIZE
    try:
        response = (
            matching(COLUMNS)
            .order("name")
            .order("id")
            .range(start, start + PAGE_SIZE - 1)
            .execute()
        )
    except APIError as error:
        if error.code != "PGRST103":  # a page past the last one
            raise
        return {"items": [], "total": matching("id").limit(1).execute().count}
    return {"items": response.data, "total": response.count}


@router.post("/customers", status_code=201)
def create_customer(body: CustomerIn, user: CurrentUser = Depends(require_roles(*EDITORS))):
    fields = checked(body.model_dump())
    row = {**fields, "company_id": user.company_id, "created_by": user.id}
    [created] = get_db().table("customers").insert(row).execute().data
    return {key: created[key] for key in COLUMNS.split(", ")}


@router.patch("/customers/{customer_id}")
def edit_customer(customer_id: int, body: CustomerPatch, user: CurrentUser = Depends(require_roles(*EDITORS))):
    """Change only the fields sent."""
    fields = checked(body.model_dump(exclude_unset=True))
    table = get_db().table("customers")
    if fields:
        rows = table.update(fields).eq("id", customer_id).eq("company_id", user.company_id).execute().data
    else:
        rows = table.select(COLUMNS).eq("id", customer_id).eq("company_id", user.company_id).execute().data
    if not rows:
        raise HTTPException(404, f"Customer {customer_id} not found.")
    return {key: rows[0][key] for key in COLUMNS.split(", ")}
