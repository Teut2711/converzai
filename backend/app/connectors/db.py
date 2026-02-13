from app.settings import settings
from typing import Dict, Any, Optional
from fastapi import FastAPI
from tortoise.contrib.fastapi import RegisterTortoise

TORTOISE_ORM: Dict[str, Any] = {
    "connections": {
        "default": {
            "engine": f"tortoise.backends.{settings.DB_DRIVER}",
            "credentials": {
                "host": settings.DB_HOST,
                "port": settings.DB_PORT,
                "user": settings.DB_USER,
                "password": settings.DB_PASSWORD,
                "database": settings.DB_DATABASE,
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
    "generate_schemas": True,
}



_instance: Optional[RegisterTortoise] = None 
async def init_db(app: FastAPI) -> None:
    global _instance
    _instance = RegisterTortoise(app, config=TORTOISE_ORM, generate_schemas=True)
    await _instance.init_orm()

async def close_db() -> None:
    global _instance
    if _instance:
        await _instance.close_orm()