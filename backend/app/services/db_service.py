from typing import List, Optional
from datetime import datetime
from tortoise.transactions import in_transaction
from pydantic import BaseModel
from app.models import (
    Product,
    Tag,
    ProductDimensions,
    ProductImage,
    Review,
    ProductMeta,
    ProductCreate,
    ProductDimensionsBase,
    ReviewBase,
    ProductMetaBase,
)
from app.models import Product_Pydantic, Product_Pydantic_List
from app.utils import get_logger

logger = get_logger(__name__)


class Pagination(BaseModel):
    """Pagination parameters for product queries"""
    offset: int = 0
    limit: int = 10


class DatabaseService:
    """
    Service responsible for all database operations related to products.
    Handles both read (queries) and write (create/update) operations.
    
    This is a singleton service - only one instance exists.
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._initialized = True
            logger.info("DatabaseService singleton initialized")

    async def save_products(self, products_data: List[ProductCreate]) -> List[Product]:
        """
        Save products to database from raw API data.
        
        Args:
            products_data: List of product dictionaries from API
            
        Returns:
            List of successfully saved Product instances
        """
        logger.info(f"Saving {len(products_data)} products to database...")

        saved_count = 0
        saved_products = []

        for product_data in products_data:
            try:
                async with in_transaction(connection_name="default"):
                    # Check if product already exists
                    sku = product_data.sku
                    existing_product = await Product.get_or_none(sku=sku)
                    if existing_product:
                        logger.debug(f"Product with SKU {sku} already exists, skipping")
                        continue

                    # Skip products without category
                    if not product_data.category:
                        logger.debug(f"Product {product_data.title} has no category, skipping")
                        continue

                    # Create product and related data
                    product = await self._create_product(product_data)
                    await self._add_tags_to_product(
                        product, product_data.tags
                    )
                    await self._create_product_dimensions(
                        product, product_data.dimensions
                    )
                    await self._create_product_images(
                        product,
                        product_data.images,
                        product_data.thumbnail,
                    )
                    await self._create_product_reviews(
                        product,
                        product_data.reviews,
                    )
                    await self._create_product_meta(
                        product, product_data.meta
                    )

                # Transaction successful - add to saved products
                saved_products.append(product)
                saved_count += 1

                if saved_count % 10 == 0:
                    logger.info(f"Saved {saved_count} products...")

            except Exception as e:
                logger.error(
                    f"Error saving product {product_data.title}: {e}"
                )
                # Automatic rollback happens here

        logger.info(f"Successfully saved {saved_count} products to database")

        # Prefetch related data for the saved products
        if saved_products:
            product_ids = [p.id for p in saved_products]
            saved_products = await Product.filter(id__in=product_ids).prefetch_related(
                "tags", "dimensions", "images", "reviews", "meta"
            )

        return saved_products

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
        )

    async def _add_tags_to_product(self, product: Product, tags: List[str]):
        """Add tags to a product"""
        for tag_name in tags:
            tag, _ = await Tag.get_or_create(
                name=tag_name, defaults={"slug": tag_name.lower().replace(" ", "-")}
            )
            await product.tags.add(tag)

    async def _create_product_dimensions(
        self, product: Product, dimensions: ProductDimensionsBase
    ):
        """Create product dimensions"""
        await ProductDimensions.create(
            width=dimensions.width,
            height=dimensions.height,
            depth=dimensions.depth,
            product=product,
        )

    async def _create_product_images(
        self, product: Product, images: List[str], thumbnail: str
    ):
        """Create product images"""
        for image_url in images:
            await ProductImage.create(
                image_url=image_url, is_thumbnail=False, product=product
            )

        # Handle thumbnail
        if thumbnail:
            await ProductImage.create(
                image_url=thumbnail, is_thumbnail=True, product=product
            )

    async def _create_product_reviews(
        self, product: Product, reviews: List[ReviewBase]
    ):
        """Create product reviews"""
        for review in reviews:
            await Review.create(
                rating=review.rating,
                comment=review.comment,
                reviewer_name=review.reviewer_name,
                reviewer_email=review.reviewer_email,
                review_date=datetime.fromisoformat(review.date.replace("Z", "+00:00")),
                product=product,
            )

    async def _create_product_meta(self, product: Product, meta: ProductMetaBase):
        """Create product metadata"""
        
        await ProductMeta.create(
            barcode=meta.barcode,
            qr_code_url=meta.qr_code_url,
            product=product,
        )
        return product
    # ============================================================================
    # READ OPERATIONS - Product Queries
    # ============================================================================

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
    ) -> List[Product_Pydantic_List]:
        """
        Get all products with optional pagination.
        
        Args:
            pagination: Optional pagination parameters
            
        Returns:
            List of Product_Pydantic_List instances
        """
        query = Product.all().order_by("-created_at").prefetch_related(
            "tags", "dimensions", "images", "reviews", "meta"
        )
        
        if pagination:
            query = query.offset(pagination.offset).limit(pagination.limit)
            logger.info(
                f"Fetching products with pagination: offset={pagination.offset}, "
                f"limit={pagination.limit}"
            )
        else:
            logger.info("Fetching all products without pagination")

        product_pydantics = await Product_Pydantic_List.from_queryset(query)
        logger.info(f"Retrieved {len(product_pydantics)} products")
        return product_pydantics

    async def get_products_by_category(
        self, category: str, pagination: Optional[Pagination] = None
    ) -> List[Product_Pydantic_List]:
        """
        Get products filtered by category with optional pagination.
        
        Args:
            category: Category name to filter by
            pagination: Optional pagination parameters
            
        Returns:
            List of Product_Pydantic_List instances in the category
        """
        query = Product.filter(category=category).order_by("-created_at").prefetch_related(
            "tags", "dimensions", "images", "reviews", "meta"
        )
        
        if pagination:
            query = query.offset(pagination.offset).limit(pagination.limit)
            logger.info(
                f"Fetching products in category '{category}' with pagination: "
                f"offset={pagination.offset}, limit={pagination.limit}"
            )
        else:
            logger.info(f"Fetching all products in category '{category}'")

        product_pydantics = await Product_Pydantic_List.from_queryset(query)
        logger.info(f"Retrieved {len(product_pydantics)} products in category '{category}'")
        return product_pydantics
    
    async def get_product_by_id(self, product_id: int) -> Optional[Product_Pydantic]:
        """
        Get a single product by ID.
        
        Args:
            product_id: ID of the product to retrieve
            
        Returns:
            Product_Pydantic instance if found, None otherwise
        """
        product = await Product.get_or_none(id=product_id).prefetch_related(
            "tags", "dimensions", "images", "reviews", "meta"
        )
        
        if not product:
            logger.warning(f"Product not found: {product_id}")
            return None
            
        product_pydantic = await Product_Pydantic.from_tortoise_orm(product)
        logger.info(f"Retrieved product: {product_id} - {product.title}")
        return product_pydantic

    async def get_product_count(self, category: Optional[str] = None) -> int:
        """
        Get total count of products, optionally filtered by category.
        
        Args:
            category: Optional category to filter by
            
        Returns:
            Total count of products
        """
        if category:
            count = await Product.filter(category=category).count()
            logger.info(f"Product count in category '{category}': {count}")
        else:
            count = await Product.all().count()
            logger.info(f"Total product count: {count}")
        
        return count

    # ============================================================================
    # HELPER METHODS - For Indexing and Relations
    # ============================================================================

    async def get_product_with_relations(self, product_id: int) -> Product:
        """
        Get a product with all its related data prefetched.
        
        Args:
            product_id: ID of the product
            
        Returns:
            Product instance with related data loaded
        """
        return await Product.get(id=product_id).prefetch_related(
            "tags", "dimensions", "images", "reviews", "meta"
        )

    async def get_products_with_relations(
        self, product_ids: List[int]
    ) -> List[Product]:
        """
        Get multiple products with all related data prefetched.
        
        Args:
            product_ids: List of product IDs
            
        Returns:
            List of Product instances with related data loaded
        """
        return await Product.filter(id__in=product_ids).prefetch_related(
            "tags", "dimensions", "images", "reviews", "meta"
        )