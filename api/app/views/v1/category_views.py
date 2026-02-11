"""
Category views for e-commerce API v1
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
from ...services.category_service import CategoryService
from ...models.category import CategoryPydantic, CategoryInPydantic

router = APIRouter(prefix="/categories", tags=["categories"])

def get_category_service() -> CategoryService:
    return CategoryService()

@router.get("/", response_model=List[CategoryPydantic])
async def get_categories(service: CategoryService = Depends(get_category_service)):
    try:
        return await service.get_all_categories()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{category_id}", response_model=CategoryPydantic)
async def get_category(
    category_id: int,
    service: CategoryService = Depends(get_category_service)
):
    try:
        category = await service.get_category_by_id(category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        return category
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/slug/{slug}", response_model=CategoryPydantic)
async def get_category_by_slug(
    slug: str,
    service: CategoryService = Depends(get_category_service)
):
    try:
        category = await service.get_category_by_slug(slug)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        return category
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=CategoryPydantic, status_code=201)
async def create_category(
    category_data: CategoryInPydantic,
    service: CategoryService = Depends(get_category_service)
):
    try:
        return await service.create_category(category_data.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{category_id}", response_model=CategoryPydantic)
async def update_category(
    category_id: int,
    category_data: CategoryInPydantic,
    service: CategoryService = Depends(get_category_service)
):
    try:
        category = await service.update_category(category_id, category_data.model_dump())
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        return category
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    service: CategoryService = Depends(get_category_service)
):
    try:
        success = await service.delete_category(category_id)
        if not success:
            raise HTTPException(status_code=404, detail="Category not found")
        return {"message": "Category deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
