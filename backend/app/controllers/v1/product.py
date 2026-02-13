"""
Product views for e-commerce API v1
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List,Optional
from pydantic import BaseModel, Field
from app.services import ProductService
from app.services import SearchService
from app.models import Product_Pydantic_List
from backend.app.models.product import Product_Pydantic


router = APIRouter(prefix="/products", tags=["products"])

class PaginationQuery(BaseModel):
    limit: int = Field(default=10, ge=1)
    offset: int = Field(default=0, ge=0)

@router.get("/", response_model=List[Product_Pydantic_List])
async def get_products(
    pagination: PaginationQuery = Depends(),
    category: Optional[str] = Query(None, description="Filter products by category name"),
    service: ProductService = Depends(ProductService)
):
    try:
        if category:
            return await service.get_products_by_category(category, pagination)
        else:
            return await service.get_all_products(pagination)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{product_id}", response_model=Product_Pydantic)
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

@router.get("/search", response_model=List[Product_Pydantic])
async def search_products(
    query: str = Query(..., description="Search query"),
    service: SearchService = Depends(SearchService)
):
    try:
        return await service.search_products(query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

