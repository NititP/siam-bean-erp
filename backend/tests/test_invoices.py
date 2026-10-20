from datetime import date, timedelta

import pytest

from app.db import get_db

UNKNOWN_ID = 999999
SHAPE = {
    "id", "number", "order_number", "customer_name", "issue_date", "due_date",
    "subtotal", "vat", "total", "status", "paid", "outstanding",
}


def invoice_for(client, customer: str = "Café Lune", lines: list[tuple[str, int]] = (("ARB-1KG", 20),)) -> dict:
    """Create a draft and confirm it through the API; returns the confirm response."""
    ids = {p["sku"]: p["id"] for p in client.get("/products").json()}
    [buyer] = client.get("/customers", params={"q": customer}).json()["items"]
    order = client.post(
        "/orders",
        json={
            "customer_id": buyer["id"],
            "lines": [{"product_id": ids[sku], "quantity": quantity} for sku, quantity in lines],
        },
    ).json()
    return client.post(f"/orders/{order['id']}/confirm").json()


def pay(invoice_id: int, amount: float) -> None:
    # Setup only: recording payments through the API is Part 3's ticket.
    row = get_db().table("invoices").select("company_id").eq("id", invoice_id).single().execute().data
    get_db().table("payments").insert({"company_id": row["company_id"], "invoice_id": invoice_id, "amount": amount}).execute()


# ---------- List -------------------------------------------------------------


def test_the_invoice_list_is_empty_at_the_start(client_as):
    response = client_as("sales").get("/invoices")

    assert response.status_code == 200
    assert response.json() == []


def test_after_us_1_inv_0001_is_open_with_9630_outstanding(client_as):
    sales = client_as("sales")
    issued = invoice_for(sales)

    [invoice] = sales.get("/invoices").json()

    assert set(invoice) >= SHAPE
    assert invoice["id"] == issued["invoice_id"]
    assert invoice["number"] == "INV-0001"
    assert invoice["order_number"] == "SO-0001"
    assert invoice["customer_name"] == "Café Lune"
    assert invoice["subtotal"] == 9000.00
    assert invoice["vat"] == 630.00
    assert invoice["total"] == 9630.00
    assert invoice["paid"] == 0.00
    assert invoice["outstanding"] == 9630.00
    assert invoice["status"] == "open"
    assert date.fromisoformat(invoice["due_date"]) == date.fromisoformat(invoice["issue_date"]) + timedelta(days=30)


def test_the_invoice_list_shows_newest_first(client_as):
    sales = client_as("sales")
    invoice_for(sales)
    invoice_for(sales, customer="Brew Lab Ari", lines=[("DRP-10", 2)])

    numbers = [(i["number"], i["customer_name"]) for i in sales.get("/invoices").json()]

    assert numbers == [("INV-0002", "Brew Lab Ari"), ("INV-0001", "Café Lune")]


def test_a_part_payment_shows_as_paid_and_outstanding(client_as):
    sales = client_as("sales")
    issued = invoice_for(sales)
    pay(issued["invoice_id"], 4000)

    [invoice] = sales.get("/invoices").json()

    assert invoice["paid"] == 4000.00
    assert invoice["outstanding"] == 5630.00
    assert invoice["status"] == "open"


# ---------- Detail -----------------------------------------------------------


def test_invoice_detail_has_the_shape_lines_and_payments(client_as):
    sales = client_as("sales")
    issued = invoice_for(sales, lines=[("ARB-1KG", 20), ("DRP-10", 2)])
    pay(issued["invoice_id"], 1000)

    response = sales.get(f"/invoices/{issued['invoice_id']}")

    assert response.status_code == 200
    invoice = response.json()
    assert set(invoice) >= SHAPE | {"lines", "payments"}
    assert invoice["number"] == "INV-0001"
    assert invoice["subtotal"] == 9300.00  # 20 x 450 + 2 x 150
    assert invoice["vat"] == 651.00
    assert invoice["total"] == 9951.00
    assert invoice["paid"] == 1000.00
    assert invoice["outstanding"] == 8951.00
    assert [(l["sku"], l["quantity"], l["unit_price"], l["line_total"]) for l in invoice["lines"]] == [
        ("ARB-1KG", 20, 450.00, 9000.00),
        ("DRP-10", 2, 150.00, 300.00),
    ]
    [payment] = invoice["payments"]
    assert payment["amount"] == 1000.00
    assert payment["paid_at"]


def test_invoice_detail_and_list_agree(client_as):
    sales = client_as("sales")
    issued = invoice_for(sales)

    detail = sales.get(f"/invoices/{issued['invoice_id']}").json()
    [row] = sales.get("/invoices").json()

    assert {key: detail[key] for key in SHAPE} == {key: row[key] for key in SHAPE}


def test_an_unknown_invoice_is_404(client_as):
    response = client_as("sales").get(f"/invoices/{UNKNOWN_ID}")

    assert response.status_code == 404
    assert response.json()["detail"] == f"Invoice {UNKNOWN_ID} not found."


# ---------- Roles ------------------------------------------------------------


@pytest.mark.parametrize("role", ["admin", "sales", "accountant"])
def test_admin_sales_and_accountant_see_invoices(client_as, role):
    issued = invoice_for(client_as("sales"))
    client = client_as(role)

    assert [i["number"] for i in client.get("/invoices").json()] == ["INV-0001"]
    assert client.get(f"/invoices/{issued['invoice_id']}").status_code == 200


def test_warehouse_gets_403_on_invoices(client_as):
    issued = invoice_for(client_as("sales"))
    warehouse = client_as("warehouse")

    assert warehouse.get("/invoices").status_code == 403
    assert warehouse.get(f"/invoices/{issued['invoice_id']}").status_code == 403
