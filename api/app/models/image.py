from tortoise import fields, models

class ProductImage(models.Model):
    id = fields.IntField(pk=True)

    image_url = fields.CharField(max_length=500)
    is_thumbnail = fields.BooleanField(default=False)

    product = fields.ForeignKeyField(
        "models.Product",
        related_name="images",
        on_delete=fields.CASCADE,
    )
