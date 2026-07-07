from fastapi import FastAPI # type: ignore

from app.api.api import api_router # type: ignore
from app.config.settings import settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)

app.include_router(api_router)