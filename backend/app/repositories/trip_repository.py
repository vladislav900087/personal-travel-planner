import math
import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.trip import Trip


class TripRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, trip: Trip) -> Trip:
        self.db.add(trip)
        await self.db.commit()
        await self.db.refresh(trip)

        return trip

    async def update(self, trip: Trip) -> Trip:
        await self.db.commit()
        await self.db.refresh(trip)

        return trip

    async def delete(self, trip: Trip) -> None:

        await self.db.delete(trip)
        await self.db.commit()

    async def list_by_user(self, user_id: uuid.UUID) -> list[Trip]:

        statement = select(Trip).where(Trip.user_id == user_id)

        result = await self.db.scalars(statement)

        return list(result)

    async def get_by_id(self, trip_id: uuid.UUID) -> Trip | None:

        statement = select(Trip).where(Trip.id == trip_id)

        return await self.db.scalar(statement)

    async def list_all(
        self,
        user_id: uuid.UUID,
        title=None,
        description=None,
        start_date=None,
        end_date=None,
        date_from=None,
        date_to=None,
        primary_currency=None,
        page: int = 1,
        per_page: int = 20,
    ) -> dict[str, Any]:

        offset = (page - 1) * per_page

        statement = select(Trip).where(Trip.user_id == user_id)

        if title is not None:
            statement = statement.where(Trip.title.ilike(f"%{title}%"))

        if description is not None:
            statement = statement.where(Trip.description.ilike(f"%{description}%"))

        if start_date is not None:
            statement = statement.where(Trip.start_date == start_date)

        if end_date is not None:
            statement = statement.where(Trip.end_date == end_date)

        if date_from is not None:
            statement = statement.where(Trip.start_date >= date_from)

        if date_to is not None:
            statement = statement.where(Trip.end_date <= date_to)

        if primary_currency is not None:
            statement = statement.where(Trip.primary_currency == primary_currency)

        count_stmt = select(func.count()).select_from(statement.subquery())
        total_items = await self.db.scalar(count_stmt) or 0

        paginated_stmt = (
            statement.order_by(Trip.created_at.desc()).offset(offset).limit(per_page)
        )

        trips = await self.db.scalars(paginated_stmt)

        total_pages = math.ceil(total_items / per_page) if total_items > 0 else 1

        return {
            "items": list(trips),
            "total_items": total_items,
            "total_pages": total_pages,
            "current_page": page,
            "per_page": per_page,
        }
