"""MongoDB document models (not ODM — raw dict shapes for reference)."""

from datetime import datetime, timezone
from typing import Optional


def user_document(
    name: str,
    email: str,
    hashed_password: str,
) -> dict:
    """Create a user document for MongoDB insertion."""
    return {
        "name": name,
        "email": email,
        "hashed_password": hashed_password,
        "created_at": datetime.now(timezone.utc),
    }


def task_document(
    title: str,
    description: str,
    status: str,
    priority: str,
    owner_id: str,
) -> dict:
    """Create a task document for MongoDB insertion."""
    return {
        "title": title,
        "description": description,
        "status": status,
        "priority": priority,
        "owner_id": owner_id,
        "created_at": datetime.now(timezone.utc),
    }
