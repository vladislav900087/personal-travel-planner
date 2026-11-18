import uuid
from datetime import UTC, date, datetime, timedelta

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.trip import Trip
from app.models.user import User


def make_trip(user_id: uuid.UUID, title: str = "Almaty Weekend") -> Trip:
    now = datetime.now(UTC)
    return Trip(
        user_id=user_id,
        title=title,
        description="Short mountain getaway",
        start_date=now,
        end_date=now + timedelta(days=3),
    )


async def test_create_trip(user_repo, trip_repo):
    user = await user_repo.create(
        User(email="alice@example.com", hashed_password="hashed_secret")
    )

    created_trip = await trip_repo.create(make_trip(user.id))

    assert isinstance(created_trip.id, uuid.UUID)
    assert created_trip.user_id == user.id
    assert created_trip.title == "Almaty Weekend"
    assert created_trip.primary_currency == "USD"
    assert created_trip.created_at is not None


async def test_create_trip_invalid_user_raises_error(trip_repo):
    with pytest.raises(IntegrityError):
        await trip_repo.create(make_trip(uuid.uuid4()))


async def test_get_by_id(user_repo, trip_repo):
    user = await user_repo.create(
        User(email="bob@example.com", hashed_password="hashed_secret")
    )
    trip = await trip_repo.create(make_trip(user.id))

    found_trip = await trip_repo.get_by_id(trip.id)

    assert found_trip is not None
    assert found_trip.id == trip.id


async def test_get_by_id_not_found(trip_repo):
    assert await trip_repo.get_by_id(uuid.uuid4()) is None


async def test_list_by_user(user_repo, trip_repo):
    user1 = await user_repo.create(
        User(email="user1@example.com", hashed_password="hashed_secret")
    )
    user2 = await user_repo.create(
        User(email="user2@example.com", hashed_password="hashed_secret")
    )

    await trip_repo.create(make_trip(user1.id, title="Trip 1"))
    await trip_repo.create(make_trip(user1.id, title="Trip 2"))
    await trip_repo.create(make_trip(user2.id, title="Other User Trip"))

    user1_trips = await trip_repo.list_by_user(user1.id)

    assert len(user1_trips) == 2
    assert {t.title for t in user1_trips} == {"Trip 1", "Trip 2"}


async def test_list_by_user_empty(trip_repo):
    assert await trip_repo.list_by_user(uuid.uuid4()) == []


async def test_update_trip(user_repo, trip_repo):
    user = await user_repo.create(
        User(email="charlie@example.com", hashed_password="hashed_secret")
    )
    trip = await trip_repo.create(make_trip(user.id))

    trip.title = "Astana Business Trip"
    trip.primary_currency = "KZT"
    updated_trip = await trip_repo.update(trip)

    assert updated_trip.title == "Astana Business Trip"
    assert updated_trip.primary_currency == "KZT"


async def test_delete_trip(user_repo, trip_repo):
    user = await user_repo.create(
        User(email="dave@example.com", hashed_password="hashed_secret")
    )
    trip = await trip_repo.create(make_trip(user.id))

    await trip_repo.delete(trip)

    assert await trip_repo.get_by_id(trip.id) is None


async def test_delete_user_cascades_to_trips(user_repo, trip_repo):
    user = await user_repo.create(
        User(email="eve@example.com", hashed_password="hashed_secret")
    )
    await trip_repo.create(make_trip(user.id))

    await user_repo.delete(user)

    assert await trip_repo.list_by_user(user.id) == []


async def test_list_all_filters_by_user_and_fields(user_repo, trip_repo):
    user1 = await user_repo.create(
        User(email="u1@example.com", hashed_password="hashed_secret")
    )
    user2 = await user_repo.create(
        User(email="u2@example.com", hashed_password="hashed_secret")
    )

    await trip_repo.create(
        Trip(
            user_id=user1.id,
            title="Almaty Mountains",
            description="Hiking trip",
            start_date=date(2026, 6, 1),
            end_date=date(2026, 6, 5),
            primary_currency="KZT",
        )
    )
    await trip_repo.create(
        Trip(
            user_id=user1.id,
            title="Rome Holiday",
            description="Sightseeing",
            start_date=date(2026, 9, 10),
            end_date=date(2026, 9, 20),
            primary_currency="EUR",
        )
    )
    await trip_repo.create(
        Trip(
            user_id=user2.id,
            title="Almaty Mountains",
            description="Other user trip",
            start_date=date(2026, 6, 1),
            end_date=date(2026, 6, 5),
            primary_currency="KZT",
        )
    )

    by_title = await trip_repo.list_all(user_id=user1.id, title="almaty")
    assert by_title["total_items"] == 1
    assert len(by_title["items"]) == 1
    assert by_title["items"][0].title == "Almaty Mountains"

    by_currency = await trip_repo.list_all(user_id=user1.id, primary_currency="EUR")
    assert by_currency["total_items"] == 1
    assert by_currency["items"][0].title == "Rome Holiday"


async def test_list_all_date_range_and_exact_dates(user_repo, trip_repo):
    user = await user_repo.create(
        User(email="dates@example.com", hashed_password="hashed_secret")
    )

    await trip_repo.create(
        Trip(
            user_id=user.id,
            title="Spring Trip",
            start_date=date(2026, 4, 1),
            end_date=date(2026, 4, 10),
        )
    )
    await trip_repo.create(
        Trip(
            user_id=user.id,
            title="Summer Trip",
            start_date=date(2026, 7, 1),
            end_date=date(2026, 7, 15),
        )
    )

    exact = await trip_repo.list_all(
        user_id=user.id,
        start_date=date(2026, 4, 1),
        end_date=date(2026, 4, 10),
    )

    assert exact["total_items"] == 1
    assert [t.title for t in exact["items"]] == ["Spring Trip"]

    ranged = await trip_repo.list_all(
        user_id=user.id,
        date_from=date(2026, 6, 1),
        date_to=date(2026, 8, 1),
    )
    assert ranged["total_items"] == 1
    assert [t.title for t in ranged["items"]] == ["Summer Trip"]


async def test_list_all_pagination(user_repo, trip_repo):
    user = await user_repo.create(
        User(email="page@example.com", hashed_password="hashed_secret")
    )

    for i in range(5):
        await trip_repo.create(
            Trip(
                user_id=user.id,
                title=f"Trip {i}",
                start_date=date(2026, 5, i + 1),
                end_date=date(2026, 5, i + 2),
            )
        )

    page_2 = await trip_repo.list_all(user_id=user.id, page=2, per_page=2)

    assert len(page_2["items"]) == 2
    assert page_2["total_items"] == 5
    assert page_2["total_pages"] == 3
    assert page_2["current_page"] == 2
    assert page_2["per_page"] == 2


async def test_list_all_empty(user_repo, trip_repo):
    user = await user_repo.create(
        User(email="empty@example.com", hashed_password="hashed_secret")
    )

    result = await trip_repo.list_all(user_id=user.id)

    assert result == {
        "items": [],
        "total_items": 0,
        "total_pages": 1,
        "current_page": 1,
        "per_page": 20,
    }
