import httpx
from typing import List, Dict, Any
from app.settings import settings
from app.utils import get_logger
from app.models import ProductCreate


logger = get_logger(__name__)


class DataFetchService:
    """Service responsible for fetching product data from external API"""

    def __init__(self):
        self.products_url = settings.PRODUCT_API_URL
        self.client = httpx.AsyncClient(timeout=30.0)
        logger.info(f"DataFetchService initialized with URL: {self.products_url}")

    async def fetch_all_products(self) -> List[ProductCreate]:
   
        logger.info("Starting product fetch from API...")

        # Get first page to determine total
        first_response = await self.client.get(
            f"{self.products_url}?limit={settings.PRODUCT_API_URL_LIMIT}"
        )
        first_response.raise_for_status()
        first_data = first_response.json()

        if not first_data.get("products"):
            logger.warning("No products found in API response")
            return []

        total_products = first_data.get("total", len(first_data["products"]))
        logger.info(f"Total products to fetch: {total_products}")

        params = {"limit": total_products}
        response = await self.client.get(self.products_url, params=params)
        response.raise_for_status()
        data = response.json()

        all_products = data.get("products", [])
        logger.info(f"Successfully fetched {len(all_products)} products from API")

        # Convert to ProductCreate instances
        product_creates = []
        for product_dict in all_products:
            try:
                product_create = ProductCreate(**product_dict)
                product_creates.append(product_create)
            except Exception as e:
                logger.error(f"Error creating ProductCreate: {e}")
                continue
        
        return product_creates

    async def fetch_products_paginated(
        self, limit: int = 100, offset: int = 0
    ) -> List[ProductCreate]:
        logger.info(f"Fetching products: limit={limit}, skip={offset}")
        
        params = {"limit": limit, "skip": offset}
        response = await self.client.get(self.products_url, params=params)
        response.raise_for_status()
        data = response.json()
        all_products = data.get("products", [])
        logger.info(f"Fetched {len(all_products)} products")
        
        # Convert to ProductCreate instances
        product_creates = []
        for product_dict in all_products:
            try:
                product_create = ProductCreate(**product_dict)
                product_creates.append(product_create)
            except Exception as e:
                logger.error(f"Error creating ProductCreate: {e}")
                continue
        
        return product_creates

    async def close(self):
        """Close HTTP client connections"""
        logger.info("Closing DataFetchService HTTP connections")
        await self.client.aclose()