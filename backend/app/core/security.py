import hashlib
import uuid
from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash

from app.core.config import settings

ACCESS_MINUTES = settings.access_token_expire_minutes
REFRESH_DAYS = settings.refresh_token_expire_days

password_hash = PasswordHash.recommended()


def create_access_token(user_id: uuid.UUID) -> str:
    exp = datetime.now(UTC) + timedelta(minutes=ACCESS_MINUTES)

    return jwt.encode(
        {"sub": str(user_id), "exp": exp}, settings.secret_key, algorithm="HS256"
    )


def decode_access_token(token: str) -> uuid.UUID:

    payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])

    return uuid.UUID(payload["sub"])


def hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)
