"""
Tag schemas for e-commerce API
"""

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from tortoise.contrib.pydantic import pydantic_queryset_creator, pydantic_model_creator
from app.models.tag import ProductTag


class ProductTagCreate(BaseModel):
    name: str
    
    model_config = ConfigDict(alias_generator=to_camel)


class ProductTagRead(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
    )


ProductTag_Pydantic_List = pydantic_queryset_creator(ProductTag)
ProductTag_Pydantic = pydantic_model_creator(ProductTag)
