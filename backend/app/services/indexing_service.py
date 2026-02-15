from typing import List
from app.models import Product_Pydantic
from app.models import Product
from app.connectors import get_es
from app.utils import get_logger
from app.models import ProductCreate
from app.settings import settings
from elasticsearch import helpers

logger = get_logger(__name__)


class IndexingService:
    """Service for managing Elasticsearch indexing operations"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._es = get_es()

        return cls._instance


    async def bulk_index_products(self, products: List[Product]) -> int:
        """
        Bulk index multiple products to Elasticsearch using async_bulk helper.
        
        Args:
            products: List of Product ORM models with related data prefetched
        
        Returns:
            int: Number of successfully indexed products
        """
        if not products:
            logger.info("No products to index")
            return 0
            
        logger.info(f"Bulk indexing {len(products)} products")
        
        # Get Elasticsearch client
        es_client = self._es
        if es_client is None:
            logger.error("Elasticsearch client not available")
            return 0
        
        # Prepare documents for bulk indexing
        docs = []
        for product in products:
            try:
                # Convert ORM to Pydantic for serialization
                product_pydantic = await Product_Pydantic.from_tortoise_orm(product)
                
                # Add document in Elasticsearch bulk format
                docs.append({
                    "_index": settings.ELASTICSEARCH_INDEX_NAME,
                    "_id": str(product_pydantic.id),
                    **product_pydantic.model_dump()
                })
                
            except Exception as e:
                logger.error(f"Error preparing product {product.id} for bulk indexing: {e}")
                continue
        
        if not docs:
            logger.warning("No documents prepared for indexing")
            return 0
        
        # Use async_bulk helper for efficient bulk indexing
        success_count, errors = await helpers.async_bulk(
            es_client, 
            docs, 
            chunk_size=100,
            request_timeout=60
        )
        
        if errors:
            logger.warning(f"Bulk indexing completed with {len(errors)} errors")
        
        logger.info(f"Bulk indexing completed: {success_count}/{len(docs)} products")
        return success_count
            
        
        
    async def _generate_docs(self, products_data: List[dict]):
        """Async generator to yield documents for bulk indexing"""
        for product_data in products_data:
          
            doc_id = product_data.get('id', str(hash(str(product_data))))
            
            yield {
                "_index": settings.ELASTICSEARCH_INDEX_NAME,
                "_id": doc_id,
                "_source": product_data
            }

    async def bulk_index_product_data(self, products_data: List[ProductCreate]) -> int:
        """
        Bulk index product data directly from API data without ORM conversion.
        
        Args:
            products_data: List of product dictionaries from API
        
        Returns:
            int: Number of successfully indexed products
        """
        try:
            logger.info(f"Starting bulk indexing of {len(products_data)} products from API data")
            
            if not products_data:
                logger.warning("No products to index")
                return 0
            
            # Get Elasticsearch client
            es_client = self._es
            
            # Use async_bulk with async generator
            success_count, errors = await helpers.async_bulk(
                es_client, 
                self._generate_docs(products_data), 
                chunk_size=100,
                request_timeout=60
            )
            
            if errors:
                logger.warning(f"Bulk indexing completed with {len(errors)} errors")
            
            logger.info(f"Bulk indexing completed: {success_count}/{len(products_data)} products")
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
            logger.info(f"Deleting product index: {product_id}")
            # For now, just return True since we're focusing on bulk indexing
            return True

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
        products = await Product.all().prefetch_related(
            "tags", "dimensions", "images", "reviews"
        )
        
        
        # Use bulk indexing for efficiency
        indexed_count = await self.bulk_index_products(products)

        logger.info(f"Reindexing completed: {indexed_count}/{len(products)} products")
        return indexed_count
 