from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self):
        super().__init__(User)

    def find_by_email(
        self,
        db: Session,
        email: str,
    ) -> User | None:
        return (
            db.query(User)
            .filter(User.email == email)
            .first()
        )

    def find_by_username(
        self,
        db: Session,
        username: str,
    ) -> User | None:
        return (
            db.query(User)
            .filter(User.username == username)
            .first()
        )

    def find_active_users(
        self,
        db: Session,
    ) -> list[User]:
        return (
            db.query(User)
            .filter(User.is_active.is_(True))
            .all()
        )