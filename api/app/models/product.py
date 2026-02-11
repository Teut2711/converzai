from typing import TYPE_CHECKING
from tortoise import fields
from app.models.base import TimestampMixin
from tortoise.contrib.pydantic import pydantic_queryset_creator, pydantic_model_creator
if TYPE_CHECKING:
    from app.models.dimensions import ProductDimensions
    from app.models.image import  ProductImage
    from app.models.review import  Review
    from app.models.meta import ProductMeta

class Product(TimestampMixin):
    id = fields.IntField(pk=True)

    title = fields.CharField(max_length=255)
    description = fields.TextField()

    price = fields.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = fields.DecimalField(
        max_digits=5, decimal_places=2, null=True
    )

    rating = fields.DecimalField(max_digits=3, decimal_places=2)
    stock = fields.IntField()

    sku = fields.CharField(max_length=64, unique=True, index=True)
    weight = fields.IntField()

    warranty_information = fields.CharField(max_length=255)
    shipping_information = fields.CharField(max_length=255)

    availability_status = fields.CharField(max_length=50)
    return_policy = fields.CharField(max_length=100)
    minimum_order_quantity = fields.IntField()

    category = fields.ForeignKeyField(
        "models.Category",
        related_name="products",
        on_delete=fields.RESTRICT,
    )

    brand = fields.ForeignKeyField(
        "models.Brand",
        related_name="products",
        on_delete=fields.RESTRICT,
    )

    tags = fields.ManyToManyField(
        "models.Tag",
        related_name="products",
        through="product_tag",
    )

    dimensions: fields.ReverseRelation["ProductDimensions"]
    images: fields.ReverseRelation["ProductImage"]
    reviews: fields.ReverseRelation["Review"]
    meta: fields.ReverseRelation["ProductMeta"]



Product_Pydantic_List = pydantic_queryset_creator(Product)
Product_Pydantic = pydantic_model_creator(Product)