import pytest

from app.db import get_db

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


def pay(invoice_id: int, amount: float, *, in_full: bool = False) -> None:
    # Setup only: recording payments through the API is ticket 17.
    row = get_db().table("invoices").select("company_id").eq("id", invoice_id).single().execute().data
    get_db().table("payments").insert({"company_id": row["company_id"], "invoice_id": invoice_id, "amount": amount}).execute()
    if in_full:
        get_db().table("invoices").update({"status": "paid"}).eq("id", invoice_id).execute()


def receivables(client) -> list[dict]:
    response = client.get("/accounting/receivables")
    assert response.status_code == 200
    return response.json()


def test_nothing_is_owed_at_the_start(client_as):
    assert receivables(client_as("accountant")) == []


def test_after_us_1_inv_0001_is_owed_9630(client_as):
    invoice_for(client_as("sales"))

    [invoice] = receivables(client_as("accountant"))

    assert set(invoice) >= SHAPE
    assert invoice["number"] == "INV-0001"
    assert invoice["order_number"] == "SO-0001"
    assert invoice["customer_name"] == "Café Lune"
    assert invoice["total"] == 9630.00
    assert invoice["paid"] == 0.00
    assert invoice["outstanding"] == 9630.00
    assert invoice["status"] == "open"


def test_a_part_paid_invoice_shows_what_is_still_owed(client_as):
    issued = invoice_for(client_as("sales"))
    pay(issued["invoice_id"], 4000)

    [invoice] = receivables(client_as("accountant"))

    assert invoice["paid"] == 4000.00
    assert invoice["outstanding"] == 5630.00


def test_a_paid_invoice_is_not_a_receivable(client_as):
    sales = client_as("sales")
    lune = invoice_for(sales)
    invoice_for(sales, customer="Brew Lab Ari", lines=[("DRP-10", 2)])
    pay(lune["invoice_id"], 9630, in_full=True)

    owed = receivables(client_as("accountant"))

    assert [(i["number"], i["customer_name"], i["outstanding"]) for i in owed] == [
        ("INV-0002", "Brew Lab Ari", 321.00),  # 2 x 150 + 7% VAT
    ]


def test_receivables_agree_with_the_invoice_list(client_as):
    sales = client_as("sales")
    issued = invoice_for(sales)
    pay(issued["invoice_id"], 1000)

    [owed] = receivables(client_as("accountant"))
    [listed] = sales.get("/invoices").json()

    assert {key: owed[key] for key in SHAPE} == {key: listed[key] for key in SHAPE}


@pytest.mark.parametrize("role", ["admin", "accountant"])
def test_admin_and_accountant_see_receivables(client_as, role):
    invoice_for(client_as("sales"))

    assert [i["number"] for i in receivables(client_as(role))] == ["INV-0001"]


@pytest.mark.parametrize("role", ["sales", "warehouse"])
def test_sales_and_warehouse_get_403_on_accounting(client_as, role):
    # US-3: a Sales user gets 403 from the accounting API.
    response = client_as(role).get("/accounting/receivables")

    assert response.status_code == 403
