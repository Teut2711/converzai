"""
Product views for e-commerce API v1
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List
from pydantic import BaseModel, Field
from app.services import get_db_service, get_search_service, DatabaseService, SearchService
from app.schemas import ProductRead, Product_Pydantic_List
from app.utils import map_product_to_read

router = APIRouter(prefix="/products")


class PaginationQuery(BaseModel):
    limit: int = Field(default=10, ge=1)
    offset: int = Field(default=0, ge=0)


class PaginatedProductsResponse(BaseModel):
    products: List[ProductRead]
    total: int
    limit: int
    offset: int


@router.get("/", response_model=PaginatedProductsResponse)
async def get_products(
    pagination: PaginationQuery = Depends(),
    category: Optional[str] = Query(
        None, description="Filter products by category name"
    ),
    service: DatabaseService = Depends(get_db_service),
):
    if category:
        products, total = await service.get_products_by_category(category, pagination)
    else:
        products,total = await service.get_all_products(pagination)
    return PaginatedProductsResponse(
        products=[ map_product_to_read(product) for product in products],
        total=total,
        limit=pagination.limit,
        offset=pagination.offset
    )


@router.get("/search", response_model=List[ProductRead])
async def search_products(
    query: str = Query(..., description="Search query", min_length=3),
    use_wildcard: bool = Query(False, description="Enable wildcard-based search"),
    size: int = Query(20, description="Number of results to return"),
    service: SearchService = Depends(get_search_service),
):
    products = await service.search_products(query, size=size, regex_search=use_wildcard)
    return [map_product_to_read(product) for product in products]

@router.get("/{product_id}", response_model=ProductRead)
async def get_product(
    product_id: int, service: DatabaseService = Depends(get_db_service)
):
    product = await service.get_product_by_id(product_id)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return map_product_to_read(product)
    
    