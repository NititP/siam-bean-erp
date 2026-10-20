from dataclasses import dataclass

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase_auth.errors import AuthError

from app.db import get_db

bearer = HTTPBearer(auto_error=False)


@dataclass
class CurrentUser:
    id: str
    company_id: int
    email: str
    full_name: str
    role: str


def get_user_id(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)) -> str:
    """The token check: who is this Supabase access token for? Tests override only this."""
    if credentials is None:
        raise HTTPException(401, "Log in first.")
    try:
        response = get_db().auth.get_user(credentials.credentials)
    except AuthError:
        response = None
    if response is None or response.user is None:
        raise HTTPException(401, "Your login has expired. Log in again.")
    return response.user.id


def get_current_user(user_id: str = Depends(get_user_id)) -> CurrentUser:
    """The logged-in user with their role and company, from the users table."""
    rows = (
        get_db()
        .table("users")
        .select("id, company_id, email, full_name, role")
        .eq("id", user_id)
        .execute()
        .data
    )
    if not rows:
        raise HTTPException(403, "Your login has no role yet. Ask the owner to set one.")
    return CurrentUser(**rows[0])


def require_roles(*roles: str):
    """Dependency that lets only these roles through; anyone else gets 403."""

    def check(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if user.role not in roles:
            raise HTTPException(403, f"Your role ({user.role}) cannot do this.")
        return user

    return check
