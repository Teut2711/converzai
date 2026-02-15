from typing import Optional, List
from tortoise import fields
from tortoise.contrib.pydantic import pydantic_queryset_creator, pydantic_model_creator
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from .base import TimestampMixin
 

from .dimensions import ProductDimensions
from .image import  ProductImage
from .review import  Review

class ProductDimensionsCreate(BaseModel):
    width: float
    height: float
    depth: float

class ProductReviewCreate(BaseModel):
    rating: int
    comment: str
    date: str
    reviewer_name: str
    reviewer_email: str
    
    model_config = ConfigDict(alias_generator=to_camel)

class ProductMetaCreate(BaseModel):
    created_at: str
    updated_at: str
    barcode: Optional[str] = None
    qr_code: Optional[str] = None
    
    model_config = ConfigDict(alias_generator=to_camel)

class ProductCreate(BaseModel):
    id: Optional[int] = None
    title: str
    description: str
    category: str
    price: float
    discount_percentage: Optional[float] = None
    rating: float
    stock: int
    tags: List[str]
    brand: Optional[str] = None
    sku: str
    weight: int
    dimensions: ProductDimensionsCreate
    warranty_information: str
    shipping_information: str
    availability_status: str
    reviews: List[ProductReviewCreate]
    return_policy: str
    minimum_order_quantity: int
    images: List[str]
    thumbnail: str
    meta: Optional[ProductMetaCreate] = None
    
    model_config = ConfigDict(alias_generator=to_camel)




class ProductDimensionsRead(BaseModel):
    width: float
    height: float
    depth: float

    model_config = ConfigDict(from_attributes=True)


class ProductReviewRead(BaseModel):
    rating: int
    comment: str
    date: str
    reviewer_name: str
    reviewer_email: str

    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
    )


class ProductMetaRead(BaseModel):
    created_at: str
    updated_at: str
    barcode: Optional[str]
    qr_code: Optional[str]

    model_config = ConfigDict(alias_generator=to_camel)
class ProductImageRead(BaseModel):
    id: int
    image_url: str

    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
    )


class ProductRead(BaseModel):
    id: int
    title: str
    description: str
    category: str
    price: float
    discount_percentage: Optional[float]
    rating: float
    stock: int
    tags: List[str]
    brand: Optional[str]
    sku: str
    weight: int

    dimensions: ProductDimensionsRead
    warranty_information: str
    shipping_information: str
    availability_status: str

    reviews: List[ProductReviewRead]
    return_policy: str
    minimum_order_quantity: int

    images: List[ProductImageRead]
    thumbnail: Optional[str]
    meta: ProductMetaRead

    model_config = ConfigDict(
        alias_generator=to_camel,
        from_attributes=True,
    )

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

    tags = fields.ManyToManyField(
        "models.Tag",
        related_name="products",
        through="product_tag",
    )

    dimensions: fields.ReverseRelation["ProductDimensions"]
    images: fields.ReverseRelation["ProductImage"]
    reviews: fields.ReverseRelation["Review"]


Product_Pydantic_List = pydantic_queryset_creator(Product)
Product_Pydantic = pydantic_model_creator(Product)
