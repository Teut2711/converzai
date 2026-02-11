"""
Category models for e-commerce API using Tortoise ORM
"""

from tortoise.models import Model
from tortoise import fields
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Category(Model):
    """Category database model using Tortoise ORM"""
    
    id = fields.IntField(pk=True, index=True)
    name = fields.CharField(max_length=100, unique=True, index=True)
    slug = fields.CharField(max_length=100, unique=True, index=True)
    description = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "categories"
        
    def __str__(self):
        return f"Category(id={self.id}, name='{self.name}')"

# Pydantic models for API
class CategoryBase(BaseModel):
    """Base category model"""
    name: str
    slug: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    """Category creation model"""
    pass

class CategoryResponse(CategoryBase):
    """Category response model"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
