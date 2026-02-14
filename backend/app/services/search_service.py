"""
Search service for e-commerce API using Elasticsearch
Handles product search, filtering, and suggestions
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from decimal import Decimal
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
    
    
    def get_index_name(self):
        """Get the Elasticsearch index name"""
        return self.index_name
    
    def _serialize_for_es(self, product_data: Dict[str, Any]) -> Dict[str, Any]:

        serialized = {}
        
        for key, value in product_data.items():
            if value is None:
                continue
            elif isinstance(value, datetime):
                serialized[key] = value.isoformat()
            elif isinstance(value, Decimal):
                serialized[key] = float(value)
            elif isinstance(value, dict):
                serialized[key] = self._serialize_for_es(value)
            elif isinstance(value, list):
                serialized[key] = [
                    self._serialize_for_es(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                serialized[key] = value
        
        return serialized
    
    async def search_products(self, query: str, size: int = 20, from_: int = 0) -> List[Dict[str, Any]]:
        """Search products using Elasticsearch"""
        try:
            logger.info(f"Searching products with query: '{query}', size: {size}, from: {from_}")
            
            es_client = self._es
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
                            "category^2"      # Boost category matches
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
            
            es_client = self._es
            if es_client is None:
                logger.error("Elasticsearch client not available")
                return []
            
            # Build filter query
            filters = []
            
            if category:
                filters.append({"term": {"category.keyword": category}})
            
            if brand:
                filters.append({"term": {"brand.keyword": brand}})
            
            if min_price is not None or max_price is not None:
                price_range = {}
                if min_price is not None:
                    price_range["gte"] = min_price
                if max_price is not None:
                    price_range["lte"] = max_price
                filters.append({"range": {"price": price_range}})
            
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
            
            es_client = self._es
            if es_client is None:
                logger.error("Elasticsearch client not available")
                return []
            
            search_body = {
                "suggest": {
                    "product_suggest": {
                        "prefix": query,
                        "completion": {
                            "field": "title_suggest",
                            "size": size,
                            "skip_duplicates": True
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
    
    async def index_product(self, product_pydantic: Product_Pydantic) -> bool:
        """
        Index a single product to Elasticsearch.
        
        Args:
            product_pydantic: Product_Pydantic model (already converted from ORM)
        
        Returns:
            bool: True if indexing successful, False otherwise
        """
        try:
            logger.info(f"Indexing product: {product_pydantic.id} - {product_pydantic.title}")
            
            es_client = await self._es
            if es_client is None:
                logger.error("Elasticsearch client not available")
                return False
            
            # Convert Pydantic model to dict
            product_doc = product_pydantic.model_dump(exclude_none=True)
            
            # Serialize for Elasticsearch (handle datetime and Decimal)
            product_doc = self._serialize_for_es(product_doc)
            
            # Extract category name if available
            if 'category' in product_doc and isinstance(product_doc['category'], dict):
                product_doc['category'] = product_doc['category'].get('name', '')
            
            # Extract brand name if available
            if 'brand' in product_doc and isinstance(product_doc['brand'], dict):
                product_doc['brand'] = product_doc['brand'].get('name', '')
            
            # Add title suggestion for autocomplete
            product_doc['title_suggest'] = {
                "input": [product_pydantic.title],
                "weight": int(product_pydantic.rating * 10) if product_pydantic.rating else 50
            }
            
            # Index the document
            response = await es_client.index(
                index=self.index_name,
                id=product_pydantic.id,
                body=product_doc
            )
            
            result = response.get("result") in ["created", "updated"]
            logger.info(f"Product indexing result: {response.get('result')}")
            return result
            
        except Exception as e:
            logger.error(f"Indexing error for product {product_pydantic.id}: {e}")
            return False
    
    async def delete_product_index(self, product_id: int) -> bool:
        """Delete product from Elasticsearch index"""
        try:
            logger.info(f"Deleting product from index: {product_id}")
            
            es_client = await self._es
            if es_client is None:
                logger.error("Elasticsearch client not available")
                return False
            
            response = await es_client.delete(
                index=self.index_name,
                id=product_id,
                ignore=[404]  # Ignore if document doesn't exist
            )
            
            result = response.get("result") == "deleted"
            logger.info(f"Product deletion result: {response.get('result')}")
            return result
            
        except Exception as e:
            logger.error(f"Delete index error for product {product_id}: {e}")
            return False
    
    async def get_index_stats(self) -> Dict[str, Any]:
        """Get Elasticsearch index statistics"""
        try:
            es_client = await self._es
            if es_client is None:
                logger.error("Elasticsearch client not available")
                return {}
            
            # Get index stats
            stats = await es_client.indices.stats(index=self.index_name)
            
            if self.index_name in stats.get("indices", {}):
                index_stats = stats["indices"][self.index_name]
                return {
                    "document_count": index_stats["total"]["docs"]["count"],
                    "index_size_bytes": index_stats["total"]["store"]["size_in_bytes"],
                    "index_name": self.index_name
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error getting index stats: {e}")
            return {}