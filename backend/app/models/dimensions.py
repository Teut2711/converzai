from tortoise import fields, models

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
