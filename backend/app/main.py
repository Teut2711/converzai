"""
E-commerce API Main Application
FastAPI application with MySQL and Elasticsearch integration using Tortoise ORM
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
from contextlib import asynccontextmanager
from app.database.search_engine import init_es, close_es
from ingest_data import DataIngestionService
from app.controllers.v1 import v1_router
from app.utils import get_logger
from tortoise.contrib.fastapi import RegisterTortoise
from app.settings import settings
  

 
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
}



logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database and Elasticsearch
    instance = RegisterTortoise(app, config=TORTOISE_ORM)
    await instance.init_orm()

    await init_es()
    
    # Load seed data using DataIngestionService
    ingestion_service = DataIngestionService()
    try:
        await ingestion_service.load_seed_data()
    except Exception as e:
        logger.error(f"Error loading seed data: {e}")
    
    yield
    
    # Cleanup
    await ingestion_service.close()
    await instance.close_orm()
    await close_es()

app = FastAPI(
    title="E-commerce API",
    description="Simple e-commerce REST API with MySQL and Elasticsearch",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include v1 API
app.include_router(v1_router)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
