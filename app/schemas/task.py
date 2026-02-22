"""Pydantic schemas for Task domain."""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, examples=["Build auth module"])
    description: str = Field("", max_length=2000, examples=["Implement JWT-based authentication"])
    status: TaskStatus = Field(TaskStatus.PENDING)
    priority: TaskPriority = Field(TaskPriority.MEDIUM)


class TaskUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None


class TaskResponse(BaseModel):
    id: str
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    owner_id: str
    created_at: datetime


class TaskListResponse(BaseModel):
    tasks: List[TaskResponse]
    total: int
