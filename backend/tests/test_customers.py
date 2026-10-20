import time

import pytest

from app.db import get_db

# The three customers in docs/seed.sql, all active at the starting state.
SEED_NAMES = {"Café Lune", "Brew Lab Ari", "Sukhumvit Corner Café"}
EXTRA_SHOPS = 197  # with the seed, 200 customers (US-5)


def names(response) -> set[str]:
    return {row["name"] for row in response.json()["items"]}


def add_bean_shops(count: int = EXTRA_SHOPS) -> None:
    # Setup only: the reset deletes every customer that is not in the seed.
    company_id = get_db().table("companies").select("id").eq("name", "Siam Bean Co.").single().execute().data["id"]
    get_db().table("customers").insert(
        [
            {"company_id": company_id, "name": f"Bean Shop {n:03}", "tax_id": f"0999{n:09}", "payment_terms_days": 30}
            for n in range(1, count + 1)
        ]
    ).execute()


def deactivate(name: str) -> None:
    # Setup only: deactivating through the API is ticket 09.
    get_db().table("customers").update({"active": False}).eq("name", name).execute()


def test_search_matches_part_of_the_name_ignoring_case(client_as):
    client = client_as("sales")

    assert names(client.get("/customers", params={"q": "LUNE"})) == {"Café Lune"}
    assert names(client.get("/customers", params={"q": "café"})) == {"Café Lune", "Sukhumvit Corner Café"}


def test_no_search_lists_every_active_customer(client_as):
    response = client_as("sales").get("/customers")

    assert response.status_code == 200
    assert names(response) == SEED_NAMES
    assert response.json()["total"] == 3


def test_a_customer_row_has_its_details(client_as):
    response = client_as("sales").get("/customers", params={"q": "Café Lune"})

    [lune] = response.json()["items"]
    assert lune["name"] == "Café Lune"
    assert lune["tax_id"] == "0105561000011"
    assert lune["payment_terms_days"] == 30
    assert lune["active"] is True
    assert "id" in lune


def test_a_search_returns_at_most_20_rows_and_the_full_total(client_as):
    add_bean_shops()

    response = client_as("sales").get("/customers", params={"q": "bean shop"})

    assert response.status_code == 200
    assert len(response.json()["items"]) == 20
    assert response.json()["total"] == 197


def test_pages_reach_every_match_without_overlap(client_as):
    add_bean_shops()
    client = client_as("sales")

    pages = [client.get("/customers", params={"q": "bean shop", "page": page}).json() for page in range(1, 11)]

    assert [len(p["items"]) for p in pages] == [20] * 9 + [17]
    seen = [row["name"] for p in pages for row in p["items"]]
    assert len(set(seen)) == 197
    assert pages[0]["items"][0]["name"] == "Bean Shop 001"


def test_search_with_200_customers_answers_within_1_second(client_as):
    add_bean_shops()
    client = client_as("sales")

    started = time.perf_counter()
    response = client.get("/customers", params={"q": "shop 1"})
    elapsed = time.perf_counter() - started

    assert response.status_code == 200
    assert elapsed < 1.0, f"search took {elapsed:.2f}s"


def test_an_inactive_customer_is_hidden_by_default(client_as):
    deactivate("Brew Lab Ari")

    response = client_as("sales").get("/customers")

    assert names(response) == SEED_NAMES - {"Brew Lab Ari"}
    assert response.json()["total"] == 2


def test_include_inactive_also_returns_inactive_customers(client_as):
    deactivate("Brew Lab Ari")

    response = client_as("admin").get("/customers", params={"include_inactive": "true"})

    assert names(response) == SEED_NAMES
    assert response.json()["total"] == 3


@pytest.mark.parametrize("role", ["admin", "sales", "accountant"])
def test_admin_sales_and_accountant_see_customers(client_as, role):
    response = client_as(role).get("/customers")

    assert response.status_code == 200


def test_warehouse_is_refused_the_customer_list(client_as):
    response = client_as("warehouse").get("/customers")

    assert response.status_code == 403
    assert response.json()["detail"]
