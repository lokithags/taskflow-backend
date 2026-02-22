"""User API routes — profile management."""

from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_current_user_id, get_db
from app.schemas.user import UserResponse, UserUpdateRequest
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_profile(
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Get the authenticated user's profile."""
    service = UserService(db)
    return await service.get_profile(user_id)


@router.put("/me", response_model=UserResponse)
async def update_profile(
    data: UserUpdateRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Update the authenticated user's profile."""
    service = UserService(db)
    return await service.update_profile(user_id, data)
