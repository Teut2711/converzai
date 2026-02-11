
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class ProductBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    price: float
    discount_percentage: float = 0.0
    brand: Optional[str] = Field(None, max_length=100)
    availability_status: str = "in_stock"
    rating: float = 0.0
    stock_quantity: int = 0
    category_id: Optional[int] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    price: Optional[float] = None
    discount_percentage: Optional[float] = None
    brand: Optional[str] = None
    availability_status: Optional[str] = None
    rating: Optional[float] = None
    stock_quantity: Optional[int] = None
    category_id: Optional[int] = None

class ProductOut(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime
    final_price: float
    category_name: Optional[str]

    model_config = ConfigDict(from_attributes=True)
