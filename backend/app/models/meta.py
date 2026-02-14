from tortoise import fields
from tortoise.contrib.pydantic import pydantic_queryset_creator, pydantic_model_creator
from app.models.base import TimestampMixin

class ProductMeta(TimestampMixin):
    id = fields.IntField(pk=True)

    barcode = fields.CharField(max_length=50, unique=True)
    qr_code_url = fields.CharField(max_length=500)

    product = fields.OneToOneField(
        "models.Product",
        related_name="meta",
        on_delete=fields.CASCADE,
    )

ProductMeta_Pydantic_List = pydantic_queryset_creator(ProductMeta)
ProductMeta_Pydantic = pydantic_model_creator(ProductMeta)
