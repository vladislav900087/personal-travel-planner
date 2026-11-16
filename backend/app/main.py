from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import router as main_router
from app.core.config import settings

app = FastAPI(title="Personal Travel Planner", version="0.1.0")

app.include_router(main_router)

# allow frontend to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
