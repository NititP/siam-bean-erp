from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from supabase_auth.errors import AuthApiError

from app.auth import CurrentUser, require_roles
from app.db import get_db

router = APIRouter()

COLUMNS = "id, email, full_name, role"
ROLES = ("admin", "sales", "warehouse", "accountant")
MIN_PASSWORD = 8


class UserIn(BaseModel):
    # Missing text defaults to "" so checked() can say which field to fill in.
    email: str = ""
    full_name: str = ""
    role: str = ""
    password: str = ""


class UserPatch(BaseModel):
    role: str = ""


def checked_role(role: str) -> str:
    if role not in ROLES:
        raise HTTPException(422, f"Role must be one of {', '.join(ROLES)}.")
    return role


def email_taken(email: str) -> HTTPException:
    return HTTPException(422, f"A user with email {email} already exists.")


@router.get("/users")
def list_users(user: CurrentUser = Depends(require_roles("admin"))):
    return (
        get_db()
        .table("users")
        .select(COLUMNS)
        .eq("company_id", user.company_id)
        .order("full_name")
        .execute()
        .data
    )


@router.post("/users", status_code=201)
def create_user(body: UserIn, user: CurrentUser = Depends(require_roles("admin"))):
    """A new employee: a confirmed login in Supabase Auth plus their row in users."""
    email = body.email.strip().lower()
    full_name = body.full_name.strip()
    if not email:
        raise HTTPException(422, "Email is required.")
    if not full_name:
        raise HTTPException(422, "Full name is required.")
    role = checked_role(body.role)
    if len(body.password) < MIN_PASSWORD:
        raise HTTPException(422, f"Password must be at least {MIN_PASSWORD} characters.")
    if get_db().table("users").select("id").eq("email", email).execute().data:
        raise email_taken(email)

    try:
        auth_user = (
            get_db().auth.admin.create_user({"email": email, "password": body.password, "email_confirm": True}).user
        )
    except AuthApiError as error:
        if error.code == "email_exists":
            raise email_taken(email)
        raise HTTPException(422, error.message)

    row = {"id": auth_user.id, "company_id": user.company_id, "email": email, "full_name": full_name, "role": role}
    try:
        get_db().table("users").insert(row).execute()
    except Exception:
        # Nothing half-made: a login without a users row would have no role.
        get_db().auth.admin.delete_user(auth_user.id)
        raise
    return {key: row[key] for key in ("id", "email", "full_name", "role")}


@router.patch("/users/{user_id}")
def change_role(user_id: UUID, body: UserPatch, user: CurrentUser = Depends(require_roles("admin"))):
    role = checked_role(body.role)
    if str(user_id) == user.id:
        raise HTTPException(422, "You cannot change your own role.")
    rows = (
        get_db()
        .table("users")
        .update({"role": role})
        .eq("id", str(user_id))
        .eq("company_id", user.company_id)
        .execute()
        .data
    )
    if not rows:
        raise HTTPException(404, "User not found.")
    return {key: rows[0][key] for key in ("id", "email", "full_name", "role")}
