from fastapi import APIRouter, Depends # type: ignore
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.session import get_db

router = APIRouter()


@router.get("/health")
def health():
    return {
        "status": "healthy",
        "version": "0.1.0",
        "service": "OpenVisionAI",
    }



@router.get("/health/db")
def database_health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected",
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "type": type(e).__name__,
        }