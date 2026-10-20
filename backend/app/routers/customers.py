import re

from fastapi import APIRouter, Depends, Query
from postgrest.exceptions import APIError

from app.auth import CurrentUser, require_roles
from app.db import get_db

router = APIRouter()

PAGE_SIZE = 20


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
    user: CurrentUser = Depends(require_roles("admin", "sales", "accountant")),
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
            matching("id, name, tax_id, payment_terms_days, active")
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
