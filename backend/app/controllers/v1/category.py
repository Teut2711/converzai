"""
Search views for e-commerce API v1
"""

from fastapi import APIRouter, Depends
from typing import List


from app.services import DatabaseService, get_db_service


router = APIRouter(prefix="/categories")


@router.get("/", response_model=List[str])
async def get_categories(service: DatabaseService = Depends(get_db_service)):
    return await service.get_all_categories()
