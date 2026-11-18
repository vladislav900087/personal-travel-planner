async def test_register(client):
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "test_user@example.com", "password": "password123"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test_user@example.com"
    assert data["is_active"] is True


async def test_login(client):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "test_user@example.com", "password": "password123"},
    )

    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "test_user@example.com", "password": "password123"},
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["access_token"], str)
    assert isinstance(data["refresh_token"], str)


async def test_refresh(client):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "test_user@example.com", "password": "password123"},
    )
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "test_user@example.com", "password": "password123"},
    )
    refresh_token = login_response.json()["refresh_token"]

    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["access_token"], str)
    assert isinstance(data["refresh_token"], str)
    assert data["refresh_token"] != refresh_token


async def test_logout(client):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "test_user@example.com", "password": "password123"},
    )
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "test_user@example.com", "password": "password123"},
    )
    refresh_token = login_response.json()["refresh_token"]

    logout_response = await client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": refresh_token},
    )
    assert logout_response.status_code == 204

    # Using the same refresh token again should be rejected
    refresh_attempt = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_attempt.status_code == 401


async def test_get_me(client):
    reg_response = await client.post(
        "/api/v1/auth/register",
        json={"email": "test_user@example.com", "password": "password123"},
    )
    user_id = reg_response.json()["id"]

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "test_user@example.com", "password": "password123"},
    )
    access_token = login_response.json()["access_token"]

    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert response.json()["id"] == user_id
