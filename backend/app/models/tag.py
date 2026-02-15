from tortoise import fields
from typing import TYPE_CHECKING
from tortoise import models

if TYPE_CHECKING:
    from app.models.product import Product

class ProductTag(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, unique=True)

    products: fields.ManyToManyRelation["Product"] = fields.ManyToManyField(
        "models.Product",
        related_name="tags",
        through="product_product_tag",
    )