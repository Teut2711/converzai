from app.utils import get_logger
from app.models import ProductCreate

logger = get_logger(__name__)


class DataIngestionService:
    """
    Orchestrator service that coordinates data fetching, database operations,
    and Elasticsearch indexing for product data.
    """

    def __init__(self):
        from app.services import DataFetchService, DatabaseService, IndexingService

        self.fetch_service = DataFetchService()
        self.db_service = DatabaseService()
        self.indexing_service = IndexingService()
        
        logger.info("DataIngestionService initialized with all sub-services")

    async def load_seed_data(self):
        """
        Main orchestration method: fetches data from API, saves to database,
        and indexes to Elasticsearch.
        """
        logger.info("Starting seed data loading process...")

        products_create = await self.fetch_service.fetch_all_products()
        if not products_create:
            logger.warning("No products fetched from API, aborting seed data load")
            return

        validated_products = []
        for a_product in products_create:
            try:
                validated_products.append(a_product)
            except Exception as e:
                logger.error(f"Invalid product data: {e}, skipping")
                continue

        if not validated_products:
            logger.warning("No valid products after validation, aborting seed data load")
            return

        saved_products = await self.db_service.save_products(validated_products)
        
        if not saved_products:
            logger.warning("No products were saved to database")
            return

        await self._index_api_data(validated_products)

        logger.info("Seed data loading completed successfully")

    async def _index_api_data(self, products):
        """
        Index original API data directly to Elasticsearch without DB roundtrip.
        
        Args:
            products: List of ProductCreate instances
        """
        if not products:
            logger.info("No products to index")
            return

        logger.info(f"Indexing {len(products)} products to Elasticsearch from API data...")
        
        # Convert ProductCreate objects to dictionaries for indexing
        products_data = [product.model_dump() for product in products]
        
        indexed_count = await self.indexing_service.bulk_index_product_data(
            products_data
        )
        
        logger.info(
            f"Successfully indexed {indexed_count}/{len(products_data)} "
            f"products to Elasticsearch from API data"
        )

    async def ingest_and_index_products(self, products_data):
        """
        Ingest product data (from any source) and index to Elasticsearch.
        Useful for manual imports or migrations.
        
        Args:
            products_data: List of product dictionaries
        """
        logger.info(f"Ingesting {len(products_data)} products...")

        # Save to database
        saved_products = await self.db_service.save_products(products_data)

        # Index to Elasticsearch
        if saved_products:
            await self._index_products(saved_products)

        logger.info(f"Ingestion completed: {len(saved_products)} products processed")
        return saved_products

    async def close(self):
        """Close all service connections"""
        logger.info("Closing DataIngestionService connections")
        await self.fetch_service.close()