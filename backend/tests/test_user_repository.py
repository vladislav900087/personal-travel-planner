import uuid

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.user import User


async def test_create_user(user_repo):
    user = User(email="alice@example.com", hashed_password="hashed_secret")

    created_user = await user_repo.create(user)

    assert isinstance(created_user.id, uuid.UUID)
    assert created_user.email == "alice@example.com"
    assert created_user.is_active is True
    assert created_user.created_at is not None


async def test_create_duplicate_email_raises_error(user_repo):
    await user_repo.create(
        User(email="dup@example.com", hashed_password="hashed_secret")
    )

    with pytest.raises(IntegrityError):
        await user_repo.create(
            User(email="dup@example.com", hashed_password="hashed_secret")
        )


async def test_get_by_id(user_repo):
    user = await user_repo.create(
        User(email="bob@example.com", hashed_password="hashed_secret")
    )

    found_user = await user_repo.get_by_id(user.id)

    assert found_user is not None
    assert found_user.id == user.id


async def test_get_by_id_not_found(user_repo):
    assert await user_repo.get_by_id(uuid.uuid4()) is None


async def test_get_by_email(user_repo):
    await user_repo.create(
        User(email="charlie@example.com", hashed_password="hashed_secret")
    )

    found_user = await user_repo.get_by_email("charlie@example.com")

    assert found_user is not None
    assert found_user.email == "charlie@example.com"


async def test_get_by_email_not_found(user_repo):
    assert await user_repo.get_by_email("missing@example.com") is None


async def test_update_user(user_repo):
    user = await user_repo.create(
        User(email="old@example.com", hashed_password="hashed_secret")
    )

    user.email = "new@example.com"
    user.is_active = False
    updated_user = await user_repo.update(user)

    assert updated_user.email == "new@example.com"
    assert updated_user.is_active is False


async def test_delete_user(user_repo):
    user = await user_repo.create(
        User(email="dave@example.com", hashed_password="hashed_secret")
    )

    await user_repo.delete(user)

    assert await user_repo.get_by_id(user.id) is None
