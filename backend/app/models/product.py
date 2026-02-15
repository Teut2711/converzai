from typing import TYPE_CHECKING
from tortoise import fields
from .base import TimestampMixin

if TYPE_CHECKING:
    from .dimensions import ProductDimensions
    from .image import ProductImage
    from .review import ProductReview
    from .tag import ProductTag


class Product(TimestampMixin):
    id = fields.IntField(pk=True)

    title = fields.CharField(max_length=255)
    description = fields.TextField()

    price = fields.DecimalField(max_digits=10, decimal_places=2, min_value=0, max_value=999999.99)
    discount_percentage = fields.DecimalField(
        max_digits=5, decimal_places=2, null=True, min_value=0, max_value=100
    )

    rating = fields.DecimalField(max_digits=3, decimal_places=2, min_value=0, max_value=5)
    stock = fields.IntField(min_value=0)

    sku = fields.CharField(max_length=64, unique=True, index=True)
    weight = fields.IntField(min_value=0)

    warranty_information = fields.CharField(max_length=255)
    shipping_information = fields.CharField(max_length=255)

    availability_status = fields.CharField(max_length=50)
    return_policy = fields.CharField(max_length=100)
    minimum_order_quantity = fields.IntField(min_value=1)

    category = fields.CharField(max_length=100)
    brand = fields.CharField(max_length=100, null=True)
    thumbnail= fields.CharField(max_length=255, null=True)

    barcode = fields.CharField(max_length=50, unique=True, null=True)
    qr_code = fields.CharField(max_length=500, null=True)

    tags: fields.ManyToManyRelation["ProductTag"]

    dimensions: fields.ReverseRelation["ProductDimensions"]
    images: fields.ReverseRelation["ProductImage"]
    reviews: fields.ReverseRelation["ProductReview"]

