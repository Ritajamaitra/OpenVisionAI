from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.base_services import BaseService


class UserAlreadyExistsError(Exception):
    """Raised when an email already exists."""
    pass


class UsernameAlreadyExistsError(Exception):
    """Raised when a username already exists."""
    pass


class UserNotFoundError(Exception):
    """Raised when a user cannot be found."""
    pass


class UserService(BaseService[User]):
    """
    Business logic related to users.
    """

    def __init__(self):
        super().__init__(UserRepository())

    def create_user(
        self,
        db: Session,
        user: User,
    ) -> User:
        """
        Creates a new user after validating uniqueness.
        """

        self._validate_unique_email(db, user.email)
        self._validate_unique_username(db, user.username)

        return self.repository.create(db, user)

    def _validate_unique_email(
        self,
        db: Session,
        email: str,
    ) -> None:
        if self.repository.find_by_email(db, email):
            raise UserAlreadyExistsError(
                "Email already exists."
            )

    def _validate_unique_username(
        self,
        db: Session,
        username: str,
    ) -> None:
        if self.repository.find_by_username(db, username):
            raise UsernameAlreadyExistsError(
                "Username already exists."
            )

    def get_active_users(
        self,
        db: Session,
    ) -> list[User]:
        return self.repository.find_active_users(db)

    def get_by_email(
        self,
        db: Session,
        email: str,
    ) -> User | None:
        return self.repository.find_by_email(db, email)

    def get_by_username(
        self,
        db: Session,
        username: str,
    ) -> User | None:
        return self.repository.find_by_username(db, username)

    def get_user(
        self,
        db: Session,
        user_id: int,
    ) -> User:
        user = self.repository.get_by_id(db, user_id)

        if user is None:
            raise UserNotFoundError(
                "User not found."
            )

        return user