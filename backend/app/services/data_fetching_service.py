import httpx
import json
import hashlib
from pathlib import Path
from typing import List, Optional
from app.settings import settings
from app.utils import get_logger
from app.schemas import ProductCreate

logger = get_logger(__name__)


class DataFetchService:
    """Fetch product data from external API with optional caching."""

    def __init__(self, client=None):
        self.products_url = settings.PRODUCT_API_URL
        self.client = client or httpx.AsyncClient(timeout=30.0)
        self.cache_dir = settings.BASE_DIR / "cached_data"
        self.cache_dir.mkdir(exist_ok=True)
        logger.info(f"DataFetchService initialized with URL: {self.products_url}")

    async def get_all_products(self) -> List[ProductCreate]:
        """Fetch all products, using cache if available."""
        cache_file = self._get_cache_file_path()
        cached = await self._load_from_cache(cache_file)
        if cached is not None:
            return cached

        data = await self._fetch_from_api()
        if data:
            await self._save_to_cache(cache_file, data)
        return self._convert_to_product_creates(data)

    async def fetch_products_paginated(
        self, limit: int = 100, offset: int = 0
    ) -> List[ProductCreate]:
        """Fetch products with pagination (no caching)."""
        params = {"limit": limit, "skip": offset}
        response = await self.client.get(self.products_url, params=params)
        response.raise_for_status()
        data = response.json()
        return self._convert_to_product_creates(data.get("products", []))

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()

    # --- Internal Helpers ---

    def _get_cache_file_path(self) -> Path:
        """Cache filename based on URL hash."""
        url_hash = hashlib.md5(self.products_url.encode()).hexdigest()
        return self.cache_dir / f"{url_hash}.json"

    async def _load_from_cache(self, cache_file: Path) -> Optional[List[ProductCreate]]:
        if not cache_file.exists():
            return None
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return self._convert_to_product_creates(data.get("products", []))
        except Exception as e:
            logger.warning(f"Failed to load cache: {e}")
            return None

    async def _save_to_cache(self, cache_file: Path, data):
        """Save raw API JSON to cache file."""
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")

    async def _fetch_from_api(self) -> List[dict]:
        """Fetch all products from the API (raw JSON)."""
        first_response = await self.client.get(
            f"{self.products_url}?limit={settings.PRODUCT_API_URL_LIMIT}"
        )
        first_response.raise_for_status()
        first_data = first_response.json()
        if not first_data.get("products"):
            return []

        total = first_data.get("total", len(first_data["products"]))
        response = await self.client.get(self.products_url, params={"limit": total})
        response.raise_for_status()
        return response.json()

    def _convert_to_product_creates(
        self, products_data: List[dict]
    ) -> List[ProductCreate]:
        """Convert dicts to ProductCreate instances, skipping invalid entries."""
        result = []
        for p in products_data:
            try:
                result.append(ProductCreate(**p))
            except Exception:
                continue
        return result
