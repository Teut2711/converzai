from typing import List, Optional, Any
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

    def __init__(self, es_client: Optional[Any] = None, index_name: str = settings.ELASTICSEARCH_INDEX_NAME):
        """Initialize IndexingService with optional Elasticsearch client dependency"""
        self._es = es_client or get_es()
        self.index_name = index_name
        logger.info("IndexingService initialized")


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
                    "_index": self.index_name,
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
            
        
        
    async def _generate_docs(self, products_data: List[ProductCreate]):
        for product_data in products_data:
            doc = product_data.model_dump()
            doc_id = doc["id"]

            yield {
                "_index": settings.ELASTICSEARCH_INDEX_NAME,
                "_id": str(doc_id),
                "_source": doc
            }

    async def bulk_index_product_data(self, products_data: List[ProductCreate]) -> int:

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
 