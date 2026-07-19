from pydantic import BaseModel, EmailStr

from app.models.user_role import UserRole
from pydantic import ConfigDict

class UserResponse(BaseModel):
    id: int

    username: str

    email: EmailStr

    full_name: str | None = None

    role: UserRole

    is_active: bool

    model_config = ConfigDict(
        from_attributes=True
    )