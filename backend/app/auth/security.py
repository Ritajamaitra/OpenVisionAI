from app.config.settings import settings

SECRET_KEY = settings.secret_key

ALGORITHM = settings.algorithm

ACCESS_TOKEN_EXPIRE_MINUTES = (
    settings.access_token_expire_minutes
)