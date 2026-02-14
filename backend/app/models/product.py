from typing import TYPE_CHECKING, Optional, Dict, List, Any
from tortoise import fields
from tortoise.exceptions import NoValuesFetched
from app.models.base import TimestampMixin
from tortoise.contrib.pydantic import pydantic_queryset_creator, pydantic_model_creator
if TYPE_CHECKING:
    from app.models.dimensions import ProductDimensions
    from app.models.image import  ProductImage
    from app.models.review import  Review
    from app.models.meta import ProductMeta

    
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

    tags = fields.ManyToManyField(
        "models.Tag",
        related_name="products",
        through="product_tag",
    )

    dimensions: fields.ReverseRelation["ProductDimensions"]
    images: fields.ReverseRelation["ProductImage"]
    reviews: fields.ReverseRelation["Review"]
    meta: fields.ReverseRelation["ProductMeta"]

    def category_name(self) -> str:
        return self.category or ""

    def brand_name(self) -> str:
        return self.brand or ""

    def tag_names(self) -> List[str]:
        try:
            return [tag.name for tag in self.tags] if self.tags else []
        except (NoValuesFetched, AttributeError):
            return []

    def dimensions_data(self) -> Optional[Dict[str, float]]:
        try:
            if self.dimensions:
                return {
                    "width": self.dimensions.width,
                    "height": self.dimensions.height,
                    "depth": self.dimensions.depth,
                }
            return None
        except (NoValuesFetched, AttributeError):
            return None

    def image_urls(self) -> List[str]:
        try:
            return [img.image_url for img in self.images] if self.images else []
        except (NoValuesFetched, AttributeError):
            return []

    def reviews_data(self) -> List[Dict[str, Any]]:
        try:
            if self.reviews:
                return [
                    {
                        "rating": r.rating,
                        "comment": r.comment,
                        "reviewer_name": r.reviewer_name,
                        "reviewer_email": r.reviewer_email,
                        "review_date": r.review_date.isoformat() if r.review_date else None,
                    }
                    for r in self.reviews
                ]
            return []
        except (NoValuesFetched, AttributeError):
            return []

    def meta_data(self) -> Optional[Dict[str, str]]:
        try:
            if self.meta:
                return {
                    "barcode": self.meta.barcode,
                    "qr_code_url": self.meta.qr_code_url,
                }
            return None
        except (NoValuesFetched, AttributeError):
            return None

    class PydanticMeta:
        computed = ("category_name", "brand_name", "tag_names", "dimensions_data", "image_urls", "reviews_data", "meta_data")
        exclude = ("created_at", "updated_at")


Product_Pydantic_List = pydantic_queryset_creator(Product)
Product_Pydantic = pydantic_model_creator(Product)
