from pydantic import BaseModel, Field
from typing import Optional

class CategoryFilter(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    slug: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None

class ProductFilter(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    price_min: Optional[float] = Field(None, ge=0)
    price_max: Optional[float] = Field(None, ge=0)
    brand: Optional[str] = Field(None, min_length=1, max_length=100)
    availability_status: Optional[str] = Field(None, pattern="^(in_stock|out_of_stock)$")
    rating_min: Optional[float] = Field(None, ge=0, le=5)
    rating_max: Optional[float] = Field(None, ge=0, le=5)
    stock_quantity_min: Optional[int] = Field(None, ge=0)
    category_id: Optional[int] = Field(None, ge=1)
