#!/usr/bin/env python3
"""
Data ingestion module for e-commerce API
Fetches product data from external API and populates MySQL database
"""

import asyncio
import httpx
from typing import List, Dict, Any
import os

from app.config.settings import settings
from app.database.database import init_db
from app.models.product import Product
from app.models.category import Category
from app.utils import get_logger

logger = get_logger(__name__)


class DataIngestionService:
    
    def __init__(self):
        self.base_url = settings.PRODUCT_API_URL
        self.client = httpx.AsyncClient(timeout=30.0)
        self.max_workers = int(os.getenv('INGESTION_WORKERS', '8'))
        logger.info(f"DataIngestionService initialized with URL: {self.base_url}, workers: {self.max_workers}")
    
    async def fetch_total_pages(self) -> int:
        """Get total number of pages from API"""
        try:
            response = await self.client.get(f"{self.base_url}/products", params={"limit": 1})
            response.raise_for_status()
            data = response.json()
            total = data.get("total", 0)
            pages = (total + 29) // 30  # Ceiling division
            logger.info(f"Total products: {total}, pages: {pages}")
            return pages
        except httpx.RequestError as e:
            logger.error(f"Error fetching total pages: {e}")
            return 0
    
    async def fetch_page(self, page: int, batch_size: int = 30) -> List[Dict[str, Any]]:
        """Fetch a single page of products"""
        try:
            response = await self.client.get(
                f"{self.base_url}/products",
                params={"limit": batch_size, "skip": page * batch_size}
            )
            response.raise_for_status()
            data = response.json()
            return data.get("products", [])
        except httpx.RequestError as e:
            logger.error(f"Error fetching page {page}: {e}")
            return []
    
    async def fetch_categories(self) -> List[str]:
        """Fetch categories from external API"""
        try:
            logger.info("Fetching categories from external API")
            response = await self.client.get(f"{self.base_url}/categories")
            response.raise_for_status()
            categories = response.json()
            logger.info(f"Fetched {len(categories)} categories")
            return categories
        except httpx.RequestError as e:
            logger.error(f"Error fetching categories: {e}")
            return []
    
    async def fetch_products_parallel(self, limit: int = 100, batch_size: int = 30) -> List[Dict[str, Any]]:
        """Fetch products using parallel workers"""
        logger.info(f"Fetching up to {limit} products with {self.max_workers} workers")
        
        # Get total pages first
        total_pages = await self.fetch_total_pages()
        if total_pages == 0:
            return []
        
        # Calculate pages to fetch
        pages_to_fetch = min(total_pages, (limit + batch_size - 1) // batch_size)
        
        # Create semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(self.max_workers)
        
        async def fetch_with_semaphore(page):
            async with semaphore:
                return await self.fetch_page(page, batch_size)
        
        # Fetch pages in parallel
        tasks = [fetch_with_semaphore(page) for page in range(pages_to_fetch)]
        page_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Flatten results and apply limit
        all_products = []
        for result in page_results:
            if isinstance(result, list):
                all_products.extend(result)
            else:
                logger.error(f"Page fetch error: {result}")
        
        final_products = all_products[:limit]
        logger.info(f"Fetched {len(final_products)} products from {pages_to_fetch} pages")
        return final_products
    
    async def create_categories(self, category_names: List[str]) -> Dict[str, int]:
        """Create categories in database"""
        logger.info(f"Creating {len(category_names)} categories")
        category_map = {}
        
        for category_name in category_names:
            slug = category_name.lower().replace(' ', '-').replace('/', '-')
            
            existing = await Category.get_or_none(slug=slug)
            if existing:
                category_map[category_name] = existing.id
                logger.debug(f"Category already exists: {category_name}")
                continue
            
            from app.schemas import CategoryCreate
            
            # Use Pydantic model for category creation
            category_create = CategoryCreate(
                name=category_name,
                slug=slug,
                description=f"Products in {category_name} category"
            )
            
            category = Category(**category_create.model_dump())
            await category.save()
            
            category_map[category_name] = category.id
            logger.info(f"Created category: {category_name}")
        
        logger.info(f"Categories created/processed: {len(category_map)}")
        return category_map
    
    async def create_products(self, products_data: List[Dict[str, Any]], category_map: Dict[str, int]) -> int:
        """Create products in database"""
        logger.info(f"Creating {len(products_data)} products")
        created_count = 0
        
        for product_data in products_data:
            try:
                from app.schemas import ProductCreate
                
                # Map external API data to Pydantic model
                product_create = ProductCreate(
                    title=product_data.get("title", ""),
                    description=product_data.get("description", ""),
                    price=float(product_data.get("price", 0)),
                    discount_percentage=float(product_data.get("discountPercentage", 0)),
                    brand=product_data.get("brand", ""),
                    availability_status="in_stock" if product_data.get("stock", 0) > 0 else "out_of_stock",
                    rating=float(product_data.get("rating", 0)),
                    stock_quantity=product_data.get("stock", 0)
                )
                
                # Set category if available
                category_name = product_data.get("category")
                if category_name and category_name in category_map:
                    product_create.category_id = category_map[category_name]
                
                # Check for existing product
                existing = await Product.get_or_none(title=product_create.title)
                if existing:
                    logger.debug(f"Product already exists: {product_create.title}")
                    continue
                
                # Create product from Pydantic model
                product = Product(**product_create.model_dump(exclude_none=True))
                await product.save()
                
                created_count += 1
                
                if created_count % 10 == 0:
                    logger.info(f"Created {created_count} products...")
                    
            except Exception as e:
                logger.error(f"Error creating product {product_data.get('title', 'Unknown')}: {e}")
                continue
        
        logger.info(f"Products created: {created_count}")
        return created_count
    
    async def seed_data(self, product_limit: int = 100) -> None:
        """Seed data for the application - suitable for FastAPI lifespan"""
        logger.info(f"Starting data seeding from {self.base_url}...")
        
        await init_db()
        logger.info("Database initialized")
        
        logger.info("Fetching categories...")
        categories = await self.fetch_categories()
        if not categories:
            logger.warning("No categories found, using default categories")
            categories = ["Electronics", "Clothing", "Home", "Books", "Sports", "Beauty", "Toys", "Automotive"]
        
        logger.info("Creating categories...")
        category_map = await self.create_categories(categories)
        logger.info(f"Created {len(category_map)} categories")
        
        logger.info(f"Fetching up to {product_limit} products...")
        products_data = await self.fetch_products_parallel(product_limit)
        if not products_data:
            logger.error("No products found")
            return
        
        logger.info(f"Fetched {len(products_data)} products")
        
        logger.info("Creating products...")
        created_count = await self.create_products(products_data, category_map)
        
        logger.info("Data seeding completed!")
        logger.info(f"Categories: {len(category_map)}")
        logger.info(f"Products created: {created_count}")
        logger.info(f"Total products processed: {len(products_data)}")
    
    async def close(self):
        """Close HTTP connections"""
        logger.info("Closing data ingestion service connections")
        await self.client.aclose()


async def seed_database(product_limit: int = 100) -> None:
    """Convenience function for seeding database"""
    logger.info(f"Starting database seeding with limit: {product_limit}")
    ingestion_service = DataIngestionService()
    try:
        await ingestion_service.seed_data(product_limit)
    except Exception as e:
        logger.error(f"Data seeding failed: {e}")
    finally:
        await ingestion_service.close()
