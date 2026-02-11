from tortoise import fields
from app.models.base import TimestampMixin
from tortoise.contrib.pydantic import pydantic_queryset_creator, pydantic_model_creator
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from app.models.product import Product

class Tag(TimestampMixin):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, unique=True)

    products: fields.ManyToManyRelation["Product"]


Tag_Pydantic_List = pydantic_queryset_creator(Tag)
Tag_Pydantic = pydantic_model_creator(Tag)
