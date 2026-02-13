"""
Query models for API endpoints using Pydantic BaseModel
"""

from pydantic import BaseModel, Field
from typing import Optional


class ProductQuery(BaseModel):
    """Query parameters for product listing"""
    category: Optional[str] = Field(None, description="Filter by category name")
    limit: int = Field(10, ge=1, le=100, description="Number of products to return")
    offset: int = Field(0, ge=0, description="Number of products to skip")
    
    model_config = {"extra": "forbid"}


class ProductSearchQuery(BaseModel):
    """Query parameters for product search"""
    query: str = Field(..., min_length=1, description="Search query")
    
    model_config = {"extra": "forbid"}


class ProductCategoryQuery(BaseModel):
    """Query parameters for category filtering"""
    category_name: str = Field(..., min_length=1, description="Category name")
    
    model_config = {"extra": "forbid"}


class PaginationQuery(BaseModel):
    """Base pagination query parameters"""
    limit: int = Field(10, ge=1, le=100, description="Number of items to return")
    offset: int = Field(0, ge=0, description="Number of items to skip")
    
    model_config = {"extra": "forbid"}
