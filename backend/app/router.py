from fastapi import APIRouter # type: ignore
from app.health import router as health_router # type: ignore

api_router = APIRouter()

api_router.include_router(
    health_router,
    prefix="/api/v1",
    tags=["Health"]
)