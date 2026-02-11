"""
E-commerce API Main Application
FastAPI application with MySQL and Elasticsearch integration using Tortoise ORM
"""

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app.models.product import Product, ProductCreate, ProductResponse
from app.models.category import Category, CategoryResponse
from app.services.product_service import ProductService
from app.services.category_service import CategoryService
from app.services.search_service import SearchService
from app.database.database import init_db, close_db, get_db_config

# Create FastAPI application
app = FastAPI(
    title="E-commerce API",
    description="Simple e-commerce REST API with MySQL and Elasticsearch",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency injection
def get_product_service() -> ProductService:
    return ProductService()

def get_category_service() -> CategoryService:
    return CategoryService()

def get_search_service() -> SearchService:
    return SearchService(os.getenv("ELASTICSEARCH_URL", "http://elasticsearch:9200"))

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await init_db()

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown"""
    await close_db()

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "E-commerce API", "version": "1.0.0"}

@app.get("/categories", response_model=List[CategoryResponse])
async def get_categories(service: CategoryService = Depends(get_category_service)):
    """List all categories"""
    try:
        categories = await service.get_all_categories()
        return [CategoryResponse.model_validate(cat) for cat in categories]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/products", response_model=List[ProductResponse])
async def get_products(
    category: Optional[str] = Query(None, description="Filter by category"),
    service: ProductService = Depends(get_product_service)
):
    """List all products, optionally filtered by category"""
    try:
        if category:
            products = await service.get_products_by_category(category)
        else:
            products = await service.get_all_products()
        return [ProductResponse.model_validate(product) for product in products]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    service: ProductService = Depends(get_product_service)
):
    """Fetch a single product by ID"""
    try:
        product = await service.get_product_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return ProductResponse.model_validate(product)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/products/search", response_model=List[ProductResponse])
async def search_products(
    query: str = Query(..., description="Search query"),
    service: SearchService = Depends(get_search_service)
):
    """Full-text search using Elasticsearch"""
    try:
        products = await service.search_products(query)
        return [ProductResponse.model_validate(product) for product in products]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
