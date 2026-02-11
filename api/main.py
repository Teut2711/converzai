"""
E-commerce API Main Application
FastAPI application with MySQL and Elasticsearch integration using Tortoise ORM
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database.database import init_db, close_db
from app.database.connections import init_es, close_es
from app.views.v1 import v1_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await init_es()
    yield
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

# Include v1 API
app.include_router(v1_router)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

