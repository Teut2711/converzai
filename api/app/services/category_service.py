"""
Category service for e-commerce API using Tortoise ORM
"""

from typing import List, Optional
from ..models.category import Category, CategoryPydantic, CategoryPydanticList

class CategoryService:
    
    def __init__(self):
        pass
    
    async def get_all_categories(self) -> List[CategoryPydantic]:
        categories = await Category.all().order_by('name')
        return await CategoryPydanticList.from_queryset(categories)
    
    async def get_category_by_id(self, category_id: int) -> Optional[CategoryPydantic]:
        category = await Category.get_or_none(id=category_id)
        if not category:
            return None
        return await CategoryPydantic.from_tortoise_orm(category)
    
    async def get_category_by_slug(self, slug: str) -> Optional[CategoryPydantic]:
        category = await Category.get_or_none(slug=slug)
        if not category:
            return None
        return await CategoryPydantic.from_tortoise_orm(category)
    
    async def create_category(self, category_data: dict) -> CategoryPydantic:
        category = await Category.create(**category_data)
        return await CategoryPydantic.from_tortoise_orm(category)
    
    async def update_category(self, category_id: int, category_data: dict) -> Optional[CategoryPydantic]:
        category = await Category.get_or_none(id=category_id)
        if not category:
            return None
        
        await category.update_from_dict(category_data).save()
        return await CategoryPydantic.from_tortoise_orm(category)
    
    async def delete_category(self, category_id: int) -> bool:
        category = await Category.get_or_none(id=category_id)
        if not category:
            return False
        
        await category.delete()
        return True
