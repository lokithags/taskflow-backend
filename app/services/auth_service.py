"""Auth service — handles registration, login, and token creation."""

from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import user_document
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse


class AuthService:
    """Business logic for authentication operations."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.users

    async def register(self, data: RegisterRequest) -> TokenResponse:
        """Register a new user, return JWT."""
        existing = await self.collection.find_one({"email": data.email})
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists.",
            )

        doc = user_document(
            name=data.name,
            email=data.email,
            hashed_password=hash_password(data.password),
        )
        result = await self.collection.insert_one(doc)
        token = create_access_token(subject=str(result.inserted_id))
        return TokenResponse(access_token=token)

    async def login(self, data: LoginRequest) -> TokenResponse:
        """Authenticate user and return JWT."""
        user = await self.collection.find_one({"email": data.email})
        if not user or not verify_password(data.password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = create_access_token(subject=str(user["_id"]))
        return TokenResponse(access_token=token)
