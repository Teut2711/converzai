"""
Category service for e-commerce API using Tortoise ORM
"""

from typing import List, Optional
from ..models.category import Category

class CategoryService:
    """Service for category operations"""
    
    def __init__(self):
        pass
    
    async def get_all_categories(self) -> List[Category]:
        """Get all categories"""
        return await Category.all().order_by('name')
    
    async def get_category_by_id(self, category_id: int) -> Optional[Category]:
        """Get category by ID"""
        return await Category.get_or_none(id=category_id)
    
    async def get_category_by_slug(self, slug: str) -> Optional[Category]:
        """Get category by slug"""
        return await Category.get_or_none(slug=slug)
    
    async def create_category(self, category_data: dict) -> Category:
        """Create a new category"""
        category = await Category.create(**category_data)
        return category
    
    async def update_category(self, category_id: int, category_data: dict) -> Optional[Category]:
        """Update an existing category"""
        category = await self.get_category_by_id(category_id)
        if not category:
            return None
        
        await category.update_from_dict(category_data).save()
        return category
    
    async def delete_category(self, category_id: int) -> bool:
        """Delete a category"""
        category = await self.get_category_by_id(category_id)
        if not category:
            return False
        
        await category.delete()
        return True
