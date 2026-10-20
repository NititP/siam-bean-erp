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


# ---------- Ticket 05: create and edit (admin only) ----------

NEW_PRODUCT = {
    "sku": "GEI-250",
    "name": "Geisha, 250 g bag",
    "unit": "bag",
    "cost": 400,
    "price": 650,
    "reorder_level": 10,
}
OTHER_ROLES = ["sales", "warehouse", "accountant"]


def product_id(client, sku: str) -> int:
    return by_sku(client.get("/products"))[sku]["id"]


def test_admin_creates_a_product_and_it_appears_in_the_list(client_as):
    admin = client_as("admin")

    response = admin.post("/products", json=NEW_PRODUCT)

    assert response.status_code == 201
    assert response.json()["sku"] == "GEI-250"
    geisha = by_sku(admin.get("/products"))["GEI-250"]
    assert geisha["name"] == "Geisha, 250 g bag"
    assert geisha["unit"] == "bag"
    assert geisha["price"] == 650.00
    assert geisha["on_hand"] == 0
    assert geisha["low_stock"] is True


def test_creating_a_duplicate_sku_is_422_naming_the_sku(client_as):
    response = client_as("admin").post("/products", json={**NEW_PRODUCT, "sku": "ARB-1KG"})

    assert response.status_code == 422
    assert "ARB-1KG" in response.json()["detail"]


def test_editing_a_sku_to_one_already_used_is_422_naming_the_sku(client_as):
    admin = client_as("admin")

    response = admin.patch(f"/products/{product_id(admin, 'ROB-1KG')}", json={"sku": "ARB-1KG"})

    assert response.status_code == 422
    assert "ARB-1KG" in response.json()["detail"]
    assert "ROB-1KG" in by_sku(admin.get("/products"))


@pytest.mark.parametrize(
    "bad",
    [
        {"price": -1},
        {"cost": -0.01},
        {"sku": ""},
        {"sku": "   "},
        {"name": ""},
        {"name": "   "},
    ],
)
def test_creating_with_bad_input_is_422(client_as, bad):
    admin = client_as("admin")

    response = admin.post("/products", json={**NEW_PRODUCT, **bad})

    assert response.status_code == 422
    assert response.json()["detail"]
    assert set(by_sku(admin.get("/products"))) == SEED_SKUS


def test_editing_to_a_negative_price_is_422(client_as):
    admin = client_as("admin")

    response = admin.patch(f"/products/{product_id(admin, 'ARB-1KG')}", json={"price": -5})

    assert response.status_code == 422
    assert by_sku(admin.get("/products"))["ARB-1KG"]["price"] == 450.00


def test_admin_edits_a_product_price_and_the_rest_stays(client_as):
    admin = client_as("admin")

    response = admin.patch(f"/products/{product_id(admin, 'ARB-1KG')}", json={"price": 480})

    assert response.status_code == 200
    arabica = by_sku(admin.get("/products"))["ARB-1KG"]
    assert arabica["price"] == 480.00
    assert arabica["name"] == "Arabica, 1 kg bag"
    assert arabica["unit"] == "kg"
    assert arabica["on_hand"] == 170


def test_editing_an_unknown_product_is_404(client_as):
    response = client_as("admin").patch("/products/999999", json={"price": 480})

    assert response.status_code == 404
    assert response.json()["detail"]


@pytest.mark.parametrize("role", OTHER_ROLES)
def test_other_roles_cannot_create_a_product(client_as, role):
    response = client_as(role).post("/products", json=NEW_PRODUCT)

    assert response.status_code == 403
    assert "GEI-250" not in by_sku(client_as("admin").get("/products"))


@pytest.mark.parametrize("role", OTHER_ROLES)
def test_other_roles_cannot_edit_a_product(client_as, role):
    client = client_as(role)

    response = client.patch(f"/products/{product_id(client, 'ARB-1KG')}", json={"price": 1})

    assert response.status_code == 403
    assert by_sku(client.get("/products"))["ARB-1KG"]["price"] == 450.00
