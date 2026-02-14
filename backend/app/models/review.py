from tortoise import fields
from .base import TimestampMixin
from tortoise.contrib.pydantic import pydantic_queryset_creator, pydantic_model_creator
from tortoise.models import Model


class Review(Model):
    id = fields.IntField(pk=True)

    rating = fields.IntField()
    comment = fields.TextField()

    reviewer_name = fields.CharField(max_length=100)
    reviewer_email = fields.CharField(max_length=255)

    review_date = fields.DatetimeField()

    product = fields.ForeignKeyField(
        "models.Product",
        related_name="reviews",
        on_delete=fields.CASCADE,
    )

    class Meta:
        indexes = [("product_id", "rating")]

Review_Pydantic_List = pydantic_queryset_creator(Review)
Review_Pydantic = pydantic_model_creator(Review)
