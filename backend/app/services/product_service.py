from typing import List, Optional
from app.models.product import Product, Product_Pydantic, Product_Pydantic_List
from app.utils import get_logger
from pydantic import BaseModel


def enable_tortoise_logging():
    import logging
    import sys

    fmt = logging.Formatter(
        fmt="%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(logging.DEBUG)
    sh.setFormatter(fmt)

    # will print debug sql
    logger_db_client = logging.getLogger("tortoise.db_client")
    logger_db_client.setLevel(logging.DEBUG)
    logger_db_client.addHandler(sh)

    logger_tortoise = logging.getLogger("tortoise")
    logger_tortoise.setLevel(logging.DEBUG)
    logger_tortoise.addHandler(sh)

logger = get_logger(__name__)
# enable_tortoise_logging()
class Pagination(BaseModel):
    offset: int = 0
    limit: int = 10

class ProductService:
    """Service for managing product CRUD operations"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._initialized = True
            logger.info("ProductService singleton initialized")

    async def get_all_categories(self) -> List[str]:
        categories = await Product.all().distinct().values_list("category", flat=True)
        return categories

    async def get_all_products(
        self, pagination: Optional[Pagination]
    ) -> List[Product_Pydantic_List]:
        query = Product.all().order_by("-created_at").prefetch_related("tags", "dimensions", "images", "reviews")
        
        
        query = query.offset(pagination.offset).limit(pagination.limit)

        product_pydantics = await Product_Pydantic_List.from_queryset(query)
        return product_pydantics

    async def get_products_by_category(
        self, category: str, pagination: Optional[Pagination]
    ) -> List[Product_Pydantic_List]:
        """Get products filtered by category with pagination"""
        query = Product.filter(category=category).order_by("-created_at")
        
        if pagination:
            query = query.offset(pagination.offset).limit(pagination.limit)

        product_pydantics = await Product_Pydantic_List.from_queryset(query)
        
        return product_pydantics
    
    async def get_product_by_id(self, product_id: int) -> Optional[Product_Pydantic]:
        product = await Product.get_or_none(id=product_id)
        
        if not product:
            return None
            
        product_pydantic = await Product_Pydantic.from_tortoise_orm(product)
        return product_pydantic