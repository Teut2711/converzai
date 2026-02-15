"""
Search service for e-commerce API using Elasticsearch
Handles product search, filtering, and suggestions
"""

from typing import List, Optional, Any
from app.models.product import Product_Pydantic
from app.utils import get_logger
from app.connectors import get_es
from app.settings import settings

logger = get_logger(__name__)


class SearchService:
    
    def __init__(self, es_client: Optional[Any] = None, db_service=None):
        """Initialize SearchService with optional dependencies"""
        self._es = es_client or get_es()
        self.index_name = settings.ELASTICSEARCH_INDEX_NAME
        self.db_service = db_service
        logger.info(f"SearchService initialized with index: {self.index_name}")
    
    def get_index_name(self):
        """Get the Elasticsearch index name"""
        return self.index_name
    
    async def search_products(self, query: str, size: int = 20, regex_search: bool = False) -> List[Product_Pydantic]:
        """Search products using Elasticsearch and hydrate with database data"""
        try:
            logger.info(f"Searching products with query: '{query}', size: {size}, regex: {regex_search}")
            
            es_client = self._es
            if es_client is None:
                logger.error("Elasticsearch client not available")
                return []
            
            # Build query based on search type
            if regex_search:
                search_body = {
                    "query": {
                        "wildcard": {
                            "title": {
                                "value": f"*{query}*"
                            }
                        }
                    }
                }
            else:
                search_body = {
                    "query": {
                        "bool": {
                            "should": [
                                {
                                    "multi_match": {
                                        "query": query,
                                        "fields": [
                                            "title^3",        # Boost title matches
                                            "brand^2",        # Boost brand matches
                                            "description",    # Description matches
                                            "category^2"      # Boost category matches
                                        ],
                                        "type": "best_fields",
                                        "fuzziness": "AUTO"
                                    }
                                },
                              
                            ]
                        }
                    }
                }
            
            # Add common search parameters
            search_body.update({
                "size": size,
                "sort": [{"_score": {"order": "desc"}}]
            })
            
            # Execute search
            response = await es_client.search(
                index=self.index_name,
                body=search_body
            )
            
            # Extract hits and get product IDs
            hits = response.get("hits", {}).get("hits", [])
            product_ids = []
            
            for hit in hits:
                product_id = hit.get("_source", {}).get("id")
                if product_id:
                    product_ids.append(product_id)
            
            logger.info(f"Found {len(product_ids)} product IDs from search")
            
            # Hydrate with full product data from database
            if product_ids:
                products = await self.db_service.get_products_by_ids(product_ids)
                # logger.info(f"Hydrated {len(products)} products from database")
                return products
            else:
                return []
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    async def delete_index(self) -> bool:
        """Delete the Elasticsearch index"""
        try:
            logger.info(f"Deleting index: {self.index_name}")
            
            es_client = self._es
            if es_client is None:
                logger.error("Elasticsearch client not available")
                return False
            
            # Check if index exists
            if await es_client.indices.exists(index=self.index_name):
                await es_client.indices.delete(index=self.index_name)
                logger.info(f"Successfully deleted index: {self.index_name}")
                return True
            else:
                logger.info(f"Index {self.index_name} does not exist")
                return True
                
        except Exception as e:
            logger.error(f"Error deleting index: {e}")
            return False