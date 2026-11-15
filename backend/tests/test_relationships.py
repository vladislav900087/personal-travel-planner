from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken
from app.models.user import User


async def test_user_refresh_token_relationship(db_session: AsyncSession):
    # create a user
    user = User(
        email="test_rel@example.com",
        hashed_password="hashed_pw_test",
    )
    db_session.add(user)
    await db_session.flush()

    # create a refresh token linked to user
    token = RefreshToken(
        user_id=user.id,
        token_hash="sample_hash_123",
        expires_at=datetime.now(UTC) + timedelta(days=30),
    )
    db_session.add(token)
    await db_session.commit()

    # verify relationship from token to user
    query = select(RefreshToken).where(RefreshToken.id == token.id)
    result = await db_session.execute(query)
    saved_token = result.scalar_one()

    assert saved_token.user_id == user.id


async def test_cascade_delete_user_deletes_tokens(db_session: AsyncSession):
    # create user and token
    user = User(
        email="cascade_test@example.com",
        hashed_password="hashed_pw_test",
    )
    db_session.add(user)
    await db_session.flush()

    token = RefreshToken(
        user_id=user.id,
        token_hash="cascade_token_hash",
        expires_at=datetime.now(UTC) + timedelta(days=30),
    )
    db_session.add(token)
    await db_session.commit()

    # delete user
    await db_session.delete(user)
    await db_session.commit()

    # verify token was deleted by cascade
    query = select(RefreshToken).where(RefreshToken.user_id == user.id)
    result = await db_session.execute(query)
    assert result.scalar_one_or_none() is None
