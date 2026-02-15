"""
Image schemas for e-commerce API
"""

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from tortoise.contrib.pydantic import pydantic_queryset_creator, pydantic_model_creator
from app.models.image import ProductImage


class ProductImageRead(BaseModel):
    id: int
    image_url: str

    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
    )


ProductImage_Pydantic_List = pydantic_queryset_creator(ProductImage)
ProductImage_Pydantic = pydantic_model_creator(ProductImage)
