"""
Dimensions schemas for e-commerce API
"""

from typing import List
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from tortoise.contrib.pydantic import pydantic_queryset_creator, pydantic_model_creator
from app.models.dimensions import ProductDimensions

class ProductDimensionsCreate(BaseModel):
    width: float
    height: float
    depth: float




class ProductDimensionsRead(BaseModel):
    width: float
    height: float
    depth: float

    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
    )


ProductDimensions_Pydantic_List = pydantic_queryset_creator(ProductDimensions)
ProductDimensions_Pydantic = pydantic_model_creator(ProductDimensions)
