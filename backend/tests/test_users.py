import uuid

import pytest

from app.db import get_db

# The five demo logins from docs/demo_users.sql, all in Siam Bean Co.
DEMO_USERS = {
    ("somchai@example.com", "Khun Somchai", "admin"),
    ("nok@example.com", "Nok", "sales"),
    ("ploy@example.com", "Ploy", "sales"),
    ("lek@example.com", "Lek", "warehouse"),
    ("fon@example.com", "Fon", "accountant"),
}
# Every login a test makes starts with this, so the cleanup can find it.
TEST_EMAIL_PREFIX = "users-test-"
NON_ADMIN_ROLES = ["sales", "warehouse", "accountant"]


def new_email() -> str:
    return f"{TEST_EMAIL_PREFIX}{uuid.uuid4().hex[:8]}@example.com"


def delete_test_logins() -> None:
    # The reset does not touch logins, so remove every one a test made.
    # Deleting the auth user also removes its users row (on delete cascade).
    for user in get_db().auth.admin.list_users(page=1, per_page=1000):
        if user.email and user.email.startswith(TEST_EMAIL_PREFIX):
            get_db().auth.admin.delete_user(user.id)


@pytest.fixture(autouse=True)
def no_extra_logins_left_behind():
    delete_test_logins()
    yield
    delete_test_logins()


def add_login(role: str = "sales", full_name: str = "Test Person") -> dict:
    """Setup only: a throwaway login with a role, made straight in Supabase."""
    email = new_email()
    auth_user = get_db().auth.admin.create_user(
        {"email": email, "password": "beans-1234", "email_confirm": True}
    ).user
    company_id = get_db().table("companies").select("id").eq("name", "Siam Bean Co.").single().execute().data["id"]
    get_db().table("users").insert(
        {"id": auth_user.id, "company_id": company_id, "email": email, "full_name": full_name, "role": role}
    ).execute()
    return {"id": auth_user.id, "email": email}


def new_user_body(**changes) -> dict:
    return {"email": new_email(), "full_name": "Mali", "role": "warehouse", "password": "beans-1234"} | changes


def listed(client) -> dict[str, dict]:
    response = client.get("/users")
    assert response.status_code == 200
    return {row["email"]: row for row in response.json()}


# GET /users


def test_admin_lists_every_user_in_the_company(client_as):
    response = client_as("admin").get("/users")

    assert response.status_code == 200
    # The project also holds the team's own logins, so compare with the whole
    # users table for the company, not only the demo users.
    company_id = get_db().table("companies").select("id").eq("name", "Siam Bean Co.").single().execute().data["id"]
    in_company = get_db().table("users").select("email, full_name, role").eq("company_id", company_id).execute().data
    listed_users = {(row["email"], row["full_name"], row["role"]) for row in response.json()}
    assert DEMO_USERS <= listed_users
    assert listed_users == {(row["email"], row["full_name"], row["role"]) for row in in_company}


# POST /users


def test_admin_adds_an_employee_who_can_then_log_in_with_their_role(client_as):
    body = new_user_body(full_name="Mali", role="warehouse")

    response = client_as("admin").post("/users", json=body)

    assert response.status_code == 201
    assert response.json()["email"] == body["email"]
    assert response.json()["full_name"] == "Mali"
    assert response.json()["role"] == "warehouse"
    me = client_as("warehouse", email=body["email"]).get("/me")
    assert me.status_code == 200
    assert me.json() == {"email": body["email"], "full_name": "Mali", "role": "warehouse"}


def test_a_new_employee_login_is_already_confirmed(client_as):
    response = client_as("admin").post("/users", json=new_user_body())

    auth_user = get_db().auth.admin.get_user_by_id(response.json()["id"]).user
    assert auth_user.email_confirmed_at is not None


def test_a_new_employee_joins_the_admins_company(client_as):
    body = new_user_body()

    client_as("admin").post("/users", json=body)

    company_id = get_db().table("companies").select("id").eq("name", "Siam Bean Co.").single().execute().data["id"]
    row = get_db().table("users").select("company_id").eq("email", body["email"]).single().execute().data
    assert row["company_id"] == company_id


def test_a_new_employee_shows_in_the_list(client_as):
    admin = client_as("admin")
    body = new_user_body(full_name="Mali", role="accountant")

    admin.post("/users", json=body)

    assert listed(admin)[body["email"]]["full_name"] == "Mali"
    assert listed(admin)[body["email"]]["role"] == "accountant"


def test_a_duplicate_email_is_422_naming_the_email(client_as):
    response = client_as("admin").post("/users", json=new_user_body(email="nok@example.com"))

    assert response.status_code == 422
    assert "nok@example.com" in response.json()["detail"]


@pytest.mark.parametrize(
    "changes",
    [
        pytest.param({"role": "manager"}, id="unknown role"),
        pytest.param({"full_name": ""}, id="blank name"),
        pytest.param({"full_name": "   "}, id="name of only spaces"),
        pytest.param({"password": "short12"}, id="7-character password"),
    ],
)
def test_bad_new_user_details_are_422_and_add_no_one(client_as, changes):
    admin = client_as("admin")
    body = new_user_body(**changes)

    response = admin.post("/users", json=body)

    assert response.status_code == 422
    assert response.json()["detail"]
    assert body["email"] not in listed(admin)


def test_an_8_character_password_is_enough(client_as):
    response = client_as("admin").post("/users", json=new_user_body(password="beans-12"))

    assert response.status_code == 201


# PATCH /users/{id}


def test_admin_changes_a_users_role(client_as):
    login = add_login(role="sales")

    response = client_as("admin").patch(f"/users/{login['id']}", json={"role": "accountant"})

    assert response.status_code == 200
    assert response.json()["role"] == "accountant"
    me = client_as("accountant", email=login["email"]).get("/me")
    assert me.json()["role"] == "accountant"


def test_changing_to_an_unknown_role_is_422(client_as):
    admin = client_as("admin")
    login = add_login(role="sales")

    response = admin.patch(f"/users/{login['id']}", json={"role": "manager"})

    assert response.status_code == 422
    assert listed(admin)[login["email"]]["role"] == "sales"


def test_an_admin_cannot_change_their_own_role(client_as):
    admin = client_as("admin")
    own_id = get_db().table("users").select("id").eq("email", "somchai@example.com").single().execute().data["id"]

    response = admin.patch(f"/users/{own_id}", json={"role": "sales"})

    assert response.status_code == 422
    assert response.json()["detail"] == "You cannot change your own role."
    assert listed(admin)["somchai@example.com"]["role"] == "admin"


def test_changing_an_unknown_user_is_404(client_as):
    response = client_as("admin").patch(f"/users/{uuid.uuid4()}", json={"role": "sales"})

    assert response.status_code == 404
    assert response.json()["detail"]


# Only admin


@pytest.mark.parametrize("role", NON_ADMIN_ROLES)
def test_only_admin_lists_users(client_as, role):
    response = client_as(role).get("/users")

    assert response.status_code == 403


@pytest.mark.parametrize("role", NON_ADMIN_ROLES)
def test_only_admin_adds_users(client_as, role):
    body = new_user_body()

    response = client_as(role).post("/users", json=body)

    assert response.status_code == 403
    assert body["email"] not in listed(client_as("admin"))


@pytest.mark.parametrize("role", NON_ADMIN_ROLES)
def test_only_admin_changes_roles(client_as, role):
    login = add_login(role="warehouse")

    response = client_as(role).patch(f"/users/{login['id']}", json={"role": "admin"})

    assert response.status_code == 403
    assert listed(client_as("admin"))[login["email"]]["role"] == "warehouse"
