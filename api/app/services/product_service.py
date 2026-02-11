"""
Product service for e-commerce API using Tortoise ORM
"""

from typing import List, Optional
from ..models.product import Product, ProductOutPydantic
from tortoise.contrib.pydantic import pydantic_queryset_creator

ProductOutPydanticList = pydantic_queryset_creator(ProductOutPydantic)

class ProductService:
    
    def __init__(self):
        pass
    
    async def get_all_products(self) -> List[ProductOutPydantic]:
        products = await Product.all().order_by('-created_at').prefetch_related('category')
        return await ProductOutPydanticList.from_queryset(products)
    
    async def get_product_by_id(self, product_id: int) -> Optional[ProductOutPydantic]:
        product = await Product.get_or_none(id=product_id).prefetch_related('category')
        if not product:
            return None
        return await ProductOutPydantic.from_tortoise_orm(product)
    
    async def get_products_by_category(self, category_name: str) -> List[ProductOutPydantic]:
        products = await Product.filter(category__name=category_name).order_by('-created_at').prefetch_related('category')
        return await ProductOutPydanticList.from_queryset(products)
    
    async def create_product(self, product_data: dict) -> ProductOutPydantic:
        product = await Product.create(**product_data)
        await product.fetch_related('category')
        return await ProductOutPydantic.from_tortoise_orm(product)
    
    async def update_product(self, product_id: int, product_data: dict) -> Optional[ProductOutPydantic]:
        product = await Product.get_or_none(id=product_id)
        if not product:
            return None
        
        await product.update_from_dict(product_data).save()
        await product.fetch_related('category')
        return await ProductOutPydantic.from_tortoise_orm(product)
    
    async def delete_product(self, product_id: int) -> bool:
        product = await Product.get_or_none(id=product_id)
        if not product:
            return False
        
        await product.delete()
        return True
    
    async def search_products(self, query: str) -> List[ProductOutPydantic]:
        products = await Product.filter(
            title__icontains=query
        ).filter(
            description__icontains=query
        ).filter(
            brand__icontains=query
        ).order_by('-created_at').prefetch_related('category')
        return await ProductOutPydanticList.from_queryset(products)
