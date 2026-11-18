import uuid
from datetime import date
from typing import Any

from app.models.trip import Trip
from app.repositories.trip_repository import TripRepository
from app.repositories.user_repository import UserRepository


class TripService:
    def __init__(self, repository: TripRepository, user_repository: UserRepository):

        self.repository = repository
        self.user_repository = user_repository

    async def create_trip(
        self,
        user_id: uuid.UUID,
        title: str,
        start_date: date,
        end_date: date,
        primary_currency: str = "USD",
        description: str | None = None,
    ):
        if start_date > end_date:
            raise ValueError("start_date cannot be after end_date")

        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise ValueError("User not found")

        return await self.repository.create(
            Trip(
                user_id=user_id,
                title=title,
                start_date=start_date,
                end_date=end_date,
                primary_currency=primary_currency,
                description=description,
            )
        )

    async def update_trip(
        self,
        user_id: uuid.UUID,
        trip_id: uuid.UUID,
        title: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        primary_currency: str | None = None,
        description: str | None = None,
    ):
        if all(
            arg is None
            for arg in (title, start_date, end_date, primary_currency, description)
        ):
            raise ValueError("At least one field is required")

        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise ValueError("User not found")

        trip = await self.repository.get_by_id(trip_id)
        if trip is None or trip.user_id != user_id:
            raise ValueError("Trip not found")

        new_start = start_date if start_date is not None else trip.start_date
        new_end = end_date if end_date is not None else trip.end_date
        if new_start > new_end:
            raise ValueError("start_date cannot be after end_date")

        if title is not None:
            trip.title = title
        if start_date is not None:
            trip.start_date = start_date
        if end_date is not None:
            trip.end_date = end_date

        if primary_currency is not None:
            trip.primary_currency = primary_currency

        if description is not None:
            trip.description = description

        return await self.repository.update(trip)

    async def delete_trip(self, user_id: uuid.UUID, trip_id: uuid.UUID):

        user = await self.user_repository.get_by_id(user_id)

        if user is None:
            raise ValueError("User not found")

        trip = await self.repository.get_by_id(trip_id)

        if trip is None or trip.user_id != user_id:
            raise ValueError("Trip not found")

        return await self.repository.delete(trip)

    async def get_by_id(self, user_id: uuid.UUID, trip_id: uuid.UUID) -> Trip | None:

        user = await self.user_repository.get_by_id(user_id)

        if user is None:
            raise ValueError("User not found")

        trip = await self.repository.get_by_id(trip_id)

        if trip is None or trip.user_id != user_id:
            raise ValueError("Trip not found")

        return trip

    async def list_by_user(self, user_id: uuid.UUID) -> list[Trip]:

        user = await self.user_repository.get_by_id(user_id)

        if user is None:
            raise ValueError("User not found")

        return await self.repository.list_by_user(user_id)

    async def list_all(
        self,
        user_id: uuid.UUID,
        title: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        primary_currency: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        description: str | None = None,
        page: int = 1,
        per_page: int = 20,
    ) -> dict[str, Any]:

        if page < 1 or per_page < 1:
            raise ValueError("Page and per_page must be greater than or equal to 1")

        user = await self.user_repository.get_by_id(user_id)

        if user is None:
            raise ValueError("User not found")

        return await self.repository.list_all(
            user_id=user_id,
            title=title,
            start_date=start_date,
            end_date=end_date,
            primary_currency=primary_currency,
            date_from=date_from,
            date_to=date_to,
            description=description,
            page=page,
            per_page=per_page,
        )
