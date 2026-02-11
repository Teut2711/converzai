"""
Database configuration and connection management using Tortoise ORM
"""

from tortoise import Tortoise
from typing import Dict, Any
from app.config.settings import settings

TORTOISE_ORM: Dict[str, Any] = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.mysql",
            "credentials": {
                "dsn": settings.DATABASE_URL,
                "minsize": 5,
                "maxsize": 20,
                "connect_timeout": 10,
                "charset": "utf8mb4",
                "autocommit": True,
            },
        }
    },
    "apps": {
        "models": {
            "models": ["app.models"],
            "default_connection": "default",
        },
    },
}
async def init_db():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()

async def close_db():
    await Tortoise.close_connections()

