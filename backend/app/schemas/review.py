"""
Review schemas for e-commerce API
"""

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from tortoise.contrib.pydantic import pydantic_queryset_creator, pydantic_model_creator
from app.models.review import ProductReview



class ProductReviewCreate(BaseModel):
    rating: int
    comment: str
    date: str
    reviewer_name: str
    reviewer_email: str
    
    model_config = ConfigDict(alias_generator=to_camel)


class ProductReviewRead(BaseModel):
    rating: int
    comment: str
    date: str
    reviewer_name: str
    reviewer_email: str

    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
    )



ProductReview_Pydantic_List = pydantic_queryset_creator(ProductReview)
ProductReview_Pydantic = pydantic_model_creator(ProductReview)
