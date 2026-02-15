"""
Product utility functions
"""

from app.models import Product
from app.schemas import (
    ProductRead,
    ProductDimensionsCreate,
    ProductReviewCreate,
    ProductMetaCreate,
)


def map_product_to_read(product: Product) -> ProductRead:
    return ProductRead(
        id=product.id,
        title=product.title,
        description=product.description,
        category=product.category,
        price=float(product.price),
        discount_percentage=float(product.discount_percentage)
        if product.discount_percentage is not None
        else None,
        rating=float(product.rating),
        stock=product.stock,
        tags=[tag.name for tag in product.tags] if hasattr(product, "tags") else [],
        brand=product.brand,
        sku=product.sku,
        weight=product.weight,
        warranty_information=product.warranty_information,
        shipping_information=product.shipping_information,
        availability_status=product.availability_status,
        return_policy=product.return_policy,
        minimum_order_quantity=product.minimum_order_quantity,
        thumbnail=product.thumbnail,

        dimensions=ProductDimensionsCreate(
            width=product.dimensions.width,
            height=product.dimensions.height,
            depth=product.dimensions.depth,
        )
        if product.dimensions
        else None,

        reviews=[
            ProductReviewCreate(
                rating=r.rating,
                comment=r.comment,
                date=r.review_date.isoformat(),
                reviewer_name=r.reviewer_name,
                reviewer_email=r.reviewer_email,
            )
            for r in product.reviews
        ],

        images=[img.image_url for img in product.images],

        meta=ProductMetaCreate(
            created_at=product.created_at.isoformat(),
            updated_at=product.updated_at.isoformat(),
            barcode=product.barcode,
            qr_code=product.qr_code,
        ),
    )
