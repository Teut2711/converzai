"""
Product utility functions
"""

from app.models import Product
from app.schemas import (
    ProductRead,
    ProductDimensionsRead,
    ProductMetaRead,
)
from backend.app.schemas.product import ProductReviewRead
 


def map_product_to_read(product: Product) -> ProductRead:

    

    
    return ProductRead(
        id=product.id,
        title=product.title,
        description=product.description,
        category=product.category,
        price=product.price,
        discount_percentage=product.discount_percentage,
        rating=product.rating,
        stock=product.stock,
        tags=[tag.name for tag in (product.tags or [])],
        brand=product.brand,
        sku=product.sku,
        weight=product.weight,
        warranty_information=product.warranty_information,
        shipping_information=product.shipping_information,
        availability_status=product.availability_status,
        return_policy=product.return_policy,
        minimum_order_quantity=product.minimum_order_quantity,
        thumbnail=product.thumbnail,
        dimensions=ProductDimensionsRead(
            width=product.dimensions.width,
            height=product.dimensions.height,
            depth=product.dimensions.depth,
        ),
        reviews=ProductReviewRead(
            rating=product.reviews.rating,
            comment=product.reviews.comment,
            date=product.reviews.date,
            reviewer_name=product.reviews.reviewer_name,
            reviewer_email=product.reviews.reviewer_email,
        ),
        images=[i.image_url for i in product.images],
        meta=ProductMetaRead(
            created_at=product.created_at.isoformat(),
            updated_at=product.updated_at.isoformat(),
            barcode=product.barcode,
            qr_code=product.qr_code,
        ),
    )
