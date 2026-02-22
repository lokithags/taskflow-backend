"""MongoDB connection management with Motor async driver."""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import settings


class MongoDB:
    """Singleton-style MongoDB connection holder."""

    client: AsyncIOMotorClient = None  # type: ignore
    db: AsyncIOMotorDatabase = None  # type: ignore


mongodb = MongoDB()


async def connect_to_mongo() -> None:
    """Establish connection to MongoDB Atlas."""
    mongodb.client = AsyncIOMotorClient(settings.MONGODB_URI)
    mongodb.db = mongodb.client.get_default_database("jwt_task_db")

    # Create indexes
    await mongodb.db.users.create_index("email", unique=True)
    await mongodb.db.tasks.create_index("owner_id")
    await mongodb.db.tasks.create_index("status")
    await mongodb.db.tasks.create_index([("title", "text"), ("description", "text")])

    print("✅ Connected to MongoDB Atlas")


async def close_mongo_connection() -> None:
    """Close the MongoDB connection."""
    if mongodb.client:
        mongodb.client.close()
        print("🔌 MongoDB connection closed")


def get_database() -> AsyncIOMotorDatabase:
    """Return the database instance for dependency injection."""
    return mongodb.db
