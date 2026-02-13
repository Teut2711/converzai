from typing import Dict, Any, List
from app.models import Product_Pydantic
from app.models import Product as ProductModel
from app import SearchService
from app.utils import get_logger
from elasticsearch import helpers
from app.database import get_es
logger = get_logger(__name__)


class IndexingService:
    """Service for managing Elasticsearch indexing operations"""

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._es = get_es()
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._initialized = True
            self.search_service = SearchService()
            logger.info("IndexingService singleton initialized")

    async def index_product(self, product: ProductModel) -> bool:
        """
        Index a single product to Elasticsearch.
        Accepts Product ORM model and converts to Pydantic internally.
        
        Args:
            product: Product ORM model (should have related data already fetched)
        
        Returns:
            bool: True if indexing successful, False otherwise
        """
        try:
            logger.info(f"Indexing product: {product.id} - {product.title}")
            
            # Convert ORM to Pydantic for serialization
            product_pydantic = await Product_Pydantic.from_tortoise_orm(product)
            
            # Index in Elasticsearch
            success = await self.search_service.index_product(product_pydantic)
            
            if success:
                logger.info(f"Successfully indexed product: {product.id}")
            else:
                logger.warning(f"Failed to index product: {product.id}")
            
            return success

        except Exception as e:
            logger.error(f"Error indexing product {product.id}: {e}")
            return False

    async def bulk_index_products(self, products: List[ProductModel]) -> int:
        """
        Bulk index multiple products to Elasticsearch using async_bulk helper.
        
        Args:
            products: List of Product ORM models
        
        Returns:
            int: Number of successfully indexed products
        """
        if not products:
            logger.info("No products to index")
            return 0
            
        logger.info(f"Bulk indexing {len(products)} products")
        
        async def generate_docs():
            """Generator that yields documents for bulk indexing"""
            for product in products:
                try:
                    # Convert ORM to Pydantic for serialization
                    product_pydantic = await Product_Pydantic.from_tortoise_orm(product)
                    
                    # Yield document in Elasticsearch bulk format
                    yield {
                        "_index": self.search_service.index_name,
                        "_id": str(product_pydantic.id),
                        **product_pydantic.model_dump()
                    }
                    
                except Exception as e:
                    logger.error(f"Error preparing product {product.id} for bulk indexing: {e}")
                    continue
        
        try:
            # Get Elasticsearch client
            es_client = self.search_service._es
            if es_client is None:
                logger.error("Elasticsearch client not available")
                return 0
            
            # Use async_bulk helper for efficient bulk indexing
            success_count = 0
            async for ok, response in helpers.async_bulk(
                es_client, 
                generate_docs(), 
                chunk_size=100,
                request_timeout=60
            ):
                if ok:
                    success_count += 1
                    if success_count % 100 == 0:
                        logger.info(f"Successfully indexed {success_count} products...")
                else:
                    logger.warning(f"Failed to index document: {response}")
            
            logger.info(f"Bulk indexing completed: {success_count}/{len(products)} products")
            return success_count
            
        except Exception as e:
            logger.error(f"Error during bulk indexing: {e}")
            return 0

    async def delete_product_index(self, product_id: int) -> bool:
        """
        Delete product from Elasticsearch index.
        
        Args:
            product_id: ID of the product to remove from index
        
        Returns:
            bool: True if deletion successful, False otherwise
        """
        try:
            success = await self.search_service.delete_product_index(product_id)
            if success:
                logger.info(f"Deleted product index: {product_id}")
            else:
                logger.warning(f"Failed to delete product index: {product_id}")
            return success

        except Exception as e:
            logger.error(f"Error deleting product index {product_id}: {e}")
            return False

    async def reindex_all_products(self) -> int:
        """
        Reindex all products from database to Elasticsearch.
        Useful for rebuilding the index or after mapping changes.
        
        Returns:
            int: Number of successfully reindexed products
        """
        logger.info("Starting full reindex of all products")

        # Fetch all products with related data
        products = await ProductModel.all().prefetch_related("category", "brand", "tags")

        indexed_count = 0
        for product in products:
            try:
                success = await self.index_product(product)
                if success:
                    indexed_count += 1

                if indexed_count % 20 == 0:
                    logger.info(f"Reindexed {indexed_count} products...")

            except Exception as e:
                logger.error(f"Error reindexing product {product.id}: {e}")
                continue

        logger.info(f"Reindexing completed: {indexed_count}/{len(products)} products")
        return indexed_count

    async def reindex_product(self, product_id: int) -> bool:
        """
        Reindex a single product by ID.
        
        Args:
            product_id: ID of the product to reindex
        
        Returns:
            bool: True if reindexing successful, False otherwise
        """
        try:
            product = await ProductModel.get_or_none(id=product_id)
            if not product:
                logger.warning(f"Product not found for reindexing: {product_id}")
                return False
            
            # Fetch related data
            await product.fetch_related("category", "brand", "tags")
            
            # Index the product
            return await self.index_product(product)
            
        except Exception as e:
            logger.error(f"Error reindexing product {product_id}: {e}")
            return False

    async def get_index_stats(self) -> Dict[str, Any]:
        """
        Get Elasticsearch index statistics.
        
        Returns:
            dict: Index statistics including document count, size, etc.
        """
        try:
            stats = await self.search_service.get_index_stats()
            logger.info(f"Index stats: {stats}")
            return stats

        except Exception as e:
            logger.error(f"Error getting index stats: {e}")
            return {}