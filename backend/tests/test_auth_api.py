async def test_register(client):

    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "test_user@example.com", "password": "password123"},
    )

    assert response.status_code == 201

    assert response.json()["email"] == "test_user@example.com"
    assert response.json()["is_active"]


async def test_login(client):

    register_response = await client.post(
        "/api/v1/auth/register",
        json={"email": "test_user@example.com", "password": "password123"},
    )

    assert register_response.status_code == 201

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "test_user@example.com", "password": "password123"},
    )

    assert login_response.status_code == 200

    assert isinstance(login_response.json()["access_token"], str) is True
    assert isinstance(login_response.json()["refresh_token"], str) is True


async def test_refresh(client):

    register_response = await client.post(
        "/api/v1/auth/register",
        json={"email": "test_user@example.com", "password": "password123"},
    )

    assert register_response.status_code == 201

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "test_user@example.com", "password": "password123"},
    )

    assert login_response.status_code == 200

    login_response.json()["access_token"]
    refresh_token = login_response.json()["refresh_token"]

    refresh_response = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
    )

    assert refresh_response.status_code == 200

    refresh_response.json()["access_token"]
    new_refresh_token = refresh_response.json()["refresh_token"]

    assert new_refresh_token != refresh_token


async def test_logout(client):

    register_response = await client.post(
        "/api/v1/auth/register",
        json={"email": "test_user@example.com", "password": "password123"},
    )

    assert register_response.status_code == 201

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "test_user@example.com", "password": "password123"},
    )

    assert login_response.status_code == 200

    login_response.json()["access_token"]
    refresh_token = login_response.json()["refresh_token"]

    logout_response = await client.post(
        "/api/v1/auth/logout", json={"refresh_token": refresh_token}
    )

    assert logout_response.status_code == 204

    refresh_attempt = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
    )

    assert refresh_attempt.status_code == 401


async def test_get_me(client):

    register_response = await client.post(
        "/api/v1/auth/register",
        json={"email": "test_user@example.com", "password": "password123"},
    )

    assert register_response.status_code == 201

    user_id = register_response.json()["id"]

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "test_user@example.com", "password": "password123"},
    )

    assert login_response.status_code == 200

    access_token = login_response.json()["access_token"]

    get_response = await client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {access_token}"}
    )

    assert get_response.status_code == 200
    assert get_response.json()["id"] == user_id
