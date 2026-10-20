import pytest

UNKNOWN_ID = 999999


def product_ids(client) -> dict[str, int]:
    return {p["sku"]: p["id"] for p in client.get("/products").json()}


def customer_id(client, name: str) -> int:
    [customer] = client.get("/customers", params={"q": name}).json()["items"]
    return customer["id"]


def new_order(client, customer: str = "Café Lune", lines: list[tuple[str, int]] = (("ARB-1KG", 20),)):
    """POST /orders for the named customer with (sku, quantity) lines."""
    ids = product_ids(client)
    return client.post(
        "/orders",
        json={
            "customer_id": customer_id(client, customer),
            "lines": [{"product_id": ids[sku], "quantity": quantity} for sku, quantity in lines],
        },
    )


# ---------- Create a draft -------------------------------------------------


def test_creating_an_order_makes_draft_so_0001(client_as):
    response = new_order(client_as("sales"))

    assert response.status_code == 201
    order = response.json()
    assert order["number"] == "SO-0001"
    assert order["status"] == "draft"
    assert order["customer_name"] == "Café Lune"


def test_order_numbers_follow_on(client_as):
    client = client_as("sales")

    first = new_order(client).json()
    second = new_order(client, customer="Brew Lab Ari").json()

    assert (first["number"], second["number"]) == ("SO-0001", "SO-0002")


def test_order_lines_copy_the_products_price_and_cost(client_as):
    response = new_order(client_as("sales"), lines=[("ARB-1KG", 20), ("DRP-10", 3)])

    lines = {line["sku"]: line for line in response.json()["lines"]}
    assert lines["ARB-1KG"]["quantity"] == 20
    assert lines["ARB-1KG"]["unit_price"] == 450.00
    assert lines["ARB-1KG"]["unit_cost"] == 320.00
    assert lines["DRP-10"]["quantity"] == 3
    assert lines["DRP-10"]["unit_price"] == 150.00
    assert lines["DRP-10"]["unit_cost"] == 90.00


def test_a_later_price_change_does_not_change_the_order_line(client_as):
    sales = client_as("sales")
    order = new_order(sales).json()
    admin = client_as("admin")

    admin.patch(f"/products/{product_ids(admin)['ARB-1KG']}", json={"price": 500, "cost": 350})

    [line] = sales.get(f"/orders/{order['id']}").json()["lines"]
    assert line["unit_price"] == 450.00
    assert line["unit_cost"] == 320.00


def test_an_order_over_stock_on_hand_can_still_be_saved_as_a_draft(client_as):
    response = new_order(client_as("sales"), lines=[("ROB-1KG", 100)])

    assert response.status_code == 201
    assert response.json()["status"] == "draft"


# ---------- Refused orders leave nothing behind ---------------------------


def assert_nothing_left_behind(client):
    """A failed create used no SO number: the next order is still SO-0001."""
    assert new_order(client).json()["number"] == "SO-0001"


def test_an_inactive_customer_is_refused_by_name(client_as):
    sales = client_as("sales")
    brew_id = customer_id(sales, "Brew Lab Ari")
    sales.post(f"/customers/{brew_id}/deactivate")

    response = sales.post(
        "/orders", json={"customer_id": brew_id, "lines": [{"product_id": product_ids(sales)["ARB-1KG"], "quantity": 5}]}
    )

    assert response.status_code == 422
    assert "Brew Lab Ari" in response.json()["detail"]
    assert_nothing_left_behind(sales)


def test_an_inactive_product_is_refused_by_name(client_as):
    sales = client_as("sales")
    admin = client_as("admin")
    ids = product_ids(admin)
    admin.post(f"/products/{ids['ROB-1KG']}/deactivate")

    response = sales.post(
        "/orders",
        json={
            "customer_id": customer_id(sales, "Café Lune"),
            "lines": [{"product_id": ids["ARB-1KG"], "quantity": 5}, {"product_id": ids["ROB-1KG"], "quantity": 5}],
        },
    )

    assert response.status_code == 422
    assert "ROB-1KG" in response.json()["detail"]
    assert_nothing_left_behind(sales)


def test_an_unknown_customer_is_404(client_as):
    sales = client_as("sales")

    response = sales.post(
        "/orders", json={"customer_id": UNKNOWN_ID, "lines": [{"product_id": product_ids(sales)["ARB-1KG"], "quantity": 5}]}
    )

    assert response.status_code == 404
    assert response.json()["detail"]
    assert_nothing_left_behind(sales)


def test_an_unknown_product_is_404(client_as):
    sales = client_as("sales")

    response = sales.post(
        "/orders",
        json={
            "customer_id": customer_id(sales, "Café Lune"),
            "lines": [{"product_id": product_ids(sales)["ARB-1KG"], "quantity": 5}, {"product_id": UNKNOWN_ID, "quantity": 5}],
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"]
    assert_nothing_left_behind(sales)


@pytest.mark.parametrize("quantity", [0, -3])
def test_a_quantity_of_zero_or_below_is_422(client_as, quantity):
    sales = client_as("sales")

    response = new_order(sales, lines=[("ARB-1KG", quantity)])

    assert response.status_code == 422
    assert isinstance(response.json()["detail"], str)
    assert_nothing_left_behind(sales)


def test_an_order_with_no_lines_is_422(client_as):
    sales = client_as("sales")

    response = sales.post("/orders", json={"customer_id": customer_id(sales, "Café Lune"), "lines": []})

    assert response.status_code == 422
    assert isinstance(response.json()["detail"], str)
    assert_nothing_left_behind(sales)


# ---------- Order detail ---------------------------------------------------


def test_order_detail_returns_the_order_with_its_lines(client_as):
    sales = client_as("sales")
    created = new_order(sales, lines=[("ARB-1KG", 20), ("BLD-1KG", 2)]).json()

    response = sales.get(f"/orders/{created['id']}")

    assert response.status_code == 200
    order = response.json()
    assert order["number"] == "SO-0001"
    assert order["customer_name"] == "Café Lune"
    assert order["status"] == "draft"
    assert order["order_date"]
    assert [(line["sku"], line["quantity"]) for line in order["lines"]] == [("ARB-1KG", 20), ("BLD-1KG", 2)]
    assert order["total"] == 9760.00  # 20 x 450 + 2 x 380, before VAT


def test_draft_lines_show_stock_on_hand(client_as):
    sales = client_as("sales")
    created = new_order(sales, lines=[("ARB-1KG", 20), ("ROB-1KG", 100)]).json()

    lines = {line["sku"]: line for line in sales.get(f"/orders/{created['id']}").json()["lines"]}

    assert lines["ARB-1KG"]["on_hand"] == 170
    assert lines["ROB-1KG"]["on_hand"] == 35
    assert lines["ROB-1KG"]["unit"] == "kg"


def test_an_unknown_order_is_404(client_as):
    response = client_as("sales").get(f"/orders/{UNKNOWN_ID}")

    assert response.status_code == 404
    assert response.json()["detail"]


def test_admin_can_create_and_view_an_order(client_as):
    admin = client_as("admin")

    created = new_order(admin)

    assert created.status_code == 201
    assert admin.get(f"/orders/{created.json()['id']}").status_code == 200


# ---------- Roles ----------------------------------------------------------


@pytest.mark.parametrize("role", ["warehouse", "accountant"])
def test_only_sales_and_admin_may_create_orders(client_as, role):
    sales = client_as("sales")
    body = {"customer_id": customer_id(sales, "Café Lune"), "lines": [{"product_id": product_ids(sales)["ARB-1KG"], "quantity": 5}]}

    response = client_as(role).post("/orders", json=body)

    assert response.status_code == 403
    assert_nothing_left_behind(sales)


@pytest.mark.parametrize("role", ["warehouse", "accountant"])
def test_only_sales_and_admin_may_view_an_order(client_as, role):
    created = new_order(client_as("sales")).json()

    response = client_as(role).get(f"/orders/{created['id']}")

    assert response.status_code == 403


# ---------- Order list (ticket 11) ------------------------------------------


def test_the_order_list_is_empty_at_the_start(client_as):
    response = client_as("sales").get("/orders")

    assert response.status_code == 200
    assert response.json() == []


def test_the_order_list_shows_newest_first(client_as):
    sales = client_as("sales")
    new_order(sales)
    new_order(sales, customer="Brew Lab Ari")
    new_order(sales, customer="Sukhumvit Corner Café")

    orders = sales.get("/orders").json()

    assert [(o["number"], o["customer_name"]) for o in orders] == [
        ("SO-0003", "Sukhumvit Corner Café"),
        ("SO-0002", "Brew Lab Ari"),
        ("SO-0001", "Café Lune"),
    ]


def test_an_order_row_has_date_status_and_total_of_its_lines(client_as):
    sales = client_as("sales")
    created = new_order(sales, lines=[("ARB-1KG", 20), ("BLD-1KG", 2)]).json()

    [row] = sales.get("/orders").json()

    assert row["id"] == created["id"]
    assert row["number"] == "SO-0001"
    assert row["customer_name"] == "Café Lune"
    assert row["order_date"] == created["order_date"]
    assert row["status"] == "draft"
    assert row["total"] == 9760.00  # 20 x 450 + 2 x 380, before VAT


def test_admin_sees_every_order(client_as):
    new_order(client_as("sales"))

    response = client_as("admin").get("/orders")

    assert response.status_code == 200
    assert [o["number"] for o in response.json()] == ["SO-0001"]


@pytest.mark.parametrize("role", ["warehouse", "accountant"])
def test_only_sales_and_admin_may_list_orders(client_as, role):
    response = client_as(role).get("/orders")

    assert response.status_code == 403
