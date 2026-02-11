"""
Category service for e-commerce API using Tortoise ORM
"""

from typing import List, Optional
from ..models.category import Category, CategoryPydantic
from ..schemas import CategoryCreate, CategoryUpdate, CategoryOut, CategoryFilter
from ..utils import get_logger

logger = get_logger(__name__)

class CategoryService:
    
    def __init__(self):
        pass
    
    async def get_all_categories(self, filters: Optional[CategoryFilter] = None) -> List[CategoryOut]:
        query = Category.all().order_by('name')
        
        if filters:
            filter_data = filters.model_dump(exclude_none=True)
            filter_mappings = {
                'name': 'name__icontains',
                'slug': 'slug__icontains', 
                'description': 'description__icontains'
            }
            
            for field, db_field in filter_mappings.items():
                if field in filter_data:
                    query = query.filter(**{db_field: filter_data[field]})
        
        categories = await query
        category_pydantics = [await CategoryPydantic.from_tortoise_orm(cat) for cat in categories]
        return [CategoryOut(**cat.model_dump()) for cat in category_pydantics]
    
    async def get_category_by_id(self, category_id: int) -> Optional[CategoryOut]:
        category = await Category.get_or_none(id=category_id)
        if not category:
            return None
        category_pydantic = await CategoryPydantic.from_tortoise_orm(category)
        return CategoryOut(**category_pydantic.model_dump())
    
    async def get_category_by_slug(self, slug: str) -> Optional[CategoryOut]:
        category = await Category.get_or_none(slug=slug)
        if not category:
            return None
        category_pydantic = await CategoryPydantic.from_tortoise_orm(category)
        return CategoryOut(**category_pydantic.model_dump())
    
    async def create_category(self, category_data: CategoryCreate) -> CategoryOut:
        logger.info(f"Creating category: {category_data.name}")
        
        category = await Category.create(**category_data.model_dump(exclude_none=True))
        category_pydantic = await CategoryPydantic.from_tortoise_orm(category)
        return CategoryOut(**category_pydantic.model_dump())
    
    async def update_category(self, category_id: int, category_data: CategoryUpdate) -> Optional[CategoryOut]:
        logger.info(f"Updating category: {category_id}")
        
        category = await Category.get_or_none(id=category_id)
        if not category:
            logger.warning(f"Category not found: {category_id}")
            return None
        
        update_data = category_data.model_dump(exclude_none=True)
        if update_data:
            await category.update_from_dict(update_data).save()
        
        category_pydantic = await CategoryPydantic.from_tortoise_orm(category)
        return CategoryOut(**category_pydantic.model_dump())
    
    async def delete_category(self, category_id: int) -> bool:
        logger.info(f"Deleting category: {category_id}")
        
        category = await Category.get_or_none(id=category_id)
        if not category:
            logger.warning(f"Category not found: {category_id}")
            return False
        
        await category.delete()
        return True
