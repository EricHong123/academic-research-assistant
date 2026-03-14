"""Authentication API routes."""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
import jwt
import os


router = APIRouter()

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"

# In-memory user storage
_users_db: dict[str, dict] = {}


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


class UserCreate(BaseModel):
    """User registration model."""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User response model."""

    id: str
    email: str
    created_at: str


class TokenResponse(BaseModel):
    """Token response model."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


def create_access_token(user_id: str, email: str) -> tuple[str, int]:
    """Create JWT access token."""
    expires_delta = timedelta(minutes=1440)  # 24 hours
    expire = datetime.utcnow() + expires_delta

    payload = {
        "sub": user_id,
        "email": email,
        "exp": expire,
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token, int(expires_delta.total_seconds())


@router.post("/register", response_model=dict)
async def register(user: UserCreate):
    """Register a new user."""
    import uuid
    import bcrypt

    # Check if user exists
    for existing_user in _users_db.values():
        if existing_user["email"] == user.email:
            raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password
    password_hash = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()

    user_id = str(uuid.uuid4())
    user_data = {
        "id": user_id,
        "email": user.email,
        "password_hash": password_hash,
        "created_at": datetime.utcnow().isoformat(),
    }

    _users_db[user_id] = user_data

    return {
        "success": True,
        "data": {
            "id": user_id,
            "email": user.email,
        },
    }


@router.post("/token", response_model=dict)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login and get access token."""
    import bcrypt

    # Find user
    user = None
    for u in _users_db.values():
        if u["email"] == form_data.username:
            user = u
            break

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Verify password
    if not bcrypt.checkpw(form_data.password.encode(), user["password_hash"].encode()):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create token
    token, expires_in = create_access_token(user["id"], user["email"])

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": expires_in,
        "user": {
            "id": user["id"],
            "email": user["email"],
        },
    }


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Get current user from token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")

        if not user_id or user_id not in _users_db:
            raise HTTPException(status_code=401, detail="Invalid token")

        return _users_db[user_id]

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.get("/me", response_model=dict)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user info."""
    return {
        "success": True,
        "data": {
            "id": current_user["id"],
            "email": current_user["email"],
            "created_at": current_user["created_at"],
        },
    }
