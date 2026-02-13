from tortoise import fields, models
from  tortoise.contrib.pydantic import pydantic_queryset_creator, pydantic_model_creator
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.product import Product


class Brand(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100, unique=True)
    products: fields.ReverseRelation["Product"]


Brand_Pydantic_List = pydantic_queryset_creator(Brand)
Brand_Pydantic = pydantic_model_creator(Brand)
