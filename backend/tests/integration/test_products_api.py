
def make_product_payload():
    return {
        "sku": "TEST-001",
        "name": "Test Product",
        "description": "A test product",
        "category": "electronics",
        "price_cents": 999,
        "currency": "USD"
    }


def test_create_product(client):
    response = client.post("/api/v1/products/", json=make_product_payload())
    assert response.status_code == 201
    data = response.json()
    assert data["sku"] == "TEST-001"
    assert data["name"] == "Test Product"
    assert "id" in data


def test_create_product_duplicate_sku(client):
    client.post("/api/v1/products/", json=make_product_payload())
    response = client.post("/api/v1/products/", json=make_product_payload())
    assert response.status_code == 409


def test_get_products(client):
    client.post("/api/v1/products/", json=make_product_payload())
    response = client.get("/api/v1/products/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1


def test_get_product_by_id(client):
    created = client.post("/api/v1/products/", json=make_product_payload()).json()
    response = client.get(f"/api/v1/products/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_get_product_not_found(client):
    from uuid import uuid4
    response = client.get(f"/api/v1/products/{uuid4()}")
    assert response.status_code == 404


def test_update_product(client):
    created = client.post("/api/v1/products/", json=make_product_payload()).json()
    response = client.put(
        f"/api/v1/products/{created['id']}",
        json={"name": "Updated Name"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"
    assert response.json()["sku"] == "TEST-001"  # unchanged


def test_delete_product(client):
    created = client.post("/api/v1/products/", json=make_product_payload()).json()
    response = client.delete(f"/api/v1/products/{created['id']}")
    assert response.status_code == 204

    # Verify it's gone
    response = client.get(f"/api/v1/products/{created['id']}")
    assert response.status_code == 404

def test_create_product_negative_price(client):
    """Price must be greater than 0."""
    response = client.post("/api/v1/products/", json={
        "sku": "EDGE-001",
        "name": "Bad Product",
        "description": "Test",
        "category": "electronics",
        "price_cents": -1,
        "currency": "USD"
    })
    assert response.status_code == 422


def test_create_product_zero_price(client):
    """Price of 0 is not allowed."""
    response = client.post("/api/v1/products/", json={
        "sku": "EDGE-001",
        "name": "Bad Product",
        "description": "Test",
        "category": "electronics",
        "price_cents": 0,
        "currency": "USD"
    })
    assert response.status_code == 422


def test_create_product_sku_too_short(client):
    """SKU must be at least 3 characters."""
    response = client.post("/api/v1/products/", json={
        "sku": "AB",
        "name": "Bad Product",
        "description": "Test",
        "category": "electronics",
        "price_cents": 999,
        "currency": "USD"
    })
    assert response.status_code == 422


def test_create_product_invalid_category(client):
    """Category must be a valid enum value."""
    response = client.post("/api/v1/products/", json={
        "sku": "EDGE-001",
        "name": "Bad Product",
        "description": "Test",
        "category": "invalid_category",
        "price_cents": 999,
        "currency": "USD"
    })
    assert response.status_code == 422


def test_create_product_invalid_currency(client):
    """Currency must be a valid enum value."""
    response = client.post("/api/v1/products/", json={
        "sku": "EDGE-001",
        "name": "Bad Product",
        "description": "Test",
        "category": "electronics",
        "price_cents": 999,
        "currency": "INVALID"
    })
    assert response.status_code == 422
