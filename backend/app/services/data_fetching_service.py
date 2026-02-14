import httpx
from typing import List, Dict, Any
from app.settings import settings
from app.utils import get_logger

logger = get_logger(__name__)


class DataFetchService:
    """Service responsible for fetching product data from external API"""

    def __init__(self):
        self.products_url = settings.PRODUCT_API_URL
        self.client = httpx.AsyncClient(timeout=30.0)
        logger.info(f"DataFetchService initialized with URL: {self.products_url}")

    async def fetch_all_products(self) -> List[Dict[str, Any]]:
        """
        Fetch all products from the external API.
        
        Returns:
            List of product dictionaries from the API
        """
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

        # Fetch all products in one call
        params = {"limit": total_products}
        response = await self.client.get(self.products_url, params=params)
        response.raise_for_status()
        data = response.json()

        all_products = data.get("products", [])
        logger.info(f"Successfully fetched {len(all_products)} products from API")

        return all_products

    async def fetch_products_paginated(
        self, limit: int = 100, skip: int = 0
    ) -> Dict[str, Any]:
        """
        Fetch products with pagination.
        
        Args:
            limit: Number of products to fetch
            skip: Number of products to skip
            
        Returns:
            API response with products and pagination info
        """
        logger.info(f"Fetching products: limit={limit}, skip={skip}")
        
        params = {"limit": limit, "skip": skip}
        response = await self.client.get(self.products_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        logger.info(f"Fetched {len(data.get('products', []))} products")
        return data

    async def close(self):
        """Close HTTP client connections"""
        logger.info("Closing DataFetchService HTTP connections")
        await self.client.aclose()