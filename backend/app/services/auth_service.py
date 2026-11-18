import secrets
import uuid
from datetime import UTC, datetime, timedelta

import jwt
from fastapi import Response, status

from app.core.security import (
    REFRESH_DAYS,
    create_access_token,
    decode_access_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.repositories.token_repository import TokenRepository
from app.repositories.user_repository import UserRepository


async def issue_tokens(user: User, token_repo: TokenRepository) -> dict:

    raw = secrets.token_urlsafe(32)

    await token_repo.create(
        RefreshToken(
            user_id=user.id,
            token_hash=hash_token(raw),
            expires_at=datetime.now(UTC) + timedelta(days=REFRESH_DAYS),
        )
    )

    return {"access_token": create_access_token(user.id), "refresh_token": raw}


async def refresh_tokens(
    raw: str, token_repo: TokenRepository, user_repo: UserRepository
) -> dict:

    invalid = ValueError("Invalid refresh token")

    now = datetime.now(UTC)

    token = await token_repo.get_by_hash(hash_token(raw))

    if token is None or token.expires_at < now:
        raise invalid

    if token.revoked_at is not None:
        await token_repo.revoke_all(token.user_id)
        raise invalid

    user = await user_repo.get_by_id(token.user_id)

    if user is None or not user.is_active:
        raise invalid

    token.revoked_at = now
    await token_repo.update(token)

    return await issue_tokens(user, token_repo)


async def register(email: str, password: str, user_repo: UserRepository) -> User:

    existing_user = await user_repo.get_by_email(email)

    if existing_user is not None:
        raise ValueError("User already exists")

    user = await user_repo.create(
        User(email=email, hashed_password=hash_password(password))
    )

    return user


async def authenticate_user(
    email: str, password: str, user_repo: UserRepository
) -> User | None:

    user = await user_repo.get_by_email(email)
    if user is None or not user.is_active:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user


async def login_user(
    email: str, password: str, user_repo: UserRepository, token_repo: TokenRepository
) -> dict:

    user = await authenticate_user(email, password, user_repo)

    if user is None:
        raise ValueError("Invalid credentials")

    return await issue_tokens(user, token_repo)


async def logout_user(raw: str, token_repo: TokenRepository) -> None:

    token = await token_repo.get_by_hash(hash_token(raw))

    if token is not None and token.revoked_at is None:
        token.revoked_at = datetime.now(UTC)
        await token_repo.update(token)

        return Response(status_code=status.HTTP_204_NO_CONTENT)


async def get_current_user(token: str, user_repo: UserRepository) -> User:
    try:
        user_id = decode_access_token(token)

    except jwt.InvalidTokenError:
        raise ValueError("Invalid access token")

    user = await user_repo.get_by_id(user_id)

    if user is None or not user.is_active:
        raise ValueError("Invalid access token")

    return user


async def logout_from_all_devices(
    user_id: uuid.UUID, token_repo: TokenRepository
) -> None:

    await token_repo.revoke_all(user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
