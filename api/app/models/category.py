

from tortoise.models import Model
from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise import Tortoise

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

Tortoise.init_models(["app.models.product", "app.models.category"], "models")

CategoryPydantic = pydantic_model_creator(Category, name="Category")
CategoryInPydantic = pydantic_model_creator(Category, name="CategoryIn", exclude_readonly=True)
