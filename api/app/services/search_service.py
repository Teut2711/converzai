"""
Search service for e-commerce API using Elasticsearch
"""

from typing import List, Optional, Dict, Any
from ..models.product import Product
from ..utils import get_logger
from ..database.search_engine import get_es

logger = get_logger(__name__)


class SearchService:
    """Singleton service for Elasticsearch search operations"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SearchService, cls).__new__(cls)
            cls._instance.index_name = "products"
            logger.info(f"SearchService initialized with index: {cls._instance.index_name}")
        return cls._instance
    
    @property
    async def es(self):
        """Get Elasticsearch client from search_engine module"""
        return await get_es()
    
    async def search_products(self, query: str, size: int = 20, from_: int = 0) -> List[Dict[str, Any]]:
        """Search products using Elasticsearch"""
        try:
            logger.info(f"Searching products with query: '{query}', size: {size}, from: {from_}")
            
            es_client = await self.es
            if es_client is None:
                logger.error("Elasticsearch client not available")
                return []
            
            # Search query with multiple fields
            search_body = {
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": [
                            "title^3",        # Boost title matches
                            "brand^2",        # Boost brand matches
                            "description",    # Description matches
                            "categories^2"    # Boost category matches
                        ],
                        "type": "best_fields",
                        "fuzziness": "AUTO"
                    }
                },
                "highlight": {
                    "fields": {
                        "title": {},
                        "description": {},
                        "brand": {}
                    }
                },
                "size": size,
                "from": from_,
                "sort": [
                    {"_score": {"order": "desc"}},
                    {"created_at": {"order": "desc"}}
                ]
            }
            
            # Execute search
            response = await es_client.search(
                index=self.index_name,
                body=search_body
            )
            
            # Extract hits
            hits = response.get("hits", {}).get("hits", [])
            products = []
            
            for hit in hits:
                product_data = hit.get("_source", {})
                product_data["score"] = hit.get("_score", 0)
                
                # Add highlights if available
                if "highlight" in hit:
                    product_data["highlights"] = hit["highlight"]
                
                products.append(product_data)
            
            logger.info(f"Search completed: {len(products)} results found")
            return products
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    async def filter_products(
        self, 
        category: Optional[str] = None,
        brand: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        size: int = 20,
        from_: int = 0
    ) -> List[Dict[str, Any]]:
        """Filter products with multiple criteria"""
        try:
            logger.info(f"Filtering products - category: {category}, brand: {brand}, price_range: {min_price}-{max_price}")
            
            es_client = await self.es
            if es_client is None:
                logger.error("Elasticsearch client not available")
                return []
            
            # Build filter query
            filters = []
            
            if category:
                filters.append({"term": {"categories.keyword": category}})
            
            if brand:
                filters.append({"term": {"brand.keyword": brand}})
            
            if min_price is not None or max_price is not None:
                price_range = {}
                if min_price is not None:
                    price_range["gte"] = min_price
                if max_price is not None:
                    price_range["lte"] = max_price
                filters.append({"range": {"final_price": price_range}})
            
            # Build search body
            search_body = {
                "query": {
                    "bool": {
                        "filter": filters if filters else [{"match_all": {}}]
                    }
                },
                "size": size,
                "from": from_,
                "sort": [{"created_at": {"order": "desc"}}]
            }
            
            # Execute search
            response = await es_client.search(
                index=self.index_name,
                body=search_body
            )
            
            # Extract hits
            hits = response.get("hits", {}).get("hits", [])
            results = [hit.get("_source", {}) for hit in hits]
            
            logger.info(f"Filter completed: {len(results)} results found")
            return results
            
        except Exception as e:
            logger.error(f"Filter error: {e}")
            return []
    
    async def get_suggestions(self, query: str, size: int = 5) -> List[str]:
        """Get search suggestions"""
        try:
            logger.info(f"Getting suggestions for query: '{query}'")
            
            es_client = await self.es
            if es_client is None:
                logger.error("Elasticsearch client not available")
                return []
            
            search_body = {
                "suggest": {
                    "product_suggest": {
                        "prefix": query,
                        "completion": {
                            "field": "title_suggest",
                            "size": size
                        }
                    }
                }
            }
            
            response = await es_client.search(
                index=self.index_name,
                body=search_body
            )
            
            suggestions = []
            suggest = response.get("suggest", {}).get("product_suggest", [])
            
            for option in suggest:
                for suggestion in option.get("options", []):
                    suggestions.append(suggestion.get("text", ""))
            
            logger.info(f"Retrieved {len(suggestions)} suggestions")
            return suggestions
            
        except Exception as e:
            logger.error(f"Suggestion error: {e}")
            return []
    
    async def index_product(self, product: Product) -> bool:
        """Index a single product"""
        try:
            logger.info(f"Indexing product: {product.id} - {product.title}")
            
            es_client = await self.es
            if es_client is None:
                logger.error("Elasticsearch client not available")
                return False
            
            from ..models.product import ProductOutPydantic
            
            # Use Pydantic model for consistent serialization
            product_pydantic = ProductOutPydantic.from_tortoise_orm(product)
            product_doc = product_pydantic.model_dump(exclude_none=True)
            
            # Convert datetime to ISO format for Elasticsearch
            if 'created_at' in product_doc:
                product_doc['created_at'] = product_doc['created_at'].isoformat()
            if 'updated_at' in product_doc:
                product_doc['updated_at'] = product_doc['updated_at'].isoformat()
            
            # Add categories as array for better search
            if product.category:
                product_doc['categories'] = [product.category.name]
            else:
                product_doc['categories'] = []
            
            response = await es_client.index(
                index=self.index_name,
                id=product.id,
                body=product_doc
            )
            
            result = response.get("result") == "created" or response.get("result") == "updated"
            logger.info(f"Product indexing result: {response.get('result')}")
            return result
            
        except Exception as e:
            logger.error(f"Indexing error: {e}")
            return False
    
    async def delete_product_index(self, product_id: int) -> bool:
        """Delete product from index"""
        try:
            logger.info(f"Deleting product from index: {product_id}")
            
            es_client = await self.es
            if es_client is None:
                logger.error("Elasticsearch client not available")
                return False
            
            response = await es_client.delete(
                index=self.index_name,
                id=product_id
            )
            
            result = response.get("result") == "deleted"
            logger.info(f"Product deletion result: {response.get('result')}")
            return result
        except Exception as e:
            logger.error(f"Delete index error: {e}")
            return False
