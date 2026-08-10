from fastapi import FastAPI

from app.api.routes.auth import router as auth_router
from app.api.routes.project import router as project_router
from app.api.routes.datasets import router as dataset_router
from app.api.routes.models import router as model_router
from app.api.routes.reports import router as report_router
from app.api.routes.uploads import router as uploads_router
from app.api.routes.annotations import router as annotation_router
from app.api.routes.exports import router as export_router
from app.api.routes.experiments import router as experiment_router
from app.api.routes.training_run import router as training_run_router  
from app.config.settings import settings
from app.router import api_router

api_router.include_router(auth_router)
api_router.include_router(project_router)
api_router.include_router(dataset_router)
api_router.include_router(model_router)
api_router.include_router(report_router)
api_router.include_router(uploads_router)
api_router.include_router(annotation_router)
api_router.include_router(export_router)
api_router.include_router(experiment_router)
api_router.include_router(training_run_router)
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

app.include_router(api_router)