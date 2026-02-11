"""
Search service for e-commerce API using Elasticsearch
"""

from typing import List, Optional, Dict, Any
from elasticsearch import Elasticsearch
from ..models.product import Product

class SearchService:
    """Service for Elasticsearch search operations"""
    
    def __init__(self, elasticsearch_url: str):
        self.es = Elasticsearch([elasticsearch_url])
        self.index_name = "products"
    
    async def search_products(self, query: str, size: int = 20, from_: int = 0) -> List[Dict[str, Any]]:
        """Search products using Elasticsearch"""
        try:
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
            response = self.es.search(
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
            
            return products
            
        except Exception as e:
            print(f"Search error: {e}")
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
            response = self.es.search(
                index=self.index_name,
                body=search_body
            )
            
            # Extract hits
            hits = response.get("hits", {}).get("hits", [])
            return [hit.get("_source", {}) for hit in hits]
            
        except Exception as e:
            print(f"Filter error: {e}")
            return []
    
    async def get_suggestions(self, query: str, size: int = 5) -> List[str]:
        """Get search suggestions"""
        try:
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
            
            response = self.es.search(
                index=self.index_name,
                body=search_body
            )
            
            suggestions = []
            suggest = response.get("suggest", {}).get("product_suggest", [])
            
            for option in suggest:
                for suggestion in option.get("options", []):
                    suggestions.append(suggestion.get("text", ""))
            
            return suggestions
            
        except Exception as e:
            print(f"Suggestion error: {e}")
            return []
    
    async def index_product(self, product: Product) -> bool:
        """Index a single product"""
        try:
            product_doc = {
                "id": product.id,
                "title": product.title,
                "description": product.description,
                "price": product.price,
                "final_price": product.final_price,
                "discount_percentage": product.discount_percentage,
                "brand": product.brand,
                "categories": [product.category.name] if product.category else [],
                "availability_status": product.availability_status,
                "rating": product.rating,
                "created_at": product.created_at.isoformat(),
                "updated_at": product.updated_at.isoformat()
            }
            
            response = self.es.index(
                index=self.index_name,
                id=product.id,
                body=product_doc
            )
            
            return response.get("result") == "created" or response.get("result") == "updated"
            
        except Exception as e:
            print(f"Indexing error: {e}")
            return False
    
    async def delete_product_index(self, product_id: int) -> bool:
        """Delete product from index"""
        try:
            response = self.es.delete(
                index=self.index_name,
                id=product_id
            )
            return response.get("result") == "deleted"
        except Exception as e:
            print(f"Delete index error: {e}")
            return False
