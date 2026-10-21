import pytest

FIVE_NUMBERS = {"sales_today", "low_stock_count", "open_invoices_count", "open_receivables", "stock_value"}


def dashboard(client) -> dict:
    response = client.get("/dashboard")
    assert response.status_code == 200
    return response.json()


def invoice_for_cafe_lune(client) -> dict:
    """US-1: Café Lune's 20 x ARB-1KG draft, confirmed through the API; returns the confirm response."""
    ids = {p["sku"]: p["id"] for p in client.get("/products").json()}
    [lune] = client.get("/customers", params={"q": "Café Lune"}).json()["items"]
    order = client.post(
        "/orders", json={"customer_id": lune["id"], "lines": [{"product_id": ids["ARB-1KG"], "quantity": 20}]}
    ).json()
    return client.post(f"/orders/{order['id']}/confirm").json()


@pytest.mark.parametrize("role", ["admin", "sales", "warehouse", "accountant"])
def test_every_role_sees_the_five_numbers(client_as, role):
    assert set(dashboard(client_as(role))) >= FIVE_NUMBERS


def test_at_the_start_rob_1kg_is_the_one_low_stock_product_and_nothing_is_sold(client_as):
    # US-2: ROB-1KG is low on stock and counted on the dashboard.
    numbers = dashboard(client_as("admin"))

    assert numbers["low_stock_count"] == 1
    assert numbers["sales_today"] == 0.00
    assert numbers["open_invoices_count"] == 0


def test_confirming_cafe_lunes_order_adds_9630_to_sales_today_and_receivables(client_as):
    invoice_for_cafe_lune(client_as("sales"))

    numbers = dashboard(client_as("admin"))

    assert numbers["sales_today"] == 9630.00  # 20 x 450 + 7% VAT
    assert numbers["open_receivables"] == 9630.00


def test_a_full_payment_drops_open_receivables_by_9630(client_as):
    # US-4: paying INV-0001 in full takes 9,630 off open receivables.
    issued = invoice_for_cafe_lune(client_as("sales"))
    accountant = client_as("accountant")
    before = dashboard(accountant)["open_receivables"]

    paid = accountant.post(f"/invoices/{issued['invoice_id']}/payments", json={"amount": 9630.00})
    assert paid.status_code == 201

    assert round(before - dashboard(accountant)["open_receivables"], 2) == 9630.00
