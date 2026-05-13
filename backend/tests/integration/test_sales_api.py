from uuid import uuid4


def make_product(client, sku="SALE-001"):
    return client.post("/api/v1/products/", json={
        "sku": sku,
        "name": "Sale Test Product",
        "description": "For sale testing",
        "category": "electronics",
        "price_cents": 1000,
        "currency": "USD"
    }).json()


def make_inventory(client, product_id, quantity=100, reorder_level=10):
    return client.post("/api/v1/inventory/", json={
        "product_id": product_id,
        "quantity_on_hand": quantity,
        "reorder_level": reorder_level
    }).json()


def make_full_setup(client, sku="SALE-001", quantity=100):
    product = make_product(client, sku=sku)
    inventory = make_inventory(client, product["id"], quantity=quantity)
    return product, inventory


# ── Happy Path ────────────────────────────────────────────────────────────────

def test_record_sale_success(client):
    product, inventory = make_full_setup(client)
    response = client.post("/api/v1/sales/", json={
        "product_id": product["id"],
        "inventory_id": inventory["id"],
        "quantity_sold": 10,
        "price_at_sale": 1000
    })
    assert response.status_code == 201
    data = response.json()
    assert data["quantity_sold"] == 10
    assert data["price_at_sale"] == 1000
    assert data["product_id"] == product["id"]


def test_sale_deducts_stock(client):
    """Verifies stock is correctly reduced after a sale."""
    product, inventory = make_full_setup(client, quantity=100)
    client.post("/api/v1/sales/", json={
        "product_id": product["id"],
        "inventory_id": inventory["id"],
        "quantity_sold": 10,
        "price_at_sale": 1000
    })
    inv = client.get(f"/api/v1/inventory/{product['id']}").json()
    assert inv["quantity_on_hand"] == 90


def test_get_sales_by_product(client):
    product, inventory = make_full_setup(client)
    client.post("/api/v1/sales/", json={
        "product_id": product["id"],
        "inventory_id": inventory["id"],
        "quantity_sold": 5,
        "price_at_sale": 1000
    })
    response = client.get(f"/api/v1/sales/product/{product['id']}")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_sale_by_id(client):
    product, inventory = make_full_setup(client)
    sale = client.post("/api/v1/sales/", json={
        "product_id": product["id"],
        "inventory_id": inventory["id"],
        "quantity_sold": 5,
        "price_at_sale": 1000
    }).json()
    response = client.get(f"/api/v1/sales/{sale['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == sale["id"]


def test_get_sale_not_found(client):
    response = client.get(f"/api/v1/sales/{uuid4()}")
    assert response.status_code == 404


# ── Edge Cases ────────────────────────────────────────────────────────────────

def test_record_sale_insufficient_stock(client):
    """Cannot sell more units than available."""
    product, inventory = make_full_setup(client, quantity=10)
    response = client.post("/api/v1/sales/", json={
        "product_id": product["id"],
        "inventory_id": inventory["id"],
        "quantity_sold": 999,
        "price_at_sale": 1000
    })
    assert response.status_code == 409


def test_record_sale_zero_quantity(client):
    """Cannot sell 0 units."""
    product, inventory = make_full_setup(client)
    response = client.post("/api/v1/sales/", json={
        "product_id": product["id"],
        "inventory_id": inventory["id"],
        "quantity_sold": 0,
        "price_at_sale": 1000
    })
    assert response.status_code == 422


def test_record_sale_negative_quantity(client):
    """Cannot sell negative units."""
    product, inventory = make_full_setup(client)
    response = client.post("/api/v1/sales/", json={
        "product_id": product["id"],
        "inventory_id": inventory["id"],
        "quantity_sold": -5,
        "price_at_sale": 1000
    })
    assert response.status_code == 422


def test_record_sale_wrong_inventory_id(client):
    """inventory_id must match the product's actual inventory."""
    product1, inventory1 = make_full_setup(client, sku="SALE-001")
    product2, inventory2 = make_full_setup(client, sku="SALE-002")
    response = client.post("/api/v1/sales/", json={
        "product_id": product1["id"],
        "inventory_id": inventory2["id"],  # wrong inventory
        "quantity_sold": 1,
        "price_at_sale": 1000
    })
    assert response.status_code == 400


def test_record_sale_nonexistent_product(client):
    """Cannot record sale for nonexistent product."""
    response = client.post("/api/v1/sales/", json={
        "product_id": str(uuid4()),
        "inventory_id": str(uuid4()),
        "quantity_sold": 1,
        "price_at_sale": 1000
    })
    assert response.status_code == 404


def test_stock_cannot_go_negative(client):
    """
    Core business invariant — stock must never go below 0.
    Sell all available stock then try to sell one more.
    """
    product, inventory = make_full_setup(client, quantity=5)

    # Sell exactly what's available
    client.post("/api/v1/sales/", json={
        "product_id": product["id"],
        "inventory_id": inventory["id"],
        "quantity_sold": 5,
        "price_at_sale": 1000
    })

    # Try to sell one more
    response = client.post("/api/v1/sales/", json={
        "product_id": product["id"],
        "inventory_id": inventory["id"],
        "quantity_sold": 1,
        "price_at_sale": 1000
    })
    assert response.status_code == 409

    # Verify stock is at 0 not negative
    inv = client.get(f"/api/v1/inventory/{product['id']}").json()
    assert inv["quantity_on_hand"] == 0