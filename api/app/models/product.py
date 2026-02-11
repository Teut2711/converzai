"""
Product models for e-commerce API using Tortoise ORM
"""

from tortoise.models import Model
from tortoise import fields
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class Product(Model):
    """Product database model using Tortoise ORM"""
    
    id = fields.IntField(pk=True, index=True)
    title = fields.CharField(max_length=255, index=True)
    description = fields.TextField(null=True)
    price = fields.FloatField()
    discount_percentage = fields.FloatField(default=0.0)
    brand = fields.CharField(max_length=100, null=True, index=True)
    category_id = fields.IntField(null=True, index=True)
    availability_status = fields.CharField(max_length=20, default="in_stock", index=True)
    rating = fields.FloatField(default=0.0)
    stock_quantity = fields.IntField(default=0)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    # Relationships
    category = fields.ForeignKeyField('models.Category', related_name='products', null=True)
    
    class Meta:
        table = "products"
    
    @property
    def final_price(self) -> float:
        """Calculate final price after discount"""
        if self.discount_percentage > 0:
            return round(self.price * (1 - self.discount_percentage / 100), 2)
        return self.price
    
    def __str__(self):
        return f"Product(id={self.id}, title='{self.title}', price={self.price})"

# Pydantic models for API
class ProductBase(BaseModel):
    """Base product model"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    discount_percentage: float = Field(default=0.0, ge=0, le=100)
    brand: Optional[str] = Field(None, max_length=100)
    category_id: Optional[int] = None
    availability_status: str = Field(default="in_stock", max_length=20)
    rating: float = Field(default=0.0, ge=0, le=5)
    stock_quantity: int = Field(default=0, ge=0)

class ProductCreate(ProductBase):
    """Product creation model"""
    pass

class ProductResponse(ProductBase):
    """Product response model"""
    id: int
    final_price: float
    created_at: datetime
    updated_at: datetime
    category: Optional[str] = None
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm(cls, obj):
        """Create response model from ORM object"""
        if obj is None:
            return None
        data = cls.from_attributes(obj)
        if hasattr(obj, 'category') and obj.category:
            data.category = obj.category.name
        return data
