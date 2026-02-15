from typing import List, Optional
from datetime import datetime
from tortoise.transactions import in_transaction
from pydantic import BaseModel
from app.models import (
    Product,
    ProductTag,
    ProductDimensions,
    ProductImage,
    ProductReview,
)
from app.schemas import (
    ProductCreate,
    ProductDimensionsCreate,
    ProductReviewCreate,
    ProductRead,
    Product_Pydantic_List,
)
from app.utils import get_logger, map_product_to_read

logger = get_logger(__name__)


class Pagination(BaseModel):
    """Pagination parameters for product queries"""

    offset: int = 0
    limit: int = 10


class DatabaseService:
    """
    Service responsible for all database operations related to products.
    Handles both read (queries) and write (create/update) operations.
    """

    def __init__(self):
        logger.info("DatabaseService initialized")

    async def save_products(self, products_data: List[ProductCreate]) -> None:
        logger.info(f"Saving {len(products_data)} products to database...")

        saved_count = 0
        saved_products = []

        for product_data in products_data:
            async with in_transaction(connection_name="default"):
                # Check if product already exists
                _id = product_data.id
                existing_product = await Product.get_or_none(id=_id)
                if existing_product:
                    logger.debug(f"Product with ID {_id} already exists, skipping")
                    continue

                # Skip products without category
                if not product_data.category:
                    logger.debug(
                        f"Product {product_data.title} has no category, skipping"
                    )
                    continue

                # Create product and related data
                product = await self._create_product(product_data)
                await self._add_tags_to_product(product, product_data.tags)
                await self._create_product_dimensions(product, product_data.dimensions)
                await self._create_product_images(
                    product,
                    product_data.images,
                )
                await self._create_product_reviews(
                    product,
                    product_data.reviews,
                )

            # Transaction successful - add to saved products
            saved_products.append(product)
            saved_count += 1

            if saved_count % 10 == 0:
                logger.info(f"Saved {saved_count} products...")

        logger.info(f"Successfully saved {saved_count} products to database")


    async def _create_product(self, product_data: ProductCreate) -> Product:
        """Create a product record from ProductCreate data"""
        return await Product.create(
            title=product_data.title,
            description=product_data.description,
            price=product_data.price,
            discount_percentage=product_data.discount_percentage,
            rating=product_data.rating,
            stock=product_data.stock,
            sku=product_data.sku,
            weight=product_data.weight,
            warranty_information=product_data.warranty_information,
            shipping_information=product_data.shipping_information,
            availability_status=product_data.availability_status,
            return_policy=product_data.return_policy,
            minimum_order_quantity=product_data.minimum_order_quantity,
            category=product_data.category,
            brand=product_data.brand,
            thumbnail=product_data.thumbnail,
            qr_code=product_data.meta.qr_code,
            barcode=product_data.meta.barcode,
        )

    async def _add_tags_to_product(self, product: Product, tags: List[str]) -> None:
        """Attach tags to a product (idempotent, M2M-safe)."""

        if not tags:
            return

        for raw_name in tags:
            tag_name = raw_name.strip().lower()

            if not tag_name:
                continue

            tag, _ = await ProductTag.get_or_create(name=tag_name)
            await product.tags.add(tag)

    async def _create_product_dimensions(
        self, product: Product, dimensions: ProductDimensionsCreate
    ):
        """Create product dimensions"""
        await ProductDimensions.create(
            width=dimensions.width,
            height=dimensions.height,
            depth=dimensions.depth,
            product=product,
        )

    async def _create_product_images(self, product: Product, images: List[str]):
        """Create product images"""
        for image_url in images:
            await ProductImage.create(image_url=image_url, product=product)

    async def _create_product_reviews(
        self, product: Product, reviews: List[ProductReviewCreate]
    ) -> None:
        """Create product reviews"""
        for review in reviews:
            try:
                await ProductReview.create(
                    rating=review.rating,
                    comment=review.comment,
                    reviewer_name=review.reviewer_name,
                    reviewer_email=review.reviewer_email,
                    review_date=review.date,
                    product=product,
                )
            except Exception as e:
                logger.error(f"Error creating review: {e}")
                logger.error(f"Review data: {review}")
                continue

    async def get_all_categories(self) -> List[str]:
        """
        Get all distinct product categories.

        Returns:
            List of category names
        """
        categories = await Product.all().distinct().values_list("category", flat=True)
        logger.info(f"Retrieved {len(categories)} categories")
        return categories

    async def get_all_products(
        self, pagination: Optional[Pagination] = None
    ) -> Product_Pydantic_List:
        query = (
            Product.all()
            .order_by("-created_at")
            .prefetch_related("tags", "dimensions", "images", "reviews")
        )

        if pagination:
            query = query.offset(pagination.offset).limit(pagination.limit)
            logger.info(
                f"Fetching products with pagination: offset={pagination.offset}, "
                f"limit={pagination.limit}"
            )
        else:
            logger.info("Fetching all products without pagination")

        products = await query
        total = await Product.all().count()

        return products, total

    async def get_products_by_category(
        self, category: str, pagination: Optional[Pagination] = None
    ) -> Product_Pydantic_List:
        query = (
            Product.filter(category=category)
            .order_by("-created_at")
            .prefetch_related("tags", "dimensions", "images", "reviews")
        )

        if pagination:
            query = query.offset(pagination.offset).limit(pagination.limit)
            logger.info(
                f"Fetching products in category '{category}' with pagination: "
                f"offset={pagination.offset}, limit={pagination.limit}"
            )
        else:
            logger.info(f"Fetching all products in category '{category}'")
        products = await query
        total = await Product.filter(category=category).count()
        logger.info(f"Retrieved products in category '{category}'")
        return products, total

    async def get_product_by_id(self, product_id: int) -> Optional[Product]:
        product = await Product.get_or_none(id=product_id).prefetch_related(
            "tags", "dimensions", "images", "reviews"
        )

        if not product:
            logger.warning(f"Product not found: {product_id}")
            return None

        logger.info(f"Retrieved product: {product_id} - {product.title}")
        return product

    async def get_products_by_ids(
        self, ids: List[int], pagination: Optional[Pagination] = None
    ) -> List[Product]:
        query = (
            Product.filter(id__in=ids)
            .order_by("-created_at")
            .prefetch_related("tags", "dimensions", "images", "reviews")
        )

        if pagination:
            query = query.offset(pagination.offset).limit(pagination.limit)
            logger.info(
                f"Fetching products with pagination: "
                f"offset={pagination.offset}, limit={pagination.limit}"
            )
        else:
            logger.info("Fetching all products")
        products = await query

        logger.info("Retrieved products by IDs")
        return products


def get_db_service() -> DatabaseService:
    return DatabaseService()
