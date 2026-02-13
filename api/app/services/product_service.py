from typing import List, Optional
from app.models.product import Product, Product_Pydantic, Product_Pydantic_List
from app.schemas import ProductCreate, ProductUpdate, ProductOut, ProductQuery
from app.utils import get_logger

logger = get_logger(__name__)


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
        """Get all unique category names"""
        categories = await Product.all().values("category").distinct()
        return categories

    async def get_all_products(
        self, pagination: Optional[ProductQuery] = None
    ) -> List[ProductOut]:
        """Get all products with optional pagination and filtering"""
       
        query = Product.all().order_by("-created_at").prefetch_related("category", "brand")
        
        if pagination:
            # Apply filters if provided
            filter_data = pagination.model_dump(exclude_none=True, exclude={"offset", "limit"})
            filter_mappings = {
                "title": "title__icontains",
                "description": "description__icontains",
                "price_min": "price__gte",
                "price_max": "price__lte",
                "brand": "brand__name__icontains",
                "availability_status": "availability_status",
                "rating_min": "rating__gte",
                "rating_max": "rating__lte",
                "stock_quantity_min": "stock__gte",
                "category_id": "category_id",
            }

            for field, db_field in filter_mappings.items():
                if field in filter_data:
                    query = query.filter(**{db_field: filter_data[field]})
            
            # Apply pagination after filters
            query = query.offset(pagination.offset).limit(pagination.limit)

        products = await query
        product_pydantics = await Product_Pydantic_List.from_queryset(query)
        return [ProductOut(**prod.model_dump()) for prod in product_pydantics]

    async def get_product_by_id(self, product_id: int) -> Optional[ProductOut]:
        """Get a single product by ID"""
        product = await Product.get_or_none(id=product_id).prefetch_related("category", "brand")
        if not product:
            return None
        product_pydantic = await Product_Pydantic.from_tortoise_orm(product)
        return ProductOut(**product_pydantic.model_dump())

    async def get_products_by_category(self, category_name: str) -> List[ProductOut]:
        """Get all products in a specific category"""
        query = (
            Product.filter(category__name=category_name)
            .order_by("-created_at")
            .prefetch_related("category", "brand")
        )
        product_pydantics = await Product_Pydantic_List.from_queryset(query)
        return [ProductOut(**prod.model_dump()) for prod in product_pydantics]

    async def create_product(self, product_data: ProductCreate) -> Product:
        """
        Create a new product in the database.
        Returns the Product ORM model (not Pydantic) so it can be indexed.
        """
        logger.info(f"Creating product: {product_data.title}")

        # Create product in database
        product = await Product.create(**product_data.model_dump(exclude_none=True))
        
        # Fetch related data for indexing
        await product.fetch_related("category", "brand", "tags")
        
        logger.info(f"Product created with ID: {product.id}")
        return product

    async def update_product(
        self, product_id: int, product_data: ProductUpdate
    ) -> Optional[Product]:
        """
        Update an existing product.
        Returns the Product ORM model (not Pydantic) so it can be re-indexed.
        """
        logger.info(f"Updating product: {product_id}")

        product = await Product.get_or_none(id=product_id)
        if not product:
            logger.warning(f"Product not found: {product_id}")
            return None

        update_data = product_data.model_dump(exclude_none=True)
        if update_data:
            await product.update_from_dict(update_data).save()

        # Fetch related data for indexing
        await product.fetch_related("category", "brand", "tags")
        
        logger.info(f"Product updated: {product_id}")
        return product

    async def delete_product(self, product_id: int) -> bool:
        """Delete a product from the database"""
        logger.info(f"Deleting product: {product_id}")

        product = await Product.get_or_none(id=product_id)
        if not product:
            logger.warning(f"Product not found: {product_id}")
            return False

        await product.delete()
        logger.info(f"Product deleted: {product_id}")
        return True

    async def search_products(self, query: str) -> List[ProductOut]:
        """
        Basic database search for products.
        For advanced search, use SearchService with Elasticsearch.
        """
        logger.info(f"Searching products with query: {query}")

        # Use OR logic for searching across multiple fields
        from tortoise.expressions import Q
        
        products_query = (
            Product.filter(
                Q(title__icontains=query) | 
                Q(description__icontains=query) | 
                Q(brand__name__icontains=query)
            )
            .order_by("-created_at")
            .prefetch_related("category", "brand")
        )
        
        product_pydantics = await Product_Pydantic_List.from_queryset(products_query)
        return [ProductOut(**prod.model_dump()) for prod in product_pydantics]
    
    async def get_product_orm_by_id(self, product_id: int) -> Optional[Product]:
        """
        Get Product ORM model by ID (for internal use, e.g., indexing).
        Fetches all related data.
        """
        product = await Product.get_or_none(id=product_id)
        if product:
            await product.fetch_related("category", "brand", "tags")
        return product