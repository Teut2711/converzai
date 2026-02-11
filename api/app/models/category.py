

from tortoise.models import Model
from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator, pydantic_queryset_creator




class Category(Model):
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


CategoryPydantic = pydantic_model_creator(Category)
CategoryPydanticList = pydantic_queryset_creator(Category)
