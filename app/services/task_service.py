"""Task service — CRUD operations with search and filtering."""

from typing import Optional

from bson import ObjectId
from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.user import task_document
from app.schemas.task import (
    TaskCreateRequest,
    TaskListResponse,
    TaskResponse,
    TaskUpdateRequest,
)


class TaskService:
    """Business logic for task CRUD."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.tasks

    def _to_response(self, doc: dict) -> TaskResponse:
        return TaskResponse(
            id=str(doc["_id"]),
            title=doc["title"],
            description=doc["description"],
            status=doc["status"],
            priority=doc.get("priority", "medium"),
            owner_id=doc["owner_id"],
            created_at=doc["created_at"],
        )

    async def create(self, data: TaskCreateRequest, owner_id: str) -> TaskResponse:
        """Create a new task."""
        doc = task_document(
            title=data.title,
            description=data.description,
            status=data.status.value,
            priority=data.priority.value,
            owner_id=owner_id,
        )
        result = await self.collection.insert_one(doc)
        doc["_id"] = result.inserted_id
        return self._to_response(doc)

    async def list_tasks(
        self,
        owner_id: str,
        search: Optional[str] = None,
        task_status: Optional[str] = None,
    ) -> TaskListResponse:
        """List tasks with optional search and status filter."""
        query: dict = {"owner_id": owner_id}

        if task_status:
            query["status"] = task_status

        if search:
            query["$or"] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}},
            ]

        cursor = self.collection.find(query).sort("created_at", -1)
        tasks = await cursor.to_list(length=1000)
        total = await self.collection.count_documents(query)

        return TaskListResponse(
            tasks=[self._to_response(t) for t in tasks],
            total=total,
        )

    async def get_by_id(self, task_id: str, owner_id: str) -> TaskResponse:
        """Get a single task by ID, scoped to owner."""
        if not ObjectId.is_valid(task_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid task ID.")

        doc = await self.collection.find_one({"_id": ObjectId(task_id), "owner_id": owner_id})
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")
        return self._to_response(doc)

    async def update(self, task_id: str, data: TaskUpdateRequest, owner_id: str) -> TaskResponse:
        """Update a task."""
        if not ObjectId.is_valid(task_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid task ID.")

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update.")

        # Convert enum to string value
        if "status" in update_data and update_data["status"] is not None:
            update_data["status"] = update_data["status"].value
        if "priority" in update_data and update_data["priority"] is not None:
            update_data["priority"] = update_data["priority"].value

        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(task_id), "owner_id": owner_id},
            {"$set": update_data},
            return_document=True,
        )
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")
        return self._to_response(result)

    async def delete(self, task_id: str, owner_id: str) -> None:
        """Delete a task."""
        if not ObjectId.is_valid(task_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid task ID.")

        result = await self.collection.delete_one({"_id": ObjectId(task_id), "owner_id": owner_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")
