from tortoise import fields
from tortoise.models import Model


class ProductReview(Model):
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
