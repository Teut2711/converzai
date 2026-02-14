"""
Product views for e-commerce API v1
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from pydantic import BaseModel, Field
from app.services import DatabaseService
from app.services import SearchService
from app.models import Product_Pydantic_List, Product_Pydantic


router = APIRouter(prefix="/products")


class PaginationQuery(BaseModel):
    limit: int = Field(default=10, ge=1)
    offset: int = Field(default=0, ge=0)


@router.get("/", response_model=Product_Pydantic_List)
async def get_products(
    pagination: PaginationQuery = Depends(),
    category: Optional[str] = Query(
        None, description="Filter products by category name"
    ),
    service: DatabaseService = Depends(DatabaseService),
):
    if category:
        return await service.get_products_by_category(category, pagination)
    else:
        return await service.get_all_products(pagination)



@router.get("/search", response_model=Product_Pydantic_List)
async def search_products(
    query: str = Query(..., description="Search query"),
    regex_search: bool = Query(False, description="Enable regex-based search"),
    size: int = Query(20, description="Number of results to return"),
    from_: int = Query(0, description="Number of results to skip"),
    service: SearchService = Depends(SearchService),
):
    return await service.search_products(query, size=size, from_=from_, regex_search=regex_search)

@router.get("/{product_id}", response_model=Product_Pydantic)
async def get_product(
    product_id: int, service: DatabaseService = Depends(DatabaseService)
):
    product = await service.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
