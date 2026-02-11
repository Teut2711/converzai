#!/usr/bin/env python3
"""
Data ingestion script for e-commerce API
Fetches product data from dummyjson.com and populates MySQL database
"""

import asyncio
import requests
import sys
import os
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from dotenv import load_dotenv



from app.database.database import Base, SessionLocal, engine
from app.models.product import Product
from app.models.category import Category

load_dotenv()

class DataIngestionService:
    """Service for ingesting product data from dummyjson.com"""
    
    def __init__(self):
        self.base_url = "https://dummyjson.com"
        self.db: Session = SessionLocal()
    
    async def fetch_categories(self) -> List[Dict[str, Any]]:
        """Fetch categories from dummyjson.com"""
        try:
            response = requests.get(f"{self.base_url}/products/categories")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching categories: {e}")
            return []
    
    async def fetch_products(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Fetch products from dummyjson.com"""
        try:
            # Fetch products with pagination
            products = []
            skip = 0
            total_products = 0
            
            while True:
                response = requests.get(
                    f"{self.base_url}/products",
                    params={"limit": 30, "skip": skip}
                )
                response.raise_for_status()
                
                data = response.json()
                batch_products = data.get("products", [])
                
                if not batch_products:
                    break
                
                products.extend(batch_products)
                total_products = data.get("total", len(products))
                
                print(f"Fetched {len(products)}/{total_products} products...")
                
                if len(products) >= limit or len(products) >= total_products:
                    break
                
                skip += 30
            
            return products[:limit]
            
        except requests.RequestException as e:
            print(f"Error fetching products: {e}")
            return []
    
    async def create_categories(self, category_names: List[str]) -> Dict[str, int]:
        """Create categories in database"""
        category_map = {}
        
        for category_name in category_names:
            # Generate slug from category name
            slug = category_name.lower().replace(' ', '-').replace('/', '-')
            
            # Check if category already exists
            existing = self.db.query(Category).filter(Category.slug == slug).first()
            if existing:
                category_map[category_name] = existing.id
                continue
            
            # Create new category
            category = Category(
                name=category_name,
                slug=slug,
                description=f"Products in {category_name} category"
            )
            self.db.add(category)
            self.db.commit()
            self.db.refresh(category)
            
            category_map[category_name] = category.id
            print(f"Created category: {category_name}")
        
        return category_map
    
    async def create_products(self, products_data: List[Dict[str, Any]], category_map: Dict[str, int]) -> int:
        """Create products in database"""
        created_count = 0
        
        for product_data in products_data:
            try:
                # Map dummyjson fields to our model
                product_dict = {
                    "title": product_data.get("title", ""),
                    "description": product_data.get("description", ""),
                    "price": float(product_data.get("price", 0)),
                    "discount_percentage": float(product_data.get("discountPercentage", 0)),
                    "brand": product_data.get("brand", ""),
                    "availability_status": "in_stock" if product_data.get("stock", 0) > 0 else "out_of_stock",
                    "rating": float(product_data.get("rating", 0)),
                    "stock_quantity": product_data.get("stock", 0)
                }
                
                # Set category if available
                category_name = product_data.get("category")
                if category_name and category_name in category_map:
                    product_dict["category_id"] = category_map[category_name]
                
                # Check if product already exists (by title)
                existing = self.db.query(Product).filter(Product.title == product_dict["title"]).first()
                if existing:
                    continue
                
                # Create new product
                product = Product(**product_dict)
                self.db.add(product)
                self.db.commit()
                self.db.refresh(product)
                
                created_count += 1
                
                if created_count % 10 == 0:
                    print(f"Created {created_count} products...")
                    
            except Exception as e:
                print(f"Error creating product {product_data.get('title', 'Unknown')}: {e}")
                continue
        
        return created_count
    
    async def run_ingestion(self, product_limit: int = 100) -> None:
        """Run the complete data ingestion process"""
        print("Starting data ingestion...")
        
        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)
        print("Database tables created/verified")
        
        # Fetch categories
        print("Fetching categories...")
        categories = await self.fetch_categories()
        if not categories:
            print("No categories found, using default categories")
            categories = ["Electronics", "Clothing", "Home", "Books", "Sports", "Beauty", "Toys", "Automotive"]
        
        # Create categories
        print("Creating categories...")
        category_map = await self.create_categories(categories)
        print(f"Created {len(category_map)} categories")
        
        # Fetch products
        print(f"Fetching up to {product_limit} products...")
        products_data = await self.fetch_products(product_limit)
        if not products_data:
            print("No products found")
            return
        
        print(f"Fetched {len(products_data)} products")
        
        # Create products
        print("Creating products...")
        created_count = await self.create_products(products_data, category_map)
        
        print(f"\nData ingestion completed!")
        print(f"Categories: {len(category_map)}")
        print(f"Products created: {created_count}")
        print(f"Total products processed: {len(products_data)}")
    
    def close(self):
        """Close database connection"""
        self.db.close()

async def main():
    """Main function"""
    ingestion_service = DataIngestionService()
    
    try:
        # Get product limit from command line argument or use default
        product_limit = 100
        if len(sys.argv) > 1:
            try:
                product_limit = int(sys.argv[1])
            except ValueError:
                print("Invalid product limit, using default: 100")
        
        await ingestion_service.run_ingestion(product_limit)
        
    except KeyboardInterrupt:
        print("\nData ingestion interrupted by user")
    except Exception as e:
        print(f"Data ingestion failed: {e}")
    finally:
        ingestion_service.close()

if __name__ == "__main__":
    asyncio.run(main())
