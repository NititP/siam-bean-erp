import pytest

from app.db import get_db

ROLES = ["admin", "sales", "warehouse", "accountant"]
# The four products in docs/seed.sql, all active at the starting state.
SEED_SKUS = {"ARB-1KG", "ROB-1KG", "BLD-1KG", "DRP-10"}


def by_sku(response) -> dict:
    return {row["sku"]: row for row in response.json()}


def deactivate(sku: str) -> None:
    # Setup only: deactivating through the API is ticket 06.
    get_db().table("products").update({"active": False}).eq("sku", sku).execute()


@pytest.mark.parametrize("role", ROLES)
def test_every_role_sees_the_active_products(client_as, role):
    response = client_as(role).get("/products")

    assert response.status_code == 200
    assert set(by_sku(response)) == SEED_SKUS


def test_starting_stock_shows_robusta_low_and_arabica_not_low(client_as):
    products = by_sku(client_as("warehouse").get("/products"))

    assert products["ROB-1KG"]["on_hand"] == 35
    assert products["ROB-1KG"]["low_stock"] is True
    assert products["ARB-1KG"]["on_hand"] == 170
    assert products["ARB-1KG"]["low_stock"] is False


def test_an_inactive_product_is_hidden_by_default(client_as):
    deactivate("DRP-10")

    response = client_as("sales").get("/products")

    assert response.status_code == 200
    assert set(by_sku(response)) == SEED_SKUS - {"DRP-10"}


def test_include_inactive_also_returns_inactive_products(client_as):
    deactivate("DRP-10")

    response = client_as("admin").get("/products", params={"include_inactive": "true"})

    assert response.status_code == 200
    assert set(by_sku(response)) == SEED_SKUS


def test_a_product_row_has_what_the_list_shows(client_as):
    arabica = by_sku(client_as("accountant").get("/products"))["ARB-1KG"]

    assert arabica["name"] == "Arabica, 1 kg bag"
    assert arabica["unit"] == "kg"
    assert arabica["price"] == 450.00
    assert {"sku", "name", "unit", "price", "on_hand", "low_stock"} <= arabica.keys()
