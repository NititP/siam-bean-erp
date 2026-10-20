import os
import tempfile
from pathlib import Path

import pytest
from dotenv import load_dotenv
from filelock import FileLock

# Load the test settings before the app is imported. They point to the same
# Supabase project as .env, and every test resets its data.
load_dotenv(Path(__file__).resolve().parents[1] / ".env.test", override=True)

from app.db import get_db  # noqa: E402

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
