import httpx
from app.config.settings import settings
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

logger = get_logger(__name__)


async def load_seed_data():
    """Load seed data from API and save to database"""
    logger.info("Starting seed data loading...")

    async with httpx.AsyncClient(timeout=30.0) as client:
        logger.info("Fetching product count...")

        # Get first page to determine total
        first_response = await client.get(
            f"{settings.PRODUCT_API_URL}?limit={settings.PRODUCT_API_URL_LIMIT}&skip=0"
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
            response = await client.get(settings.PRODUCT_API_URL, params=params)
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
        await save_products_to_db(all_products)

        logger.info("Seed data loading completed successfully")


async def save_products_to_db(products):
    logger.info(f"Saving {len(products)} products to database...")

    saved_count = 0

    for product_data in products:
        try:
            async with in_transaction(connection_name="default"):
                # Get or create category
                category = await create_or_get_category(
                    product_data.get("category")
                )
                if not category:
                    continue

                # Get or create brand
                brand = await create_or_get_brand(
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
                product = await create_product(
                    product_data, category, brand
                )

                # Related data
                await add_tags_to_product(
                    product, product_data.get("tags", [])
                )
                await create_product_dimensions(
                    product, product_data.get("dimensions", {})
                )
                await create_product_images(
                    product,
                    product_data.get("images", []),
                    product_data.get("thumbnail"),
                )
                await create_product_reviews(
                    product,
                    product_data.get("reviews", []),
                )
                await create_product_meta(
                    product, product_data.get("meta", {})
                )

            saved_count += 1

        except Exception as e:
            logger.error(
                f"Error saving product {product_data.get('title')}: {e}"
            )
            # automatic rollback happens here

    logger.info(f"Successfully saved {saved_count} products")


async def create_or_get_category(category_name):
    """Create or get category - Single Responsibility: Category management"""
    if not category_name:
        return None

    category, _ = await Category.get_or_create(
        name=category_name, defaults={"slug": category_name.lower().replace(" ", "-")}
    )
    return category


async def create_or_get_brand(brand_name):
    """Create or get brand - Single Responsibility: Brand management"""
    if not brand_name:
        return None

    brand, _ = await Brand.get_or_create(
        name=brand_name, defaults={"slug": brand_name.lower().replace(" ", "-")}
    )
    return brand


async def create_product(product_data, category, brand):
    """Create product - Single Responsibility: Product creation"""
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


async def add_tags_to_product(product, tags):
    """Add tags to product - Single Responsibility: Tag relationships"""
    for tag_name in tags:
        tag, _ = await Tag.get_or_create(
            name=tag_name, defaults={"slug": tag_name.lower().replace(" ", "-")}
        )
        await product.tags.add(tag)


async def create_product_dimensions(product, dimensions_data):
    """Create product dimensions - Single Responsibility: Dimensions management"""
    if dimensions_data:
        await ProductDimensions.create(
            width=float(dimensions_data.get("width", 0)),
            height=float(dimensions_data.get("height", 0)),
            depth=float(dimensions_data.get("depth", 0)),
            product=product,
        )


async def create_product_images(product, images, thumbnail):
    """Create product images - Single Responsibility: Image management"""
    # Handle regular images
    for image_url in images:
        await ProductImage.create(
            image_url=image_url, is_thumbnail=False, product=product
        )

    # Handle thumbnail
    if thumbnail:
        await ProductImage.create(
            image_url=thumbnail, is_thumbnail=True, product=product
        )


async def create_product_reviews(product, reviews):
    """Create product reviews - Single Responsibility: Review management"""
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


async def create_product_meta(product, meta_data):
    """Create product meta data - Single Responsibility: Meta data management"""
    if meta_data:
        await ProductMeta.create(
            barcode=meta_data.get("barcode", ""),
            qr_code_url=meta_data.get("qrCode", ""),
            product=product,
        )


async def fetch_products_page(client, offset, limit):
    """Fetch a single page of products - API helper"""
    try:
        response = await client.get(
            f"{settings.PRODUCT_API_URL}/products?limit={limit}&offset={offset}"
        )
        response.raise_for_status()
        data = response.json()
        return data.get("products", [])
    except Exception as e:
        logger.error(f"Error fetching page offset {offset}: {e}")
        return []
