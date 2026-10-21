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
