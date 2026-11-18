import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class TripRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    description: str | None
    start_date: date
    end_date: date
    primary_currency: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TripCreate(BaseModel):
    title: str
    description: str | None = None
    start_date: date
    end_date: date
    primary_currency: str | None = None


class TripUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    primary_currency: str | None = None


class PaginatedTrips(BaseModel):
    items: list[TripRead]
    total_items: int
    total_pages: int
    current_page: int
    per_page: int
