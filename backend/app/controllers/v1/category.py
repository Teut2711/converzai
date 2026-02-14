"""
Search views for e-commerce API v1
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List

from app.services import ProductService


router = APIRouter(prefix="/categories")


@router.get("/", response_model=List[str])
async def get_categories(
    service: ProductService = Depends(ProductService)
):
    try:
        return await service.get_all_categories()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
