"""
Product models for e-commerce API using Tortoise ORM
"""

from tortoise.models import Model
from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator, pydantic_queryset_creator
from tortoise.exceptions import NoValuesFetched
from typing import Optional
from pydantic import BaseModel


class Product(Model):
    id = fields.IntField(pk=True, index=True)
    title = fields.CharField(max_length=255, index=True)
    description = fields.TextField(null=True)
    price = fields.FloatField()
    discount_percentage = fields.FloatField(default=0.0)
    brand = fields.CharField(max_length=100, null=True, index=True)
    category_id = fields.IntField(null=True, index=True)
    availability_status = fields.CharField(max_length=20, default="in_stock", index=True)
    rating = fields.FloatField(default=0.0)
    stock_quantity = fields.IntField(default=0)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    category = fields.ForeignKeyField('models.Category', related_name='products', null=True)
    
    class Meta:
        table = "products"
    
    @property
    def final_price(self) -> float:
        if self.discount_percentage > 0:
            return round(self.price * (1 - self.discount_percentage / 100), 2)
        return self.price
    
    @property
    def category_name(self) -> Optional[str]:
        try:
            if self.category:
                return self.category.name
            return None
        except (NoValuesFetched, AttributeError):
            return None
    
    class PydanticMeta:
        computed = ("final_price", "category_name")
        exclude = ("category",)



ProductPydantic = pydantic_model_creator(Product)
Product_Pydantic_List = pydantic_queryset_creator(Product)


