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


@pytest.mark.parametrize("q", ["*", "%", "_"])
def test_wildcard_characters_in_a_search_match_only_themselves(client_as, q):
    response = client_as("sales").get("/customers", params={"q": q})

    assert response.status_code == 200
    assert response.json() == {"items": [], "total": 0}


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


# ---------- Ticket 08: create and edit (admin and sales) ----------

NEW_CUSTOMER = {"name": "Roast Room Thonglor", "tax_id": "0105564000044", "payment_terms_days": 15}
EDITORS = ["admin", "sales"]
NOT_EDITORS = ["accountant", "warehouse"]


def customer(client, name: str) -> dict:
    [row] = client.get("/customers", params={"q": name}).json()["items"]
    return row


@pytest.mark.parametrize("role", EDITORS)
def test_admin_and_sales_create_a_customer(client_as, role):
    client = client_as(role)

    response = client.post("/customers", json=NEW_CUSTOMER)

    assert response.status_code == 201
    created = customer(client, "Roast Room")
    assert created["name"] == "Roast Room Thonglor"
    assert created["tax_id"] == "0105564000044"
    assert created["payment_terms_days"] == 15
    assert created["active"] is True


@pytest.mark.parametrize(
    "bad, field",
    [
        ({"tax_id": ""}, "Tax ID"),
        ({"tax_id": "   "}, "Tax ID"),
        ({"name": ""}, "Name"),
        ({"name": "   "}, "Name"),
    ],
)
def test_a_blank_name_or_tax_id_is_422_naming_the_field(client_as, bad, field):
    client = client_as("sales")

    response = client.post("/customers", json={**NEW_CUSTOMER, **bad})

    assert response.status_code == 422
    assert field in response.json()["detail"]
    assert client.get("/customers", params={"q": "Roast Room"}).json()["total"] == 0


@pytest.mark.parametrize("missing, field", [("tax_id", "Tax ID"), ("name", "Name")])
def test_a_missing_name_or_tax_id_is_422_naming_the_field(client_as, missing, field):
    body = {k: v for k, v in NEW_CUSTOMER.items() if k != missing}

    response = client_as("sales").post("/customers", json=body)

    assert response.status_code == 422
    assert field in response.json()["detail"]


def test_negative_payment_terms_are_422(client_as):
    client = client_as("sales")
    lune = customer(client, "Café Lune")

    created = client.post("/customers", json={**NEW_CUSTOMER, "payment_terms_days": -1})
    edited = client.patch(f"/customers/{lune['id']}", json={"payment_terms_days": -1})

    assert created.status_code == 422
    assert edited.status_code == 422
    assert customer(client, "Café Lune")["payment_terms_days"] == 30


@pytest.mark.parametrize("role", EDITORS)
def test_admin_and_sales_edit_a_customer(client_as, role):
    client = client_as(role)
    lune = customer(client, "Café Lune")

    response = client.patch(f"/customers/{lune['id']}", json={"name": "Café Lune Ari", "payment_terms_days": 45})

    assert response.status_code == 200
    edited = customer(client, "Café Lune")
    assert edited["name"] == "Café Lune Ari"
    assert edited["payment_terms_days"] == 45
    assert edited["tax_id"] == "0105561000011"


def test_editing_an_unknown_customer_is_404_from_our_code(client_as):
    response = client_as("sales").patch("/customers/999999", json={"payment_terms_days": 7})

    assert response.status_code == 404
    assert response.json()["detail"] == "Customer 999999 not found."


@pytest.mark.parametrize("role", NOT_EDITORS)
def test_accountant_and_warehouse_cannot_create_a_customer(client_as, role):
    response = client_as(role).post("/customers", json=NEW_CUSTOMER)

    assert response.status_code == 403
    assert client_as("admin").get("/customers", params={"q": "Roast Room"}).json()["total"] == 0


@pytest.mark.parametrize("role", NOT_EDITORS)
def test_accountant_and_warehouse_cannot_edit_a_customer(client_as, role):
    admin = client_as("admin")
    lune = customer(admin, "Café Lune")

    response = client_as(role).patch(f"/customers/{lune['id']}", json={"payment_terms_days": 0})

    assert response.status_code == 403
    assert customer(admin, "Café Lune")["payment_terms_days"] == 30


# ---------- Ticket 09: deactivate and reactivate (admin and sales) ----------


@pytest.mark.parametrize("role", EDITORS)
def test_deactivating_a_customer_hides_them_from_the_default_list(client_as, role):
    client = client_as(role)

    response = client.post(f"/customers/{customer(client, 'Brew Lab')['id']}/deactivate")

    assert response.status_code == 200
    assert "Brew Lab Ari" not in names(client.get("/customers"))
    [shown] = client.get("/customers", params={"q": "Brew Lab", "include_inactive": "true"}).json()["items"]
    assert shown["active"] is False


def test_patching_active_true_brings_a_customer_back(client_as):
    client = client_as("sales")
    brew_lab = customer(client, "Brew Lab")["id"]
    client.post(f"/customers/{brew_lab}/deactivate")
    assert "Brew Lab Ari" not in names(client.get("/customers"))

    response = client.patch(f"/customers/{brew_lab}", json={"active": True})

    assert response.status_code == 200
    assert customer(client, "Brew Lab")["active"] is True


@pytest.mark.parametrize("role", NOT_EDITORS)
def test_accountant_and_warehouse_cannot_deactivate_a_customer(client_as, role):
    admin = client_as("admin")
    brew_lab = customer(admin, "Brew Lab")["id"]

    response = client_as(role).post(f"/customers/{brew_lab}/deactivate")

    assert response.status_code == 403
    assert "Brew Lab Ari" in names(admin.get("/customers"))


def test_deactivating_an_unknown_customer_is_404_from_our_code(client_as):
    response = client_as("sales").post("/customers/999999/deactivate")

    assert response.status_code == 404
    assert response.json()["detail"] == "Customer 999999 not found."
