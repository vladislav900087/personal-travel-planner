import uuid

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken


class TokenRepository:
    def __init__(self, db: AsyncSession):

        self.db = db

    async def create(self, token: RefreshToken) -> RefreshToken:
        self.db.add(token)
        await self.db.commit()
        await self.db.refresh(token)

        return token

    async def update(self, token: RefreshToken) -> RefreshToken:

        await self.db.commit()

        return token

    async def delete(self, token: RefreshToken) -> RefreshToken:

        await self.db.delete(token)
        await self.db.commit()

        return token

    async def get_by_user(self, user_id: int) -> RefreshToken:

        statement = select(RefreshToken).where(RefreshToken.user_id == user_id)

        return await self.db.scalar(statement)

    async def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        statement = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        return await self.db.scalar(statement)

    async def revoke_all(self, user_id: uuid.UUID) -> None:

        statement = (
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
            .values(revoked_at=func.now())
        )

        await self.db.execute(statement)
        await self.db.commit()
