async def auth_headers(client, email: str = "traveler@example.com") -> dict[str, str]:
    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "password123"},
    )
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "password123"},
    )
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def test_create_trip(client):
    headers = await auth_headers(client)

    payload = {
        "title": "Summer in Italy",
        "description": "Rome and Florence trip",
        "start_date": "2026-07-01",
        "end_date": "2026-07-15",
        "primary_currency": "EUR",
    }
    response = await client.post("/api/v1/trips", json=payload, headers=headers)

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Summer in Italy"
    assert data["primary_currency"] == "EUR"
    assert data["description"] == "Rome and Florence trip"
    assert data["start_date"] == "2026-07-01"
    assert data["end_date"] == "2026-07-15"
    assert "id" in data


async def test_create_trip_invalid_dates(client):
    headers = await auth_headers(client)

    payload = {
        "title": "Invalid Trip",
        "start_date": "2026-07-20",
        "end_date": "2026-07-10",
    }
    response = await client.post("/api/v1/trips", json=payload, headers=headers)

    assert response.status_code == 400
    assert "start_date cannot be after end_date" in response.json()["detail"]


async def test_create_trip_unauthenticated(client):
    payload = {
        "title": "Unauthenticated Trip",
        "start_date": "2026-08-01",
        "end_date": "2026-08-05",
    }
    response = await client.post("/api/v1/trips", json=payload)

    assert response.status_code == 401 or response.status_code == 403


async def test_get_trip_by_id(client):
    headers = await auth_headers(client)

    create_resp = await client.post(
        "/api/v1/trips",
        json={
            "title": "Almaty Trip",
            "start_date": "2026-09-01",
            "end_date": "2026-09-05",
        },
        headers=headers,
    )
    trip_id = create_resp.json()["id"]

    response = await client.get(f"/api/v1/trips/{trip_id}", headers=headers)

    assert response.status_code == 200
    assert response.json()["id"] == trip_id
    assert response.json()["title"] == "Almaty Trip"


async def test_get_trip_not_found(client):
    headers = await auth_headers(client)
    random_id = "00000000-0000-0000-0000-000000000000"

    response = await client.get(f"/api/v1/trips/{random_id}", headers=headers)

    assert response.status_code == 404


async def test_get_trip_forbidden_for_other_user(client):
    user1_headers = await auth_headers(client, email="user1@example.com")
    user2_headers = await auth_headers(client, email="user2@example.com")

    created = await client.post(
        "/api/v1/trips",
        json={
            "title": "Private Trip",
            "start_date": "2026-10-01",
            "end_date": "2026-10-05",
        },
        headers=user1_headers,
    )
    trip_id = created.json()["id"]

    # Other user must receive 404 to avoid leaking existence of private trips
    response = await client.get(f"/api/v1/trips/{trip_id}", headers=user2_headers)
    assert response.status_code == 404


async def test_list_trips_pagination_and_isolation(client):
    user1_headers = await auth_headers(client, email="owner1@example.com")
    user2_headers = await auth_headers(client, email="owner2@example.com")

    for i in range(3):
        await client.post(
            "/api/v1/trips",
            json={
                "title": f"Trip {i}",
                "start_date": f"2026-0{i + 1}-01",
                "end_date": f"2026-0{i + 1}-10",
            },
            headers=user1_headers,
        )

    await client.post(
        "/api/v1/trips",
        json={
            "title": "Other User Trip",
            "start_date": "2026-05-01",
            "end_date": "2026-05-10",
        },
        headers=user2_headers,
    )

    response = await client.get(
        "/api/v1/trips?page=1&per_page=2",
        headers=user1_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_items"] == 3
    assert len(data["items"]) == 2
    assert data["total_pages"] == 2


async def test_list_trips_filters(client):
    headers = await auth_headers(client)

    await client.post(
        "/api/v1/trips",
        json={
            "title": "Japan Cherry Blossom",
            "start_date": "2026-04-01",
            "end_date": "2026-04-10",
            "primary_currency": "JPY",
        },
        headers=headers,
    )
    await client.post(
        "/api/v1/trips",
        json={
            "title": "Paris Weekend",
            "start_date": "2026-05-01",
            "end_date": "2026-05-05",
            "primary_currency": "EUR",
        },
        headers=headers,
    )

    response = await client.get(
        "/api/v1/trips?primary_currency=JPY",
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_items"] == 1
    assert data["items"][0]["title"] == "Japan Cherry Blossom"


async def test_update_trip(client):
    headers = await auth_headers(client)

    create_resp = await client.post(
        "/api/v1/trips",
        json={
            "title": "Original Title",
            "start_date": "2026-06-01",
            "end_date": "2026-06-10",
            "primary_currency": "USD",
        },
        headers=headers,
    )
    trip_id = create_resp.json()["id"]

    patch_resp = await client.patch(
        f"/api/v1/trips/{trip_id}",
        json={"title": "Updated Title", "primary_currency": "KZT"},
        headers=headers,
    )

    assert patch_resp.status_code == 200
    data = patch_resp.json()
    assert data["title"] == "Updated Title"
    assert data["primary_currency"] == "KZT"


async def test_update_trip_invalid_dates(client):
    headers = await auth_headers(client)

    create_resp = await client.post(
        "/api/v1/trips",
        json={
            "title": "Test Trip",
            "start_date": "2026-06-10",
            "end_date": "2026-06-20",
        },
        headers=headers,
    )
    trip_id = create_resp.json()["id"]

    patch_resp = await client.patch(
        f"/api/v1/trips/{trip_id}",
        json={"start_date": "2026-06-25"},
        headers=headers,
    )
    assert patch_resp.status_code == 400
    assert "start_date cannot be after end_date" in patch_resp.json()["detail"]


async def test_update_trip_empty_body_raises_error(client):
    headers = await auth_headers(client)

    create_resp = await client.post(
        "/api/v1/trips",
        json={
            "title": "Test Trip",
            "start_date": "2026-06-10",
            "end_date": "2026-06-20",
        },
        headers=headers,
    )
    trip_id = create_resp.json()["id"]

    patch_resp = await client.patch(
        f"/api/v1/trips/{trip_id}",
        json={},
        headers=headers,
    )
    assert patch_resp.status_code == 400


async def test_update_trip_other_user_forbidden(client):
    user1_headers = await auth_headers(client, email="owner_u@example.com")
    user2_headers = await auth_headers(client, email="hacker_u@example.com")

    created = await client.post(
        "/api/v1/trips",
        json={
            "title": "Protected Trip",
            "start_date": "2026-06-10",
            "end_date": "2026-06-20",
        },
        headers=user1_headers,
    )
    trip_id = created.json()["id"]

    patch_resp = await client.patch(
        f"/api/v1/trips/{trip_id}",
        json={"title": "Hacked Title"},
        headers=user2_headers,
    )
    assert patch_resp.status_code == 404


async def test_delete_trip(client):
    headers = await auth_headers(client)

    create_resp = await client.post(
        "/api/v1/trips",
        json={
            "title": "Trip to Delete",
            "start_date": "2026-07-01",
            "end_date": "2026-07-05",
        },
        headers=headers,
    )
    trip_id = create_resp.json()["id"]

    del_resp = await client.delete(f"/api/v1/trips/{trip_id}", headers=headers)
    assert del_resp.status_code == 204

    get_resp = await client.get(f"/api/v1/trips/{trip_id}", headers=headers)
    assert get_resp.status_code == 404


async def test_delete_trip_other_user_forbidden(client):
    user1_headers = await auth_headers(client, email="del_owner@example.com")
    user2_headers = await auth_headers(client, email="del_other@example.com")

    created = await client.post(
        "/api/v1/trips",
        json={
            "title": "Trip Protected From Deletion",
            "start_date": "2026-07-01",
            "end_date": "2026-07-05",
        },
        headers=user1_headers,
    )
    trip_id = created.json()["id"]

    del_resp = await client.delete(f"/api/v1/trips/{trip_id}", headers=user2_headers)
    assert del_resp.status_code == 404

    get_resp = await client.get(f"/api/v1/trips/{trip_id}", headers=user1_headers)
    assert get_resp.status_code == 200
