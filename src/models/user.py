"""User and authentication models."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    """Base user model."""

    email: EmailStr


class UserCreate(UserBase):
    """User creation model."""

    password: str = Field(..., min_length=8)


class User(UserBase):
    """User model."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    is_active: bool = True


class Token(BaseModel):
    """JWT token model."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: User


class TokenData(BaseModel):
    """Token payload data."""

    user_id: Optional[str] = None
    exp: Optional[datetime] = None
