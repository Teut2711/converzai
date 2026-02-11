"""
Database configuration and connection management using Tortoise ORM
"""

from tortoise import Tortoise
from tortoise.contrib.fastapi import register_tortoise
from typing import Dict, Any
from app.config.settings import settings


async def init_db():
    """Initialize database connection"""
    await Tortoise.init(config=settings.tortoise_config)
    await Tortoise.generate_schemas()

async def close_db():
    """Close database connection"""
    await Tortoise.close_connections()

def get_db_config() -> Dict[str, Any]:
    """Get database configuration for FastAPI"""
    return {
        "db_url": settings.database_url,
        "modules": ["app.models.product", "app.models.category"],
        "generate_schemas": True,
    }
