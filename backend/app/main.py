from fastapi import FastAPI

from app.api.routes.auth import router as auth_router
from app.api.routes.project import router as project_router
from app.config.settings import settings
from app.router import api_router

api_router.include_router(auth_router)
api_router.include_router(project_router)
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)

app.include_router(api_router)