import uuid
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.refresh_token import RefreshToken
from app.models.user import User


async def test_create_token(user_repo, token_repo):
    user = await user_repo.create(
        User(email="alice@example.com", hashed_password="hashed_secret")
    )
    expires_at = datetime.now(UTC) + timedelta(days=7)

    token = RefreshToken(user_id=user.id, token_hash="hash_123", expires_at=expires_at)
    created_token = await token_repo.create(token)

    assert isinstance(created_token.id, uuid.UUID)
    assert created_token.user_id == user.id
    assert created_token.token_hash == "hash_123"
    assert created_token.revoked_at is None


async def test_create_token_invalid_user_raises_error(token_repo):
    token = RefreshToken(
        user_id=uuid.uuid4(),
        token_hash="hash_invalid",
        expires_at=datetime.now(UTC) + timedelta(days=7),
    )

    with pytest.raises(IntegrityError):
        await token_repo.create(token)


async def test_get_by_user(user_repo, token_repo):
    user = await user_repo.create(
        User(email="bob@example.com", hashed_password="hashed_secret")
    )
    token = await token_repo.create(
        RefreshToken(
            user_id=user.id,
            token_hash="hash_bob",
            expires_at=datetime.now(UTC) + timedelta(days=7),
        )
    )

    found_token = await token_repo.get_by_user(user.id)

    assert found_token is not None
    assert found_token.id == token.id


async def test_get_by_user_not_found(token_repo):
    assert await token_repo.get_by_user(uuid.uuid4()) is None


async def test_update_token(user_repo, token_repo):
    user = await user_repo.create(
        User(email="charlie@example.com", hashed_password="hashed_secret")
    )
    token = await token_repo.create(
        RefreshToken(
            user_id=user.id,
            token_hash="hash_charlie",
            expires_at=datetime.now(UTC) + timedelta(days=7),
        )
    )

    revoked_time = datetime.now(UTC)
    token.revoked_at = revoked_time
    updated_token = await token_repo.update(token)

    assert updated_token.revoked_at == revoked_time


async def test_delete_token(user_repo, token_repo):
    user = await user_repo.create(
        User(email="dave@example.com", hashed_password="hashed_secret")
    )
    token = await token_repo.create(
        RefreshToken(
            user_id=user.id,
            token_hash="hash_dave",
            expires_at=datetime.now(UTC) + timedelta(days=7),
        )
    )

    await token_repo.delete(token)

    assert await token_repo.get_by_user(user.id) is None


async def test_delete_user_cascades_to_tokens(user_repo, token_repo):
    user = await user_repo.create(
        User(email="eve@example.com", hashed_password="hashed_secret")
    )
    await token_repo.create(
        RefreshToken(
            user_id=user.id,
            token_hash="hash_eve",
            expires_at=datetime.now(UTC) + timedelta(days=7),
        )
    )

    await user_repo.delete(user)

    assert await token_repo.get_by_user(user.id) is None


async def test_get_by_hash(user_repo, token_repo):

    user = await user_repo.create(
        User(email="eve@example.com", hashed_password="hashed_secret")
    )

    await token_repo.create(
        RefreshToken(
            user_id=user.id,
            token_hash="hash_eve",
            expires_at=datetime.now(UTC) + timedelta(days=7),
        )
    )

    token = await token_repo.get_by_hash(token_hash="hash_eve")

    assert token is not None
    assert token.user_id == user.id


async def test_revoke_all(user_repo, token_repo):

    user = await user_repo.create(
        User(email="eve@example.com", hashed_password="hashed_secret")
    )

    await token_repo.create(
        RefreshToken(
            user_id=user.id,
            token_hash="hash_eve",
            expires_at=datetime.now(UTC) + timedelta(days=7),
        )
    )

    await token_repo.revoke_all(user.id)

    token = await token_repo.get_by_hash(token_hash="hash_eve")

    assert token is not None
    assert token.user_id == user.id
    assert token.revoked_at is not None
