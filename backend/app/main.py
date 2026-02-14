"""
E-commerce API Main Application
FastAPI application with MySQL and Elasticsearch integration using Tortoise ORM
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.utils import get_logger
from app.connectors import init_db, close_db
from app.connectors import init_es, close_es
  

 
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database and Elasticsearch
    await init_db(app)
    await init_es()


    from app.services import DataIngestionService
    # Load seed data using DataIngestionService
    ingestion_service = DataIngestionService()
    try:
        logger.info("Loading seed data...")
        await ingestion_service.load_seed_data()
        logger.info("Seed data loaded successfully")    
    except Exception as e:
        logger.error(f"Error loading seed data: {e}")    
    yield
    
    # Cleanup
    await ingestion_service.close()
    await close_db()
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

# noqa: F401
from app.controllers.v1 import v1_router


# Include v1 API
app.include_router(v1_router)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
