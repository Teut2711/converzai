#!/usr/bin/env python3
"""
Data ingestion module for e-commerce API
Fetches product data from external API and populates MySQL database
"""

import httpx
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

from app.config.settings import settings
from app.database.database import Base, SessionLocal, engine
from app.models.product import Product
from app.models.category import Category
from app.utils import get_logger

logger = get_logger(__name__)


class DataIngestionService:
    
    def __init__(self):
        self.base_url = settings.PRODUCT_API_URL
        self.db: Session = SessionLocal()
        self.client = httpx.AsyncClient(timeout=30.0)
        logger.info(f"DataIngestionService initialized with URL: {self.base_url}")
    
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
    
    async def fetch_products(self, limit: int = 100, batch_size: int = 30) -> List[Dict[str, Any]]:
        """Fetch products using standard limit/offset pagination"""
        try:
            logger.info(f"Fetching up to {limit} products with batch size {batch_size}")
            products = []
            offset = 0
            total_products = 0
            
            while True:
                response = await self.client.get(
                    f"{self.base_url}/products",
                    params={"limit": batch_size, "skip": offset}
                )
                response.raise_for_status()
                
                data = response.json()
                batch_products = data.get("products", [])
                total_products = data.get("total", len(products))
                
                if not batch_products:
                    break
                
                products.extend(batch_products)
                
                logger.info(f"Fetched {len(products)}/{total_products} products...")
                
                if len(products) >= limit or len(products) >= total_products:
                    break
                
                offset += batch_size
            
            result = products[:limit]
            logger.info(f"Total products fetched: {len(result)}")
            return result
            
        except httpx.RequestError as e:
            logger.error(f"Error fetching products: {e}")
            return []
    
    async def create_categories(self, category_names: List[str]) -> Dict[str, int]:
        """Create categories in database"""
        logger.info(f"Creating {len(category_names)} categories")
        category_map = {}
        
        for category_name in category_names:
            slug = category_name.lower().replace(' ', '-').replace('/', '-')
            
            existing = self.db.query(Category).filter(Category.slug == slug).first()
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
            self.db.add(category)
            self.db.commit()
            self.db.refresh(category)
            
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
                existing = self.db.query(Product).filter(Product.title == product_create.title).first()
                if existing:
                    logger.debug(f"Product already exists: {product_create.title}")
                    continue
                
                # Create product from Pydantic model
                product = Product(**product_create.model_dump(exclude_none=True))
                self.db.add(product)
                self.db.commit()
                self.db.refresh(product)
                
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
        
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified")
        
        logger.info("Fetching categories...")
        categories = await self.fetch_categories()
        if not categories:
            logger.warning("No categories found, using default categories")
            categories = ["Electronics", "Clothing", "Home", "Books", "Sports", "Beauty", "Toys", "Automotive"]
        
        logger.info("Creating categories...")
        category_map = await self.create_categories(categories)
        logger.info(f"Created {len(category_map)} categories")
        
        logger.info(f"Fetching up to {product_limit} products...")
        products_data = await self.fetch_products(product_limit)
        if not products_data:
            logger.error("No products found")
            return
        
        logger.info(f"Fetched {len(products_data)} products")
        
        logger.info("Creating products...")
        created_count = await self.create_products(products_data, category_map)
        
        logger.info(f"Data seeding completed!")
        logger.info(f"Categories: {len(category_map)}")
        logger.info(f"Products created: {created_count}")
        logger.info(f"Total products processed: {len(products_data)}")
    
    async def close(self):
        """Close database and HTTP connections"""
        logger.info("Closing data ingestion service connections")
        await self.client.aclose()
        self.db.close()


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
