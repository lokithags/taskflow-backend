"""Task API routes — full CRUD with search and filtering."""

from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_current_user_id, get_db
from app.schemas.auth import MessageResponse
from app.schemas.task import (
    TaskCreateRequest,
    TaskListResponse,
    TaskResponse,
    TaskUpdateRequest,
)
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    data: TaskCreateRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Create a new task for the authenticated user."""
    service = TaskService(db)
    return await service.create(data, user_id)


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    search: Optional[str] = Query(None, max_length=200),
    task_status: Optional[str] = Query(None, alias="status"),
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """List tasks with optional search and status filter."""
    service = TaskService(db)
    return await service.list_tasks(user_id, search=search, task_status=task_status)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Get a specific task by ID."""
    service = TaskService(db)
    return await service.get_by_id(task_id, user_id)


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    data: TaskUpdateRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Update a task by ID."""
    service = TaskService(db)
    return await service.update(task_id, data, user_id)


@router.delete("/{task_id}", response_model=MessageResponse)
async def delete_task(
    task_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Delete a task by ID."""
    service = TaskService(db)
    await service.delete(task_id, user_id)
    return MessageResponse(message="Task deleted successfully.")
