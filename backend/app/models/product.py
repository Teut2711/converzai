from typing import TYPE_CHECKING, Optional, List
from tortoise import fields
from tortoise.contrib.pydantic import pydantic_queryset_creator, pydantic_model_creator
from pydantic import BaseModel, Field
from app.models.base import TimestampMixin
 
if TYPE_CHECKING:
    from app.models.dimensions import ProductDimensions
    from app.models.image import  ProductImage
    from app.models.review import  Review

class ProductDimensionsBase(BaseModel):
    width: float
    height: float
    depth: float

class ReviewBase(BaseModel):
    rating: int
    comment: str
    date: str
    reviewer_name: str = Field(alias="reviewerName")
    reviewer_email: str = Field(alias="reviewerEmail")

class ProductCreate(BaseModel):
    id: Optional[int] = None
    title: str
    description: str
    category: str
    price: float
    discount_percentage: Optional[float] = Field(default=None, alias="discountPercentage")
    rating: float
    stock: int
    tags: List[str]
    brand: Optional[str] = None
    sku: str
    weight: int
    dimensions: ProductDimensionsBase
    warranty_information: str = Field(alias="warrantyInformation")
    shipping_information: str = Field(alias="shippingInformation")
    availability_status: str = Field(alias="availabilityStatus")
    reviews: List[ReviewBase]
    return_policy: str = Field(alias="returnPolicy")
    minimum_order_quantity: int = Field(alias="minimumOrderQuantity")
    barcode: Optional[str] = None
    qr_code: Optional[str] = Field(alias="qrCode")
    images: List[str]
    thumbnail: str

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
