"""Ticket 19: the scenario's success criterion as one API test.

Café Lune's 20 kg order goes from order to stock to invoice to payment to
dashboard, and the numbers agree on every screen (US-1, US-3, US-4).
"""


def on_hand(client, sku: str) -> float:
    [product] = [p for p in client.get("/products").json() if p["sku"] == sku]
    return product["on_hand"]


def dashboard(client) -> dict:
    response = client.get("/dashboard")
    assert response.status_code == 200
    return response.json()


def test_cafe_lunes_order_goes_from_order_to_payment_and_the_numbers_agree(client_as):
    # The fresh_demo_data fixture has just run reset_demo_data.
    sales = client_as("sales")
    warehouse = client_as("warehouse")
    accountant = client_as("accountant")
    admin = client_as("admin")
    assert on_hand(sales, "ARB-1KG") == 170

    # Sales creates a draft: 20 x ARB-1KG for Café Lune.
    arb = next(p for p in sales.get("/products").json() if p["sku"] == "ARB-1KG")
    [lune] = sales.get("/customers", params={"q": "Café Lune"}).json()["items"]
    created = sales.post(
        "/orders", json={"customer_id": lune["id"], "lines": [{"product_id": arb["id"], "quantity": 20}]}
    )
    assert created.status_code == 201
    order_id = created.json()["id"]

    # US-3: Warehouse cannot confirm, even by calling the API, and nothing changes.
    assert warehouse.post(f"/orders/{order_id}/confirm").status_code == 403
    assert sales.get(f"/orders/{order_id}").json()["status"] == "draft"
    assert on_hand(sales, "ARB-1KG") == 170

    # US-1: Sales confirms; stock drops to 150 and INV-0001 is 9,000 + 630 VAT.
    confirmed = sales.post(f"/orders/{order_id}/confirm")
    assert confirmed.status_code == 200
    issued = confirmed.json()
    assert issued["invoice_number"] == "INV-0001"
    assert (issued["subtotal"], issued["vat"], issued["total"]) == (9000.00, 630.00, 9630.00)
    assert on_hand(sales, "ARB-1KG") == 150

    # The same invoice numbers on the Invoice and Accounting screens.
    invoice = sales.get(f"/invoices/{issued['invoice_id']}").json()
    assert (invoice["number"], invoice["customer_name"]) == ("INV-0001", "Café Lune")
    assert (invoice["total"], invoice["status"], invoice["outstanding"]) == (9630.00, "open", 9630.00)
    [owed] = accountant.get("/accounting/receivables").json()
    assert (owed["number"], owed["outstanding"]) == ("INV-0001", 9630.00)

    # Dashboard: sales today and open receivables are both 9,630.00.
    before = dashboard(admin)
    assert before["sales_today"] == 9630.00
    assert before["open_receivables"] == 9630.00

    # US-4: the accountant records the full payment; the invoice is paid.
    paid = accountant.post(f"/invoices/{issued['invoice_id']}/payments", json={"amount": 9630.00})
    assert paid.status_code == 201
    assert (paid.json()["status"], paid.json()["outstanding"]) == ("paid", 0.00)
    assert accountant.get("/accounting/receivables").json() == []

    # Open receivables drop by 9,630.00; sales today is unchanged.
    after = dashboard(admin)
    assert round(before["open_receivables"] - after["open_receivables"], 2) == 9630.00
    assert after["sales_today"] == 9630.00
