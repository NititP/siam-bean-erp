import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.main import app

# The demo logins from docs/demo_users.sql. client_as("sales") logs in as Nok.
DEMO_USERS = {
    "admin": ("somchai@example.com", "Khun Somchai"),
    "sales": ("nok@example.com", "Nok"),
    "warehouse": ("lek@example.com", "Lek"),
    "accountant": ("fon@example.com", "Fon"),
}


def test_me_without_a_token_is_401():
    response = TestClient(app).get("/me")

    assert response.status_code == 401
    assert response.json()["detail"]


def test_me_with_a_bad_token_is_401():
    response = TestClient(app).get("/me", headers={"Authorization": "Bearer not-a-real-token"})

    assert response.status_code == 401
    assert response.json()["detail"]


@pytest.mark.parametrize("role", DEMO_USERS)
def test_me_returns_the_logged_in_user(client_as, role):
    email, full_name = DEMO_USERS[role]

    response = client_as(role).get("/me")

    assert response.status_code == 200
    assert response.json() == {"email": email, "full_name": full_name, "role": role}


def sales_only_app() -> FastAPI:
    """A small endpoint that only admin and sales may use."""
    from app.auth import require_roles

    tiny = FastAPI()

    @tiny.get("/sales-only", dependencies=[Depends(require_roles("admin", "sales"))])
    def sales_only():
        return {"ok": True}

    return tiny


@pytest.mark.parametrize("role", ["admin", "sales"])
def test_a_role_on_the_list_gets_through(client_as, role):
    response = client_as(role, app=sales_only_app()).get("/sales-only")

    assert response.status_code == 200


@pytest.mark.parametrize("role", ["warehouse", "accountant"])
def test_a_role_not_on_the_list_gets_403(client_as, role):
    response = client_as(role, app=sales_only_app()).get("/sales-only")

    assert response.status_code == 403
    assert response.json()["detail"]


def test_a_protected_endpoint_without_a_token_is_401():
    response = TestClient(sales_only_app()).get("/sales-only")

    assert response.status_code == 401
