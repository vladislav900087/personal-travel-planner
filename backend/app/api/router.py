from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.trips import router as trips_router

router = APIRouter(prefix="/api/v1", tags=["Main router"])

router.include_router(auth_router, tags=["Authentication"])
router.include_router(trips_router, tags=["Trips"])

