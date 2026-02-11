from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_queryset_creator, pydantic_model_creator

class ProductImage(models.Model):
    id = fields.IntField(pk=True)

    image_url = fields.CharField(max_length=500)
    is_thumbnail = fields.BooleanField(default=False)

    product = fields.ForeignKeyField(
        "models.Product",
        related_name="images",
        on_delete=fields.CASCADE,
    )

ProductImage_Pydantic_List = pydantic_queryset_creator(ProductImage)
ProductImage_Pydantic = pydantic_model_creator(ProductImage)