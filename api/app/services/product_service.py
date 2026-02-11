"""
Product service for e-commerce API using Tortoise ORM
"""

from typing import List, Optional
from ..models.product import Product
from ..models.category import Category

class ProductService:
    """Service for product operations"""
    
    def __init__(self):
        pass
    
    async def get_all_products(self) -> List[Product]:
        """Get all products"""
        return await Product.all().order_by('-created_at')
    
    async def get_product_by_id(self, product_id: int) -> Optional[Product]:
        """Get product by ID"""
        return await Product.get_or_none(id=product_id).prefetch_related('category')
    
    async def get_products_by_category(self, category_name: str) -> List[Product]:
        """Get products by category name"""
        return await Product.filter(category__name=category_name).order_by('-created_at').prefetch_related('category')
    
    async def create_product(self, product_data: dict) -> Product:
        """Create a new product"""
        product = await Product.create(**product_data)
        return product
    
    async def update_product(self, product_id: int, product_data: dict) -> Optional[Product]:
        """Update an existing product"""
        product = await self.get_product_by_id(product_id)
        if not product:
            return None
        
        await product.update_from_dict(product_data).save()
        return product
    
    async def delete_product(self, product_id: int) -> bool:
        """Delete a product"""
        product = await self.get_product_by_id(product_id)
        if not product:
            return False
        
        await product.delete()
        return True
    
    async def search_products(self, query: str) -> List[Product]:
        """Search products by title or description"""
        return await Product.filter(
            title__icontains=query
        ).filter(
            description__icontains=query
        ).filter(
            brand__icontains=query
        ).order_by('-created_at').prefetch_related('category')
