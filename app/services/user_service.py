"""User service — profile retrieval and updates."""

from bson import ObjectId
from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.schemas.user import UserResponse, UserUpdateRequest


class UserService:
    """Business logic for user profile operations."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.users

    async def get_profile(self, user_id: str) -> UserResponse:
        """Fetch user profile by ID."""
        user = await self.collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )
        return UserResponse(
            id=str(user["_id"]),
            name=user["name"],
            email=user["email"],
            created_at=user["created_at"],
        )

    async def update_profile(self, user_id: str, data: UserUpdateRequest) -> UserResponse:
        """Update user profile fields."""
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update.",
            )

        # Check email uniqueness if email is being updated
        if "email" in update_data:
            existing = await self.collection.find_one(
                {"email": update_data["email"], "_id": {"$ne": ObjectId(user_id)}}
            )
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A user with this email already exists.",
                )

        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(user_id)},
            {"$set": update_data},
            return_document=True,
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )
        return UserResponse(
            id=str(result["_id"]),
            name=result["name"],
            email=result["email"],
            created_at=result["created_at"],
        )
