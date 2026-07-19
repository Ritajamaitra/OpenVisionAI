from sqlalchemy.orm import Session

from app.auth.hashing import hash_password, verify_password
from app.auth.jwt import create_access_token, decode_token
from app.models.user import User
from app.models.user_role import UserRole
from app.services.user_services import (
    UserAlreadyExistsError,
    UserNotFoundError,
    UserService,
    UsernameAlreadyExistsError,
)


class InvalidCredentialsError(Exception):
    """Raised when authentication fails."""
    pass


class AuthenticationService:
    """
    Handles authentication workflows.

    Responsibilities
    ----------------
    - Register users
    - Authenticate users
    - Resolve the current authenticated user
    """

    def __init__(self):
        self.user_service = UserService()

    def register_user(
        self,
        db: Session,
        user: User,
        password: str,
    ) -> User:
        """
        Register a new user.
        """

        # Hash password BEFORE persisting
        user.password_hash = hash_password(password)
        user.role = UserRole.USER  

        return self.user_service.create_user(
            db=db,
            user=user,
        )

    def authenticate_user(
        self,
        db: Session,
        email: str,
        password: str,
    ) -> str:
        """
        Authenticate a user and return a JWT.
        """

        user = self.user_service.get_by_email(
            db,
            email,
        )

        if user is None:
            raise InvalidCredentialsError(
                "Invalid email or password."
            )

        if not verify_password(
            password,
            user.password_hash,
        ):
            raise InvalidCredentialsError(
                "Invalid email or password."
            )

        return create_access_token(
            user_id=user.id,
            username=user.username,
            role=user.role.value,
        )

    def get_current_user(
        self,
        db: Session,
        token: str,
    ) -> User:
        """
        Resolve the current authenticated user.
        """

        payload = decode_token(token)

        user_id = int(payload["sub"])

        return self.user_service.get_user(
            db,
            user_id,
        )