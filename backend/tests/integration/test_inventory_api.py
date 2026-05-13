from uuid import uuid4

def make_product(client):
    response = client.post("/api/v1/products/", json={
        "sku": "TEST-001",
        "name": "Test Product",
        "description": "A test product",
        "category": "electronics",
        "price_cents": 999,
        "currency": "USD"
    })
    return response.json()


def make_inventory(client, product_id, quantity=100, reorder_level=10):
    response = client.post("/api/v1/inventory/", json={
        "product_id": product_id,
        "quantity_on_hand": quantity,
        "reorder_level": reorder_level
    })
    return response.json()


def test_create_inventory(client):
    product = make_product(client)
    response = client.post("/api/v1/inventory/", json={
        "product_id": product["id"],
        "quantity_on_hand": 100,
        "reorder_level": 10
    })
    assert response.status_code == 201
    data = response.json()
    assert data["quantity_on_hand"] == 100
    assert data["reorder_level"] == 10
    assert data["product_id"] == product["id"]


def test_create_inventory_product_not_found(client):
    from uuid import uuid4
    response = client.post("/api/v1/inventory/", json={
        "product_id": str(uuid4()),
        "quantity_on_hand": 100,
        "reorder_level": 10
    })
    assert response.status_code == 404


def test_create_inventory_duplicate(client):
    product = make_product(client)
    client.post("/api/v1/inventory/", json={
        "product_id": product["id"],
        "quantity_on_hand": 100,
        "reorder_level": 10
    })
    response = client.post("/api/v1/inventory/", json={
        "product_id": product["id"],
        "quantity_on_hand": 100,
        "reorder_level": 10
    })
    assert response.status_code == 409


def test_get_all_inventory(client):
    product = make_product(client)
    make_inventory(client, product["id"])
    response = client.get("/api/v1/inventory/")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_inventory_by_product(client):
    product = make_product(client)
    make_inventory(client, product["id"])
    response = client.get(f"/api/v1/inventory/{product['id']}")
    assert response.status_code == 200
    assert response.json()["product_id"] == product["id"]


def test_get_inventory_not_found(client):
    from uuid import uuid4
    response = client.get(f"/api/v1/inventory/{uuid4()}")
    assert response.status_code == 404


def test_update_inventory(client):
    product = make_product(client)
    make_inventory(client, product["id"])
    response = client.put(
        f"/api/v1/inventory/{product['id']}",
        json={"quantity_on_hand": 50}
    )
    assert response.status_code == 200
    assert response.json()["quantity_on_hand"] == 50
    assert response.json()["reorder_level"] == 10  # unchanged


def test_delete_inventory(client):
    product = make_product(client)
    make_inventory(client, product["id"])
    response = client.delete(f"/api/v1/inventory/{product['id']}")
    assert response.status_code == 204

    response = client.get(f"/api/v1/inventory/{product['id']}")
    assert response.status_code == 404

def test_create_inventory_negative_quantity(client):
    """Quantity on hand cannot be negative."""
    product = make_product(client)  # ← fix helper name
    response = client.post("/api/v1/inventory/", json={
        "product_id": product["id"],
        "quantity_on_hand": -1,
        "reorder_level": 10
    })
    assert response.status_code == 422


def test_create_inventory_negative_reorder_level(client):
    """Reorder level cannot be negative."""
    product = make_product(client)  # ← fix helper name
    response = client.post("/api/v1/inventory/", json={
        "product_id": product["id"],
        "quantity_on_hand": 100,
        "reorder_level": -1
    })
    assert response.status_code == 422


def test_create_inventory_nonexistent_product(client):
    """Cannot create inventory for a product that doesn't exist."""
    response = client.post("/api/v1/inventory/", json={
        "product_id": str(uuid4()),
        "quantity_on_hand": 100,
        "reorder_level": 10
    })
    assert response.status_code == 404
