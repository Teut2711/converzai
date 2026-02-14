from tortoise import fields
from tortoise.models import Model
from tortoise.contrib.pydantic import pydantic_queryset_creator, pydantic_model_creator
from typing import TYPE_CHECKING    
if TYPE_CHECKING:
    from .product import Product


class Category(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100, unique=True)
    products: fields.ReverseRelation["Product"]

Category_Pydantic_List = pydantic_queryset_creator(Category)
Category_Pydantic = pydantic_model_creator(Category)
