import uuid
from datetime import date, timedelta

import pytest

from app.models.user import User


async def test_create_trip(user_repo, trip_service):
    user = await user_repo.create(
        User(email="alice@example.com", hashed_password="hashed_secret")
    )
    start = date(2026, 12, 1)
    end = start + timedelta(days=5)

    trip = await trip_service.create_trip(
        user_id=user.id,
        title="Almaty Trip",
        start_date=start,
        end_date=end,
        primary_currency="KZT",
        description="Winter vacation",
    )

    assert trip.id is not None
    assert trip.user_id == user.id
    assert trip.title == "Almaty Trip"
    assert trip.primary_currency == "KZT"
    assert trip.description == "Winter vacation"


async def test_create_trip_user_not_found(trip_service):
    with pytest.raises(ValueError, match="User not found"):
        await trip_service.create_trip(
            user_id=uuid.uuid4(),
            title="Ghost Trip",
            start_date=date(2026, 12, 1),
            end_date=date(2026, 12, 5),
        )


async def test_create_trip_invalid_dates(user_repo, trip_service):
    user = await user_repo.create(
        User(email="dates_err@example.com", hashed_password="hashed_secret")
    )
    with pytest.raises(ValueError, match="start_date cannot be after end_date"):
        await trip_service.create_trip(
            user_id=user.id,
            title="Invalid Dates Trip",
            start_date=date(2026, 12, 10),
            end_date=date(2026, 12, 5),
        )


async def test_get_by_id(user_repo, trip_service):
    user = await user_repo.create(
        User(email="bob@example.com", hashed_password="hashed_secret")
    )
    created = await trip_service.create_trip(
        user_id=user.id,
        title="Astana Trip",
        start_date=date(2026, 12, 1),
        end_date=date(2026, 12, 3),
    )

    found = await trip_service.get_by_id(user_id=user.id, trip_id=created.id)

    assert found is not None
    assert found.id == created.id


async def test_get_by_id_user_not_found(trip_service):
    with pytest.raises(ValueError, match="User not found"):
        await trip_service.get_by_id(user_id=uuid.uuid4(), trip_id=uuid.uuid4())


async def test_get_by_id_not_found(user_repo, trip_service):
    user = await user_repo.create(
        User(email="bob2@example.com", hashed_password="hashed_secret")
    )

    with pytest.raises(ValueError, match="Trip not found"):
        await trip_service.get_by_id(user_id=user.id, trip_id=uuid.uuid4())


async def test_get_by_id_forbidden_for_other_user(user_repo, trip_service):
    owner = await user_repo.create(
        User(email="owner@example.com", hashed_password="hashed_secret")
    )
    other = await user_repo.create(
        User(email="other@example.com", hashed_password="hashed_secret")
    )
    trip = await trip_service.create_trip(
        user_id=owner.id,
        title="Private Trip",
        start_date=date(2026, 12, 1),
        end_date=date(2026, 12, 3),
    )

    with pytest.raises(ValueError, match="Trip not found"):
        await trip_service.get_by_id(user_id=other.id, trip_id=trip.id)


async def test_list_by_user(user_repo, trip_service):
    user1 = await user_repo.create(
        User(email="u1@example.com", hashed_password="hashed_secret")
    )
    user2 = await user_repo.create(
        User(email="u2@example.com", hashed_password="hashed_secret")
    )

    await trip_service.create_trip(
        user_id=user1.id,
        title="Trip 1",
        start_date=date(2026, 12, 1),
        end_date=date(2026, 12, 2),
    )
    await trip_service.create_trip(
        user_id=user1.id,
        title="Trip 2",
        start_date=date(2026, 12, 5),
        end_date=date(2026, 12, 6),
    )
    await trip_service.create_trip(
        user_id=user2.id,
        title="Other Trip",
        start_date=date(2026, 12, 1),
        end_date=date(2026, 12, 2),
    )

    trips = await trip_service.list_by_user(user_id=user1.id)

    assert len(trips) == 2
    assert {t.title for t in trips} == {"Trip 1", "Trip 2"}


async def test_list_by_user_not_found(trip_service):
    with pytest.raises(ValueError, match="User not found"):
        await trip_service.list_by_user(user_id=uuid.uuid4())


async def test_update_trip(user_repo, trip_service):
    user = await user_repo.create(
        User(email="charlie@example.com", hashed_password="hashed_secret")
    )
    trip = await trip_service.create_trip(
        user_id=user.id,
        title="Old Title",
        start_date=date(2026, 12, 1),
        end_date=date(2026, 12, 3),
    )

    updated = await trip_service.update_trip(
        user_id=user.id,
        trip_id=trip.id,
        title="New Title",
        primary_currency="EUR",
    )

    assert updated.title == "New Title"
    assert updated.primary_currency == "EUR"


async def test_update_trip_invalid_dates(user_repo, trip_service):
    user = await user_repo.create(
        User(email="update_err@example.com", hashed_password="hashed_secret")
    )
    trip = await trip_service.create_trip(
        user_id=user.id,
        title="Valid Trip",
        start_date=date(2026, 12, 1),
        end_date=date(2026, 12, 10),
    )

    with pytest.raises(ValueError, match="start_date cannot be after end_date"):
        await trip_service.update_trip(
            user_id=user.id,
            trip_id=trip.id,
            start_date=date(2026, 12, 15),
        )


async def test_update_trip_no_fields_raises_error(user_repo, trip_service):
    user = await user_repo.create(
        User(email="charlie2@example.com", hashed_password="hashed_secret")
    )

    with pytest.raises(ValueError, match="At least one field is required"):
        await trip_service.update_trip(user_id=user.id, trip_id=uuid.uuid4())


async def test_update_trip_user_not_found(trip_service):
    with pytest.raises(ValueError, match="User not found"):
        await trip_service.update_trip(
            user_id=uuid.uuid4(), trip_id=uuid.uuid4(), title="Updated"
        )


async def test_update_trip_forbidden_for_other_user(user_repo, trip_service):
    owner = await user_repo.create(
        User(email="owner2@example.com", hashed_password="hashed_secret")
    )
    other = await user_repo.create(
        User(email="other2@example.com", hashed_password="hashed_secret")
    )
    trip = await trip_service.create_trip(
        user_id=owner.id,
        title="Owner Trip",
        start_date=date(2026, 12, 1),
        end_date=date(2026, 12, 3),
    )

    with pytest.raises(ValueError, match="Trip not found"):
        await trip_service.update_trip(
            user_id=other.id, trip_id=trip.id, title="Hacked"
        )


async def test_delete_trip(user_repo, trip_service):
    user = await user_repo.create(
        User(email="dave@example.com", hashed_password="hashed_secret")
    )
    trip = await trip_service.create_trip(
        user_id=user.id,
        title="To Delete",
        start_date=date(2026, 12, 1),
        end_date=date(2026, 12, 3),
    )

    await trip_service.delete_trip(user_id=user.id, trip_id=trip.id)

    with pytest.raises(ValueError, match="Trip not found"):
        await trip_service.get_by_id(user_id=user.id, trip_id=trip.id)


async def test_delete_trip_user_not_found(trip_service):
    with pytest.raises(ValueError, match="User not found"):
        await trip_service.delete_trip(user_id=uuid.uuid4(), trip_id=uuid.uuid4())


async def test_delete_trip_forbidden_for_other_user(user_repo, trip_service):
    owner = await user_repo.create(
        User(email="owner3@example.com", hashed_password="hashed_secret")
    )
    other = await user_repo.create(
        User(email="other3@example.com", hashed_password="hashed_secret")
    )
    trip = await trip_service.create_trip(
        user_id=owner.id,
        title="Protected Trip",
        start_date=date(2026, 12, 1),
        end_date=date(2026, 12, 3),
    )

    with pytest.raises(ValueError, match="Trip not found"):
        await trip_service.delete_trip(user_id=other.id, trip_id=trip.id)


async def test_list_all_trips_and_filters(user_repo, trip_service):
    user1 = await user_repo.create(
        User(email="list1@example.com", hashed_password="hashed_secret")
    )
    user2 = await user_repo.create(
        User(email="list2@example.com", hashed_password="hashed_secret")
    )

    await trip_service.create_trip(
        user_id=user1.id,
        title="Almaty Weekend",
        description="Mountain hike",
        start_date=date(2026, 6, 1),
        end_date=date(2026, 6, 3),
        primary_currency="KZT",
    )
    await trip_service.create_trip(
        user_id=user1.id,
        title="Rome Vacation",
        description="Museum tour",
        start_date=date(2026, 9, 10),
        end_date=date(2026, 9, 20),
        primary_currency="EUR",
    )
    await trip_service.create_trip(
        user_id=user2.id,
        title="Almaty Weekend",
        description="Other user trip",
        start_date=date(2026, 6, 1),
        end_date=date(2026, 6, 3),
        primary_currency="KZT",
    )

    all_trips = await trip_service.list_all(user_id=user1.id)
    assert all_trips["total_items"] == 2
    assert len(all_trips["items"]) == 2

    filtered = await trip_service.list_all(
        user_id=user1.id,
        title="almaty",
        primary_currency="KZT",
        date_from=date(2026, 5, 1),
        date_to=date(2026, 7, 1),
    )
    assert filtered["total_items"] == 1
    assert filtered["items"][0].title == "Almaty Weekend"


async def test_list_all_pagination(user_repo, trip_service):
    user = await user_repo.create(
        User(email="listpage@example.com", hashed_password="hashed_secret")
    )

    for i in range(3):
        await trip_service.create_trip(
            user_id=user.id,
            title=f"Trip {i}",
            start_date=date(2026, 8, i + 1),
            end_date=date(2026, 8, i + 2),
        )

    result = await trip_service.list_all(user_id=user.id, page=2, per_page=2)

    assert len(result["items"]) == 1
    assert result["total_items"] == 3
    assert result["total_pages"] == 2
    assert result["current_page"] == 2
    assert result["per_page"] == 2


async def test_list_all_user_not_found(trip_service):
    with pytest.raises(ValueError, match="User not found"):
        await trip_service.list_all(user_id=uuid.uuid4())


async def test_list_all_invalid_pagination_raises_error(trip_service):
    with pytest.raises(
        ValueError, match="Page and per_page must be greater than or equal to 1"
    ):
        await trip_service.list_all(user_id=uuid.uuid4(), page=0, per_page=10)
