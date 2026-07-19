from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt.

    Args:
        password: Plain text password.

    Returns:
        Secure bcrypt hash.
    """
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """
    Verify a plain text password against its stored hash.

    Args:
        plain_password: Password provided by the user.
        hashed_password: Password hash stored in the database.

    Returns:
        True if the password matches, otherwise False.
    """
    return pwd_context.verify(
        plain_password,
        hashed_password,
    )