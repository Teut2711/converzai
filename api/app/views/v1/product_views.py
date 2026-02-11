"""
Product views for e-commerce API v1
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List
from ...services.product_service import ProductService
from ...models.product import ProductOutPydantic, ProductInPydantic

router = APIRouter(prefix="/products", tags=["products"])

def get_product_service() -> ProductService:
    return ProductService()

@router.get("/", response_model=List[ProductOutPydantic])
async def get_products(
    category: str = Query(None, description="Filter by category name"),
    service: ProductService = Depends(get_product_service)
):
    try:
        if category:
            return await service.get_products_by_category(category)
        return await service.get_all_products()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{product_id}", response_model=ProductOutPydantic)
async def get_product(
    product_id: int,
    service: ProductService = Depends(get_product_service)
):
    try:
        product = await service.get_product_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=ProductOutPydantic, status_code=201)
async def create_product(
    product_data: ProductInPydantic,
    service: ProductService = Depends(get_product_service)
):
    try:
        return await service.create_product(product_data.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{product_id}", response_model=ProductOutPydantic)
async def update_product(
    product_id: int,
    product_data: ProductInPydantic,
    service: ProductService = Depends(get_product_service)
):
    try:
        product = await service.update_product(product_id, product_data.model_dump())
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    service: ProductService = Depends(get_product_service)
):
    try:
        success = await service.delete_product(product_id)
        if not success:
            raise HTTPException(status_code=404, detail="Product not found")
        return {"message": "Product deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
