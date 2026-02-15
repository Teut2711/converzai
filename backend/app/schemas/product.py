from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from tortoise.contrib.pydantic import pydantic_queryset_creator, pydantic_model_creator
from app.models.product import Product

from .image import ProductImageRead, ProductImageCreate
from .review import ProductReviewRead, ProductReviewCreate
from .dimensions import ProductDimensionsRead, ProductDimensionsCreate
from .meta import ProductMetaRead, ProductMetaCreate


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
    dimensions: "ProductDimensionsCreate"
    warranty_information: str
    shipping_information: str
    availability_status: str
    reviews: List["ProductReviewCreate"]
    return_policy: str
    minimum_order_quantity: int
    images: List["ProductImageCreate"]
    thumbnail: str
    meta: Optional["ProductMetaCreate"] = None

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,  # Allow both camelCase and snake_case
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

    dimensions: "ProductDimensionsRead"
    warranty_information: str
    shipping_information: str
    availability_status: str

    reviews: List["ProductReviewRead"]
    return_policy: str
    minimum_order_quantity: int

    images: List["ProductImageRead"]
    thumbnail: Optional[str]
    meta: Optional["ProductMetaRead"]

    model_config = ConfigDict(
        alias_generator=to_camel,
        from_attributes=True,
    )


Product_Pydantic_List = pydantic_queryset_creator(Product)
Product_Pydantic = pydantic_model_creator(Product)
