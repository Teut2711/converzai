from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from tortoise.contrib.pydantic import pydantic_queryset_creator, pydantic_model_creator
from app.models.product import Product


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

Product_Pydantic_List = pydantic_queryset_creator(Product)
Product_Pydantic = pydantic_model_creator(Product)
