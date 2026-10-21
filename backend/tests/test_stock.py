import pytest

from app.db import get_db

# Ticket 13: stock in (admin, warehouse).


def by_sku(response) -> dict:
    return {row["sku"]: row for row in response.json()}


def product_id(client, sku: str) -> int:
    return by_sku(client.get("/products", params={"include_inactive": "true"}))[sku]["id"]


def on_hand(client, sku: str) -> int:
    return by_sku(client.get("/products", params={"include_inactive": "true"}))[sku]["on_hand"]


def deactivate(sku: str) -> None:
    # Setup only: deactivating is ticket 06, already tested there.
    get_db().table("products").update({"active": False}).eq("sku", sku).execute()


@pytest.mark.parametrize("role", ["admin", "warehouse"])
def test_stocking_in_30_arabica_shows_200_on_hand(client_as, role):
    client = client_as(role)

    response = client.post("/stock/in", json={"product_id": product_id(client, "ARB-1KG"), "quantity": 30})

    assert response.status_code == 201
    assert by_sku(client.get("/products"))["ARB-1KG"]["on_hand"] == 200


def test_the_note_is_saved_as_stock_in_and_the_note(client_as):
    warehouse = client_as("warehouse")

    response = warehouse.post(
        "/stock/in",
        json={"product_id": product_id(warehouse, "ARB-1KG"), "quantity": 30, "note": "Doi Chang delivery"},
    )

    assert response.status_code == 201
    assert response.json()["ref_doc"] == "STOCK-IN: Doi Chang delivery"


@pytest.mark.parametrize("quantity", [0, -5])
def test_a_quantity_of_zero_or_below_is_422_with_a_message(client_as, quantity):
    warehouse = client_as("warehouse")

    response = warehouse.post("/stock/in", json={"product_id": product_id(warehouse, "ARB-1KG"), "quantity": quantity})

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert isinstance(detail, str) and detail
    assert on_hand(warehouse, "ARB-1KG") == 170


def test_an_inactive_product_is_422_naming_the_sku(client_as):
    warehouse = client_as("warehouse")
    deactivate("DRP-10")

    response = warehouse.post("/stock/in", json={"product_id": product_id(warehouse, "DRP-10"), "quantity": 30})

    assert response.status_code == 422
    assert "DRP-10" in response.json()["detail"]
    assert on_hand(warehouse, "DRP-10") == 240


@pytest.mark.parametrize("role", ["sales", "accountant"])
def test_sales_and_accountant_cannot_stock_in(client_as, role):
    client = client_as(role)

    response = client.post("/stock/in", json={"product_id": product_id(client, "ARB-1KG"), "quantity": 30})

    assert response.status_code == 403
    assert on_hand(client, "ARB-1KG") == 170
