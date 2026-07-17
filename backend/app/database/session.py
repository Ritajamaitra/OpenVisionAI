from collections.abc import Generator

from sqlalchemy.orm import Session, sessionmaker # type: ignore

from app.database.connection import engine

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()