"""
Search views for e-commerce API v1
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List
from app.services.search_service import SearchService
from app.models.product import ProductOutPydantic
from app.config.settings import settings

router = APIRouter(prefix="/search", tags=["search"])

def get_search_service() -> SearchService:
    return SearchService(settings.ELASTICSEARCH_URL)

@router.get("/products", response_model=List[ProductOutPydantic])
async def search_products(
    query: str = Query(..., description="Search query"),
    service: SearchService = Depends(get_search_service)
):
    try:
        products = await service.search_products(query)
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
