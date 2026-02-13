"""
Elasticsearch indexing service for products
Handles bulk indexing, search indexing, and index management
"""

from typing import List, Dict, Any
from app.models import Product_Pydantic_List
from app.services.search_service import SearchService
from app.utils import get_logger

logger = get_logger(__name__)


class IndexingService:
    """Service for managing Elasticsearch indexing operations"""
    
    def __init__(self):
        self.search_service = SearchService()
    
    async def bulk_index_products(self, products: Product_Pydantic_List) -> int:
        """Bulk index multiple products to Elasticsearch"""
        logger.info(f"Bulk indexing {len(products)} products")
        
        indexed_count = 0
        for product_data in products:
            try:
                
                
                
                await self.search_service.index_product(product_data)
                indexed_count += 1
                
                if indexed_count % 10 == 0:
                    logger.info(f"Indexed {indexed_count} products...")
                    
            except Exception as e:
                logger.error(f"Error indexing product {product_data.get('title', 'Unknown')}: {e}")
                continue
        
        logger.info(f"Bulk indexing completed: {indexed_count}/{len(products)} products")
        return indexed_count
    
    async def create_product_index(self, product_data: Dict[str, Any]) -> bool:
        """Index a single product"""
        try:
            from app.schemas import ProductCreate
            product_create = ProductCreate(
                title=product_data.get("title", ""),
                description=product_data.get("description", ""),
                price=float(product_data.get("price", 0)),
                discount_percentage=float(product_data.get("discountPercentage", 0)),
                brand=product_data.get("brand", ""),
                availability_status=product_data.get("availabilityStatus", "out_of_stock"),
                rating=float(product_data.get("rating", 0)),
                stock_quantity=product_data.get("stock", 0)
            )
            
            # Create temporary product object for indexing
            from app.models import Product as ProductModel
            temp_product = ProductModel(**product_create.model_dump(exclude_none=True))
            product_pydantic = ProductPydantic.from_tortoise_orm(temp_product)
            
            # Index in Elasticsearch
            await self.search_service.index_product(product_pydantic)
            logger.info(f"Indexed product: {product_data.get('title', 'Unknown')}")
            return True
            
        except Exception as e:
            logger.error(f"Error indexing product {product_data.get('title', 'Unknown')}: {e}")
            return False
    
    async def delete_product_index(self, product_id: int) -> bool:
        """Delete product from Elasticsearch index"""
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
        """Reindex all products from database to Elasticsearch"""
        logger.info("Starting full reindex of all products")
        
        from app.models import Product as ProductModel
        products = await ProductModel.all()
        
        indexed_count = 0
        for product in products:
            try:
                product_pydantic = ProductPydantic.from_tortoise_orm(product)
                await self.search_service.index_product(product_pydantic)
                indexed_count += 1
                
                if indexed_count % 20 == 0:
                    logger.info(f"Reindexed {indexed_count} products...")
                    
            except Exception as e:
                logger.error(f"Error reindexing product {product.id}: {e}")
                continue
        
        logger.info(f"Reindexing completed: {indexed_count}/{len(products)} products")
        return indexed_count
    
    async def get_index_stats(self) -> Dict[str, Any]:
        """Get Elasticsearch index statistics"""
        try:
            stats = await self.search_service.get_index_stats()
            logger.info(f"Index stats: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Error getting index stats: {e}")
            return {}
