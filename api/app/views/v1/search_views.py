"""
Search views for e-commerce API v1
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List
from ...services.search_service import SearchService
from ...models.product import ProductOutPydantic

router = APIRouter(prefix="/search", tags=["search"])

def get_search_service() -> SearchService:
    from ...config.settings import settings
    return SearchService(settings.elasticsearch_url)

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
