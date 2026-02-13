"""
Product views for e-commerce API v1
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models.product import ProductPydantic
from app.services.product_service import ProductService
from app.services.search_service import SearchService
from app.schemas.query import ProductSearchQuery, ProductCategoryQuery, PaginationQuery

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=List[ProductPydantic])
async def get_products(
    pagination: PaginationQuery = Depends(),
    service: ProductService = Depends(ProductService)
):
    try:
        return await service.get_all_products(pagination)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{product_id}", response_model=ProductPydantic)
async def get_product(
    product_id: int,
    service: ProductService = Depends(ProductService)
):
    try:
        product = await service.get_product_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search", response_model=List[ProductPydantic])
async def search_products(
    query: ProductSearchQuery = Depends(),
    service: SearchService = Depends(SearchService)
):
    try:
        return await service.search_products(query.query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/category/{category_name}", response_model=List[ProductPydantic])
async def get_products_by_category(
    query: ProductCategoryQuery = Depends(),
    service: ProductService = Depends(ProductService)
):
    try:
        return await service.get_products_by_category(query.category_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    service: ProductService = Depends(ProductService)
):
    try:
        success = await service.delete_product(product_id)
        if not success:
            raise HTTPException(status_code=404, detail="Product not found")
        return {"message": "Product deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
