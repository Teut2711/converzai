"""
Product utility functions
"""

from app.models import Product
from app.schemas import (
    ProductRead,
    ProductDimensionsRead,
    ProductMetaRead,
    ProductReviewRead,
)


def _map_dimensions(product: Product) -> ProductDimensionsRead:
    """Map product dimensions to schema."""
    return ProductDimensionsRead(
        width=product.dimensions.width,
        height=product.dimensions.height,
        depth=product.dimensions.depth,
    )


def _map_reviews(product: Product) -> list[ProductReviewRead]:
    """Map product reviews to schema list."""
    return [
        ProductReviewRead(
            rating=review.rating,
            comment=review.comment,
            date=review.date,
            reviewer_name=review.reviewer_name,
            reviewer_email=review.reviewer_email,
        ) for review in product.reviews
    ]


def _map_meta(product: Product) -> ProductMetaRead:
    """Map product metadata to schema."""
    return ProductMetaRead(
        created_at=product.created_at.isoformat(),
        updated_at=product.updated_at.isoformat(),
        barcode=product.barcode,
        qr_code=product.qr_code,
    )


def map_product_to_read(product: Product) -> ProductRead:
    """Map a Product ORM model to ProductRead schema."""
    
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
        dimensions=_map_dimensions(product),
        reviews=_map_reviews(product),
        images=[i.image_url for i in product.images],
        meta=_map_meta(product),
    )
