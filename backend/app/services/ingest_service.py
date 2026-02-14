import httpx
from app.settings import settings
from app.utils import get_logger
from app.models import (
    Product,
    Category,
    Brand,
    Tag,
    ProductDimensions,
    ProductImage,
    Review,
    ProductMeta,
)
from datetime import datetime
from tortoise.transactions import in_transaction
from app.models import Product_Pydantic
logger = get_logger(__name__)


class DataIngestionService:

    def __init__(self):
        from . import IndexingService

        self.products_url = settings.PRODUCT_API_URL
        self.client = httpx.AsyncClient(timeout=30.0)
        self.indexing_service = IndexingService()
        logger.info(f"DataIngestionService initialized with URL: {self.products_url}")

    async def load_seed_data(self):
        """Load seed data from API and save to database"""
        logger.info("Starting seed data loading...")

        # Get first page to determine total
        first_response = await self.client.get(
            f"{self.products_url}?limit={settings.PRODUCT_API_URL_LIMIT}&skip=0"
        )
        first_response.raise_for_status()
        first_data = first_response.json()

        if not first_data.get("products"):
            logger.warning("No products found in API response")
            return

        total_products = first_data.get("total", len(first_data["products"]))
        logger.info(f"Total products to fetch: {total_products}")

        # Fetch all products using pagination
        all_products = []
        skip = 0
        limit = settings.PRODUCT_API_URL_LIMIT

        while skip < total_products:
            params = {"limit": limit, "skip": skip}
            response = await self.client.get(self.products_url, params=params)
            response.raise_for_status()
            data = response.json()

            products = data.get("products", [])
            if not products:
                break

            all_products.extend(products)
            skip += len(products)

            logger.info(f"Fetched {len(all_products)} products so far...")

            if len(products) < limit:
                break

        logger.info(f"Successfully fetched {len(all_products)} products")

        # Save products to database
        await self.save_products_to_db(all_products)

        logger.info("Seed data loading completed successfully")

    async def save_products_to_db(self, products):
        """Save products to database using models - orchestrates data creation"""
        logger.info(f"Saving {len(products)} products to database...")

        saved_count = 0
        saved_products = []  # Collect successfully saved products for indexing

        for product_data in products:
            try:
                async with in_transaction(connection_name="default"):
                    # Get or create category
                    category = await self._create_or_get_category(
                        product_data.get("category")
                    )
                    if not category:
                        continue

                    # Get or create brand
                    brand = await self._create_or_get_brand(
                        product_data.get("brand")
                    )
                    if not brand:
                        continue

                    sku = product_data.get("sku")
                    existing_product = await Product.get_or_none(
                        sku=sku
                    )
                    if existing_product:
                        continue

                    # Create product
                    product = await self._create_product(
                        product_data, category, brand
                    )

                    # Related data
                    await self._add_tags_to_product(
                        product, product_data.get("tags", [])
                    )
                    await self._create_product_dimensions(
                        product, product_data.get("dimensions", {})
                    )
                    await self._create_product_images(
                        product,
                        product_data.get("images", []),
                        product_data.get("thumbnail"),
                    )
                    await self._create_product_reviews(
                        product,
                        product_data.get("reviews", []),
                    )
                    await self._create_product_meta(
                        product, product_data.get("meta", {})
                    )

                # Transaction successful - collect product for indexing
                saved_products.append(product)
                saved_count += 1

                if saved_count % 10 == 0:
                    logger.info(f"Saved {saved_count} products...")

            except Exception as e:
                logger.error(
                    f"Error saving product {product_data.get('title')}: {e}"
                )
                # automatic rollback happens here

        logger.info(f"Successfully saved {saved_count} products")

        # Index saved products in Elasticsearch
        if saved_products:
            await self._index_saved_products(saved_products)

    async def _index_saved_products(self, products):
        """Index saved products in Elasticsearch"""
        logger.info(f"Indexing {len(products)} products in Elasticsearch...")
        
        # Convert Product instances to Pydantic models
        pydantic_products = []
        
        for product in products:
            try:
                # Prefetch related data for computed fields
                await product.fetch_related("category", "brand", "tags", "dimensions", "images", "reviews", "meta")
                
                product_pydantic = await Product_Pydantic.from_tortoise_orm(product)
                pydantic_products.append(product_pydantic)
            except Exception as e:
                logger.error(f"Error converting product {product.id} to Pydantic: {e}")
                continue
        
        if pydantic_products:
            # Bulk index the products
            indexed_count = await self.indexing_service.bulk_index_products(pydantic_products)
            logger.info(f"Successfully indexed {indexed_count}/{len(pydantic_products)} products in Elasticsearch")
        else:
            logger.warning("No products to index")

    async def _create_or_get_category(self, category_name):
        if not category_name:
            return None

        category, _ = await Category.get_or_create(
            name=category_name, defaults={"slug": category_name.lower().replace(" ", "-")}
        )
        return category

    async def _create_or_get_brand(self, brand_name):
        if not brand_name:
            return None

        brand, _ = await Brand.get_or_create(
            name=brand_name, defaults={"slug": brand_name.lower().replace(" ", "-")}
        )
        return brand

    async def _create_product(self, product_data, category, brand):
        return await Product.create(
            title=product_data.get("title", ""),
            description=product_data.get("description", ""),
            price=float(product_data.get("price", 0)),
            discount_percentage=float(product_data.get("discountPercentage", 0)),
            rating=float(product_data.get("rating", 0)),
            stock=product_data.get("stock", 0),
            sku=product_data.get("sku", ""),
            weight=product_data.get("weight", 0),
            warranty_information=product_data.get("warrantyInformation", ""),
            shipping_information=product_data.get("shippingInformation", ""),
            availability_status=product_data.get("availabilityStatus", "in_stock"),
            return_policy=product_data.get("returnPolicy", ""),
            minimum_order_quantity=product_data.get("minimumOrderQuantity", 1),
            category=category,
            brand=brand,
        )

    async def _add_tags_to_product(self, product, tags):
        for tag_name in tags:
            tag, _ = await Tag.get_or_create(
                name=tag_name, defaults={"slug": tag_name.lower().replace(" ", "-")}
            )
            await product.tags.add(tag)

    async def _create_product_dimensions(self, product, dimensions_data):
        if dimensions_data:
            await ProductDimensions.create(
                width=float(dimensions_data.get("width", 0)),
                height=float(dimensions_data.get("height", 0)),
                depth=float(dimensions_data.get("depth", 0)),
                product=product,
            )

    async def _create_product_images(self, product, images, thumbnail):
        for image_url in images:
            await ProductImage.create(
                image_url=image_url, is_thumbnail=False, product=product
            )

        # Handle thumbnail
        if thumbnail:
            await ProductImage.create(
                image_url=thumbnail, is_thumbnail=True, product=product
            )

    async def _create_product_reviews(self, product, reviews):
        for review_data in reviews:
            await Review.create(
                rating=int(review_data.get("rating", 0)),
                comment=review_data.get("comment", ""),
                reviewer_name=review_data.get("reviewerName", ""),
                reviewer_email=review_data.get("reviewerEmail", ""),
                review_date=datetime.fromisoformat(
                    review_data.get("date", "").replace("Z", "+00:00")
                ),
                product=product,
            )

    async def _create_product_meta(self, product, meta_data):
        if meta_data:
            await ProductMeta.create(
                barcode=meta_data.get("barcode", ""),
                qr_code_url=meta_data.get("qrCode", ""),
                product=product,
            )

    async def close(self):
        """Close HTTP connections"""
        logger.info("Closing data ingestion service connections")
        await self.client.aclose()


 
