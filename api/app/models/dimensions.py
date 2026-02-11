from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_queryset_creator, pydantic_model_creator

class ProductDimensions(models.Model):
    id = fields.IntField(pk=True)

    width = fields.FloatField()
    height = fields.FloatField()
    depth = fields.FloatField()

    product = fields.OneToOneField(
        "models.Product",
        related_name="dimensions",
        on_delete=fields.CASCADE,
    )

ProductDimensions_Pydantic_List = pydantic_queryset_creator(ProductDimensions)
ProductDimensions_Pydantic = pydantic_model_creator(ProductDimensions)
