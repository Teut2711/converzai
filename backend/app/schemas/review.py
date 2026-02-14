from pydantic import BaseModel, Field

class ProductReviewBase(BaseModel):
    rating: int
    comment: str
    date: str
    reviewer_name: str = Field(alias="reviewerName")
    reviewer_email: str = Field(alias="reviewerEmail")

