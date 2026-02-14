from typing import Optional, List
from pydantic import BaseModel, Field, computed_field
from .dimensions import ProductDimensionsBase
from .review import ProductReviewBase
from app.models import ProductDimensions,ProductDimensions_Pydantic
from app.models import ProductReview,ProductReview_Pydantic
from app.models import ProductImage

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
    reviews: List[ProductReviewBase]
    return_policy: str = Field(alias="returnPolicy")
    minimum_order_quantity: int = Field(alias="minimumOrderQuantity")
    barcode: Optional[str] = None
    images: List[str]
    thumbnail: str

class ProductGet(BaseModel):
    """Schema for product GET responses"""
    id: int
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
    
    @computed_field
    def dimensions(dimensions:ProductDimensions):
        return ProductDimensions_Pydantic.from_tortoise_orm(dimensions)

    @computed_field
    def reviews(reviews:List[ProductReview]):
        return [ProductReview_Pydantic.from_tortoise_orm(r) for r in reviews]
    
    warranty_information: str = Field(alias="warrantyInformation")
    shipping_information: str = Field(alias="shippingInformation")
    availability_status: str = Field(alias="availabilityStatus")
    return_policy: str = Field(alias="returnPolicy")
    minimum_order_quantity: int = Field(alias="minimumOrderQuantity")
    barcode: Optional[str] = None
    qr_code: Optional[str] = Field(alias="qrCode")
    
    @computed_field
    def images(images:List[ProductImage]):
        return [i.image_url for i in images]
    
    thumbnail: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None