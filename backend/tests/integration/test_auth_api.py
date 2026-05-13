def make_user_payload():
    return {
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "testpassword123"
    }


def test_register(client):
    response = client.post("/api/v1/auth/register", json=make_user_payload())
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"
    assert "id" in data
    assert "hashed_password" not in data  # never expose password


def test_register_duplicate_email(client):
    client.post("/api/v1/auth/register", json=make_user_payload())
    response = client.post("/api/v1/auth/register", json=make_user_payload())
    assert response.status_code == 409


def test_register_invalid_email(client):
    payload = make_user_payload()
    payload["email"] = "notanemail"
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422


def test_login(client):
    client.post("/api/v1/auth/register", json=make_user_payload())
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    client.post("/api/v1/auth/register", json=make_user_payload())
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401


def test_login_user_not_found(client):
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "nonexistent@example.com",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 401


def test_login_returns_valid_token(client):
    """
    Verifies the returned JWT token is actually valid
    by using it to access a protected endpoint.
    Once we add protected routes this test will be more meaningful.
    For now verify the token is a non-empty string.
    """
    client.post("/api/v1/auth/register", json=make_user_payload())
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpassword123"
        }
    )
    token = response.json()["access_token"]
    assert isinstance(token, str)
    assert len(token) > 0

def test_register_empty_password(client):
    """Password cannot be empty."""
    response = client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "full_name": "Test User",
        "password": ""
    })
    assert response.status_code == 422


def test_register_invalid_email_format(client):
    """Email must be valid format."""
    response = client.post("/api/v1/auth/register", json={
        "email": "notanemail",
        "full_name": "Test User",
        "password": "testpassword123"
    })
    assert response.status_code == 422


def test_login_empty_credentials(client):
    """Cannot login with empty credentials."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "", "password": ""}
    )
    assert response.status_code == 422