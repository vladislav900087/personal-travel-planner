import uuid
from datetime import date

from fastapi import APIRouter, HTTPException, Query, status

from app.api.dependencies import CurrentUser, TripService
from app.schemas.trip import PaginatedTrips, TripCreate, TripRead, TripUpdate

router = APIRouter(prefix="/trips", tags=["Trips"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=TripRead)
async def create_trip(
    body: TripCreate,
    user: CurrentUser,
    service: TripService,
):
    try:
        return await service.create_trip(
            user_id=user.id,
            title=body.title,
            description=body.description,
            primary_currency=body.primary_currency or "USD",
            start_date=body.start_date,
            end_date=body.end_date,
        )
    except ValueError as exc:
        msg = str(exc)
        if "not found" in msg.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=msg
            ) from exc
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=msg
        ) from exc


@router.get("", status_code=status.HTTP_200_OK, response_model=PaginatedTrips)
async def list_trips(
    user: CurrentUser,
    service: TripService,
    title: str | None = Query(default=None),
    description: str | None = Query(default=None),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    primary_currency: str | None = Query(default=None),
    page: int = Query(default=1, ge=1, le=100),
    per_page: int = Query(default=20, ge=1, le=100),
):
    try:
        return await service.list_all(
            user_id=user.id,
            title=title,
            description=description,
            start_date=start_date,
            end_date=end_date,
            date_from=date_from,
            date_to=date_to,
            primary_currency=primary_currency,
            page=page,
            per_page=per_page,
        )
    except ValueError as exc:
        msg = str(exc)
        if "not found" in msg.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=msg
            ) from exc
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=msg
        ) from exc


@router.get("/{trip_id}", status_code=status.HTTP_200_OK, response_model=TripRead)
async def get_trip(
    trip_id: uuid.UUID,
    user: CurrentUser,
    service: TripService,
):
    try:
        return await service.get_by_id(user_id=user.id, trip_id=trip_id)
    except ValueError as exc:
        msg = str(exc)
        if "not found" in msg.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=msg
            ) from exc
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=msg
        ) from exc


@router.patch("/{trip_id}", status_code=status.HTTP_200_OK, response_model=TripRead)
async def update_trip(
    trip_id: uuid.UUID,
    body: TripUpdate,
    user: CurrentUser,
    service: TripService,
):
    try:
        return await service.update_trip(
            user_id=user.id,
            trip_id=trip_id,
            title=body.title,
            start_date=body.start_date,
            end_date=body.end_date,
            primary_currency=body.primary_currency,
            description=body.description,
        )
    except ValueError as exc:
        msg = str(exc)
        if "not found" in msg.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=msg
            ) from exc
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=msg
        ) from exc


@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trip(
    trip_id: uuid.UUID,
    user: CurrentUser,
    service: TripService,
):
    try:
        await service.delete_trip(user_id=user.id, trip_id=trip_id)
    except ValueError as exc:
        msg = str(exc)
        if "not found" in msg.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=msg
            ) from exc
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=msg
        ) from exc
