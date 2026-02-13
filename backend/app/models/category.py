from tortoise import fields
from app.models.base import TimestampMixin
from tortoise.contrib.pydantic import pydantic_queryset_creator, pydantic_model_creator

class Category(TimestampMixin):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100, unique=True)
    slug = fields.CharField(max_length=120, unique=True)
    description = fields.TextField(null=True)
    is_active = fields.BooleanField(default=True)


Category_Pydantic_List = pydantic_queryset_creator(Category)
Category_Pydantic = pydantic_model_creator(Category)
