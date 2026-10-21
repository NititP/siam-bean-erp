import pytest


def product_ids(client) -> dict[str, int]:
    return {p["sku"]: p["id"] for p in client.get("/products").json()}


def supplier_id(client, name: str) -> int:
    [supplier] = [s for s in client.get("/suppliers").json() if s["name"] == name]
    return supplier["id"]


def new_purchase_order(client, supplier: str = "Doi Chang Farm", lines=(("ARB-1KG", 200, 320),)):
    """POST /purchase-orders for the named supplier with (sku, quantity, unit_cost) lines."""
    ids = product_ids(client)
    return client.post(
        "/purchase-orders",
        json={
            "supplier_id": supplier_id(client, supplier),
            "lines": [
                {"product_id": ids[sku], "quantity": quantity, "unit_cost": unit_cost}
                for sku, quantity, unit_cost in lines
            ],
        },
    )


# ---------- Suppliers --------------------------------------------------------


@pytest.mark.parametrize("role", ["admin", "warehouse"])
def test_admin_and_warehouse_see_both_suppliers(client_as, role):
    response = client_as(role).get("/suppliers")

    assert response.status_code == 200
    assert sorted(s["name"] for s in response.json()) == ["Doi Chang Farm", "Nan Highland Coffee"]


# ---------- Create a draft purchase order ------------------------------------


@pytest.mark.parametrize("role", ["admin", "warehouse"])
def test_creating_a_purchase_order_makes_draft_po_0001(client_as, role):
    response = new_purchase_order(client_as(role))

    assert response.status_code == 201
    po = response.json()
    assert po["number"] == "PO-0001"
    assert po["status"] == "draft"
    assert po["supplier_name"] == "Doi Chang Farm"
    [line] = po["lines"]
    assert line["sku"] == "ARB-1KG"
    assert line["quantity"] == 200
    assert line["unit_cost"] == 320.00


# ---------- Roles ------------------------------------------------------------


def test_sales_gets_403_on_suppliers_and_purchase_orders(client_as):
    sales = client_as("sales")

    assert sales.get("/suppliers").status_code == 403
    assert sales.post("/purchase-orders", json={"supplier_id": 1, "lines": []}).status_code == 403


# ---------- Receive a purchase order (ticket 21) ------------------------------


def on_hand(client, sku: str) -> int:
    [product] = [p for p in client.get("/products").json() if p["sku"] == sku]
    return product["on_hand"]


def receive(client, po_id: int):
    return client.post(f"/purchase-orders/{po_id}/receive")


@pytest.mark.parametrize("role", ["admin", "warehouse"])
def test_receiving_po_0001_takes_arb_1kg_from_170_to_370(client_as, role):
    client = client_as(role)
    po = new_purchase_order(client).json()
    assert on_hand(client, "ARB-1KG") == 170

    response = receive(client, po["id"])

    assert response.status_code == 200
    assert on_hand(client, "ARB-1KG") == 370
    [listed] = client.get("/purchase-orders").json()
    assert (listed["number"], listed["status"]) == ("PO-0001", "received")


def test_receiving_twice_returns_422_and_leaves_stock_unchanged(client_as):
    client = client_as("warehouse")
    po = new_purchase_order(client).json()
    receive(client, po["id"])

    response = receive(client, po["id"])

    assert response.status_code == 422
    assert "Purchase order PO-0001 was already received" in response.json()["detail"]
    assert on_hand(client, "ARB-1KG") == 370


def test_sales_gets_403_on_receive(client_as):
    po = new_purchase_order(client_as("admin")).json()
    sales = client_as("sales")

    assert receive(sales, po["id"]).status_code == 403
    assert on_hand(sales, "ARB-1KG") == 170


def test_accountant_gets_403_on_receive(client_as):
    po = new_purchase_order(client_as("admin")).json()
    accountant = client_as("accountant")

    assert receive(accountant, po["id"]).status_code == 403
    assert on_hand(accountant, "ARB-1KG") == 170
