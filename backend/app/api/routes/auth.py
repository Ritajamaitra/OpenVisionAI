from datetime import datetime, timedelta
import secrets
import string

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
)
from app.schemas.user import UserResponse
from app.services.authentication_services import AuthenticationService
from app.auth.hashing import hash_password


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

auth_service = AuthenticationService()

# Lightweight in-memory CAPTCHA store for the local/demo application.
# A production deployment should move this to Redis/database-backed storage.
_reset_challenges: dict[str, tuple[str, datetime]] = {}
CAPTCHA_TTL_MINUTES = 10


def _generate_captcha(length: int = 6) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db),
):
    try:
        user = User(
            username=request.username,
            email=request.email,
            full_name=request.full_name,
        )

        result = auth_service.register_user(
            db=db,
            user=user,
            password=request.password,
        )

        return result

    except Exception as exc:
        import traceback

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=f"{type(exc).__name__}: {exc}",
        )


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    try:
        token = auth_service.authenticate_user(
            db=db,
            email=form_data.username,
            password=form_data.password,
        )

        return TokenResponse(
            access_token=token,
            token_type="bearer",
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )


@router.post("/forgot-password/captcha")
def generate_reset_captcha(email: str, db: Session = Depends(get_db)):
    """
    Generate a short-lived CAPTCHA challenge for password reset.

    The CAPTCHA is returned so the frontend can display it. This is intended
    for the local/demo application requested for OpenVisionAI.
    """
    user = db.query(User).filter(User.email == email).first()

    # Do not reveal whether the email exists.
    captcha = _generate_captcha()
    _reset_challenges[email.strip().lower()] = (
        captcha,
        datetime.utcnow() + timedelta(minutes=CAPTCHA_TTL_MINUTES),
    )

    return {
        "message": "If the account exists, a CAPTCHA has been generated.",
        "captcha": captcha,
        "expires_in_seconds": CAPTCHA_TTL_MINUTES * 60,
    }


@router.post("/forgot-password/reset")
def reset_password(
    email: str,
    captcha: str,
    new_password: str,
    db: Session = Depends(get_db),
):
    """
    Verify the CAPTCHA and reset the account password.

    For production, this should additionally require a time-limited
    email-verification/reset token.
    """
    normalized_email = email.strip().lower()
    challenge = _reset_challenges.get(normalized_email)

    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CAPTCHA expired or not generated. Please generate a new CAPTCHA.",
        )

    expected_captcha, expires_at = challenge

    if datetime.utcnow() > expires_at:
        _reset_challenges.pop(normalized_email, None)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CAPTCHA expired. Please generate a new CAPTCHA.",
        )

    if captcha.strip().upper() != expected_captcha:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect CAPTCHA.",
        )

    user = db.query(User).filter(User.email == normalized_email).first()

    # Consume the CAPTCHA after a successful verification.
    _reset_challenges.pop(normalized_email, None)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to reset password for this account.",
        )

    if len(new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters.",
        )

    user.password_hash = hash_password(new_password)
    db.commit()

    return {"message": "Password reset successfully."}


from app.auth.dependencies import get_current_user


@router.get(
    "/me",
    response_model=UserResponse,
)
def me(
    current_user: User = Depends(get_current_user),
):
    return current_user
