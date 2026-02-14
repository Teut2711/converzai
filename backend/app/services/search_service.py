"""
Search service for e-commerce API using Elasticsearch
Handles product search, filtering, and suggestions
"""

from typing import List
from app.models.product import Product_Pydantic
from app.utils import get_logger
from app.connectors import get_es

logger = get_logger(__name__)


class SearchService:
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SearchService, cls).__new__(cls)
            cls._instance.index_name = "products"
            cls._es = get_es()
            logger.info(f"SearchService initialized with index: {cls._instance.index_name}")
        return cls._instance
    
    def __init__(self):
        """Initialize SearchService with DatabaseService dependency"""
        from app.services.db_service import DatabaseService
        self.db_service = DatabaseService()
    
    def get_index_name(self):
        """Get the Elasticsearch index name"""
        return self.index_name
    
    async def search_products(self, query: str, size: int = 20, from_: int = 0, regex_search: bool = False) -> List[Product_Pydantic]:
        """Search products using Elasticsearch and hydrate with database data"""
        try:
            logger.info(f"Searching products with query: '{query}', size: {size}, from: {from_}, regex: {regex_search}")
            
            es_client = self._es
            if es_client is None:
                logger.error("Elasticsearch client not available")
                return []
            
            # Build query based on search type
            if regex_search:
                search_body = {
                    "query": {
                        "regexp": {
                            "title": {
                                "value": f".*{query}.*",
                                "flags": "ALL"
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
                                {
                                    "wildcard": {
                                        "title": {
                                            "value": f"*{query}*",
                                            "boost": 1.0
                                        }
                                    }
                                },
                                {
                                    "wildcard": {
                                        "category": {
                                            "value": f"*{query}*",
                                            "boost": 2.0
                                        }
                                    }
                                }
                            ]
                        }
                    }
                }
            
            # Add common search parameters
            search_body.update({
                "size": size,
                "from": from_,
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
                logger.info(f"Hydrated {len(products)} products from database")
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