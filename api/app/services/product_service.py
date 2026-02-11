"""
Product service for e-commerce API using Tortoise ORM
"""

from typing import List, Optional
from app.models import Product, ProductPydantic, Product_Pydantic_List
from app.schemas import ProductCreate, ProductUpdate, ProductOut, ProductFilter
from app.utils import get_logger

logger = get_logger(__name__)

class ProductService:
    
    def __init__(self):
        pass
    
    async def get_all_products(self, filters: Optional[ProductFilter] = None) -> List[ProductOut]:
        query = Product.all().order_by('-created_at').prefetch_related('category')
        
        if filters:
            filter_data = filters.model_dump(exclude_none=True)
            filter_mappings = {
                'title': 'title__icontains',
                'description': 'description__icontains',
                'price_min': 'price__gte',
                'price_max': 'price__lte',
                'brand': 'brand__icontains',
                'availability_status': 'availability_status',
                'rating_min': 'rating__gte',
                'rating_max': 'rating__lte',
                'stock_quantity_min': 'stock_quantity__gte',
                'category_id': 'category_id'
            }
            
            for field, db_field in filter_mappings.items():
                if field in filter_data:
                    query = query.filter(**{db_field: filter_data[field]})
        
        product_pydantics = Product_Pydantic_List.from_queryset(query)
        return [ProductOut(**prod.model_dump()) for prod in product_pydantics]
    
    async def get_product_by_id(self, product_id: int) -> Optional[ProductOut]:
        product = await Product.get_or_none(id=product_id).prefetch_related('category')
        if not product:
            return None
        product_pydantic = ProductPydantic.from_tortoise_orm(product)
        return ProductOut(**product_pydantic.model_dump())
    
    async def get_products_by_category(self, category_name: str) -> List[ProductOut]:
        products = await Product.filter(category__name=category_name).order_by('-created_at').prefetch_related('category')
        product_pydantics = Product_Pydantic_List.from_queryset(products)
        return [ProductOut(**prod.model_dump()) for prod in product_pydantics]
    
    async def create_product(self, product_data: ProductCreate) -> ProductOut:
        logger.info(f"Creating product: {product_data.title}")
        
        product = await Product.create(**product_data.model_dump(exclude_none=True))
        await product.fetch_related('category')
        product_pydantic = ProductPydantic.from_tortoise_orm(product)
        return ProductOut(**product_pydantic.model_dump())
    
    async def update_product(self, product_id: int, product_data: ProductUpdate) -> Optional[ProductOut]:
        logger.info(f"Updating product: {product_id}")
        
        product = await Product.get_or_none(id=product_id)
        if not product:
            logger.warning(f"Product not found: {product_id}")
            return None
        
        update_data = product_data.model_dump(exclude_none=True)
        if update_data:
            await product.update_from_dict(update_data).save()
        
        await product.fetch_related('category')
        product_pydantic = ProductPydantic.from_tortoise_orm(product)
        return ProductOut(**product_pydantic.model_dump())
    
    async def delete_product(self, product_id: int) -> bool:
        logger.info(f"Deleting product: {product_id}")
        
        product = await Product.get_or_none(id=product_id)
        if not product:
            logger.warning(f"Product not found: {product_id}")
            return False
        
        await product.delete()
        return True
    
    async def search_products(self, query: str) -> List[ProductOut]:
        logger.info(f"Searching products with query: {query}")
        
        products = await Product.filter(
            title__icontains=query
        ).filter(
            description__icontains=query
        ).filter(
            brand__icontains=query
        ).order_by('-created_at').prefetch_related('category')
        product_pydantics = Product_Pydantic_List.from_queryset(products)
        return [ProductOut(**prod.model_dump()) for prod in product_pydantics]
