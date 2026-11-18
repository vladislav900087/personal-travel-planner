from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database import get_db
from app.models.user import User
from app.repositories.token_repository import TokenRepository
from app.repositories.trip_repository import TripRepository
from app.repositories.user_repository import UserRepository
from app.services import auth_service

from app.services.trip_service import TripService


bearer = HTTPBearer()


def get_user_repo(db: Annotated[AsyncSession, Depends(get_db)]) -> UserRepository:
    return UserRepository(db)


def get_token_repo(db: Annotated[AsyncSession, Depends(get_db)]) -> TokenRepository:
    return TokenRepository(db)


def get_trip_repo(db: Annotated[AsyncSession, Depends(get_db)]) -> TripRepository:
    return TripRepository(db=db)


UserRepo = Annotated[UserRepository, Depends(get_user_repo)]
TokenRepo = Annotated[TokenRepository, Depends(get_token_repo)]
TripRepo = Annotated[TripRepository, Depends(get_trip_repo)]


def get_trip_service(repo: TripRepo, user_repo: UserRepo) -> TripService:
    return TripService(repository=repo, user_repository=user_repo)


TripService = Annotated[TripService, Depends(get_trip_service)]

async def get_current_user(
    creds: Annotated[HTTPAuthorizationCredentials, Depends(bearer)], user_repo: UserRepo
) -> User:
    try:
        return await auth_service.get_current_user(creds.credentials, user_repo)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid access token")


CurrentUser = Annotated[User, Depends(get_current_user)]
