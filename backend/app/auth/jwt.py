from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt

from app.auth.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    SECRET_KEY,
)


def create_access_token(
    *,
    user_id: int,
    username: str,
    role: str,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Create a signed JWT access token.
    """

    expire = (
        datetime.now(UTC)
        + (
            expires_delta
            if expires_delta
            else timedelta(
                minutes=ACCESS_TOKEN_EXPIRE_MINUTES
            )
        )
    )

    payload = {
        "sub": str(user_id),
        "username": username,
        "role": role,
        "exp": expire,
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def verify_access_token(token: str) -> bool:
    """
    Verify that the token is valid and not expired.
    """

    try:
        jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )
        return True

    except JWTError:
        return False


def decode_token(token: str) -> dict:
    """
    Decode and return the JWT payload.

    Raises JWTError if invalid.
    """

    return jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM],
    )