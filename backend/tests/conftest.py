import os
import tempfile
from pathlib import Path

import pytest
from dotenv import load_dotenv
from filelock import FileLock

# Load the test settings before the app is imported. They point to the same
# Supabase project as .env, and every test resets its data.
load_dotenv(Path(__file__).resolve().parents[1] / ".env.test", override=True)

from fastapi import Depends, FastAPI, Request  # noqa: E402
from fastapi.security import HTTPAuthorizationCredentials  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.auth import bearer, get_user_id  # noqa: E402
from app.db import get_db  # noqa: E402
from app.main import app as main_app  # noqa: E402

# One demo login per role (docs/demo_users.sql).
DEMO_EMAILS = {
    "admin": "somchai@example.com",
    "sales": "nok@example.com",
    "warehouse": "lek@example.com",
    "accountant": "fon@example.com",
}
TEST_USER_HEADER = "X-Test-User-Id"

# One file outside all three repo copies, so only one test run at a time on
# this PC. A second run waits here until the first finishes.
LOCK_PATH = os.path.join(tempfile.gettempdir(), "siam-bean-pytest.lock")


@pytest.fixture(scope="session", autouse=True)
def one_test_run_at_a_time():
    with FileLock(LOCK_PATH):
        yield


@pytest.fixture(autouse=True)
def fresh_demo_data(one_test_run_at_a_time):
    get_db().rpc("reset_demo_data", {"p_confirm": "yes-reset"}).execute()


@pytest.fixture
def client_as():
    """client_as("sales") is a TestClient logged in as the sales demo user.

    Only the token check is replaced: the user's role and company still come
    from the users table. Pass app= to log in to another FastAPI app.
    """
    apps: list[FastAPI] = []

    def login(role: str, app: FastAPI = main_app) -> TestClient:
        user_id = (
            get_db().table("users").select("id").eq("email", DEMO_EMAILS[role]).single().execute().data["id"]
        )
        app.dependency_overrides[get_user_id] = _token_check_or_test_user
        apps.append(app)
        return TestClient(app, headers={TEST_USER_HEADER: user_id})

    yield login
    for app in apps:
        app.dependency_overrides.pop(get_user_id, None)


def _token_check_or_test_user(
    request: Request, credentials: HTTPAuthorizationCredentials | None = Depends(bearer)
) -> str:
    # A client from client_as carries its user in a header, so several clients
    # in one test can be different users; any other client gets the real check.
    return request.headers.get(TEST_USER_HEADER) or get_user_id(credentials)
