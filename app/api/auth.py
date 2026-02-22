"""Auth API routes — registration and login."""

from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_db
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(data: RegisterRequest, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Register a new user and return a JWT access token."""
    service = AuthService(db)
    return await service.register(data)


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Authenticate a user and return a JWT access token."""
    service = AuthService(db)
    return await service.login(data)
