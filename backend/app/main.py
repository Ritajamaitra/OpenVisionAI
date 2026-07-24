from fastapi import FastAPI

from app.api.routes.auth import router as auth_router
from app.api.routes.project import router as project_router
from app.api.routes.datasets import router as dataset_router
from app.api.routes.models import router as model_router
from app.api.routes.reports import router as report_router
from app.config.settings import settings
from app.router import api_router

api_router.include_router(auth_router)
api_router.include_router(project_router)
api_router.include_router(dataset_router)
api_router.include_router(model_router)
api_router.include_router(report_router)
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)

app.include_router(api_router)