from fastapi import APIRouter, Depends, HTTPException, status
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

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

auth_service = AuthenticationService()
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
    request: LoginRequest,
    db: Session = Depends(get_db),
):
    try:
        token = auth_service.authenticate_user(
            db=db,
            email=request.email,
            password=request.password,
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
    

from fastapi import Depends

from app.auth.dependencies import get_current_user


@router.get(
    "/me",
    response_model=UserResponse,
)
def me(
    current_user: User = Depends(get_current_user),
):
    return current_user