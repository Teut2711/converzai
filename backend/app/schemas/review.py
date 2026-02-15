"""
Review schemas for e-commerce API
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr
from pydantic.alias_generators import to_camel, to_snake
from tortoise.contrib.pydantic import pydantic_queryset_creator, pydantic_model_creator
from app.models.review import ProductReview
 

class ProductReviewCreate(BaseModel):
    rating: int
    comment: str
    date: datetime
    reviewer_name: str
    reviewer_email: EmailStr
    
    model_config = ConfigDict(
        alias_generator=to_camel,
        
        
        )


class ProductReviewRead(BaseModel):
    rating: int
    comment: str
    review_date: datetime
    reviewer_name: str
    reviewer_email: EmailStr

    model_config = ConfigDict(
        alias_generator=to_snake,
         
    )

 
ProductReview_Pydantic_List = pydantic_queryset_creator(ProductReview)
ProductReview_Pydantic = pydantic_model_creator(ProductReview)
