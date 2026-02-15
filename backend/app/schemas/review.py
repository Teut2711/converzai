"""
Review schemas for e-commerce API
"""

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from tortoise.contrib.pydantic import pydantic_queryset_creator, pydantic_model_creator
from app.models.review import Review


class ReviewRead(BaseModel):
    id: int
    rating: int
    comment: str
    reviewer_name: str
    reviewer_email: str
    review_date: str

    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
    )


Review_Pydantic_List = pydantic_queryset_creator(Review)
Review_Pydantic = pydantic_model_creator(Review)
