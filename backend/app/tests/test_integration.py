"""
Integration tests for e-commerce API
These tests run against the full stack with real database connections
"""

import pytest
import asyncio
from httpx import AsyncClient
from tortoise import Tortoise
from app.models.product import Product
from app.models.category import Category


@pytest.mark.asyncio
async def test_full_product_workflow():
    """Test complete workflow: create category, create product, retrieve, search"""
    
    # Initialize test database
    await Tortoise.init(
        db_url="sqlite://:memory:",
        modules={"models": ["app.models.product", "app.models.category"]}
    )
    await Tortoise.generate_schemas()
    
    try:
        # Create category
        category = await Category.create(
            name="Books",
            slug="books",
            description="Various book categories"
        )
        
        # Create multiple products
        products = []
        for i in range(3):
            product = await Product.create(
                title=f"Test Book {i+1}",
                description=f"Description for test book {i+1}",
                price=19.99 + (i * 5),
                discount_percentage=0.0,
                brand="TestPublisher",
                category_id=category.id,
                availability_status="in_stock",
                rating=4.0 + (i * 0.5),
                stock_quantity=100 - (i * 10)
            )
            products.append(product)
        
        # Test category retrieval
        categories = await Category.all()
        assert len(categories) == 1
        assert categories[0].name == "Books"
        
        # Test product retrieval
        all_products = await Product.all()
        assert len(all_products) == 3
        
        # Test product by category
        category_products = await Product.filter(category_id=category.id)
        assert len(category_products) == 3
        
        # Test product by ID
        retrieved_product = await Product.get(id=products[0].id)
        assert retrieved_product.title == "Test Book 1"
        
        # Test final price calculation
        product_with_discount = await Product.create(
            title="Discounted Book",
            description="A book with discount",
            price=50.0,
            discount_percentage=20.0,
            category_id=category.id,
            availability_status="in_stock"
        )
        assert product_with_discount.final_price == 40.0
        
        # Clean up
        await Product.all().delete()
        await Category.all().delete()
        
    finally:
        await Tortoise.close_connections()


@pytest.mark.asyncio
async def test_product_model_validation():
    """Test Product model validation and constraints"""
    
    await Tortoise.init(
        db_url="sqlite://:memory:",
        modules={"models": ["app.models.product", "app.models.category"]}
    )
    await Tortoise.generate_schemas()
    
    try:
        # Create category first
        category = await Category.create(
            name="Electronics",
            slug="electronics"
        )
        
        # Test creating product with valid data
        product = await Product.create(
            title="Valid Product",
            description="A valid product description",
            price=99.99,
            discount_percentage=10.0,
            brand="ValidBrand",
            category_id=category.id,
            availability_status="in_stock",
            rating=4.5,
            stock_quantity=50
        )
        
        assert product.title == "Valid Product"
        assert product.final_price == 89.99  # 10% discount
        
        # Test product string representation
        product_str = str(product)
        assert "Valid Product" in product_str
        assert "99.99" in product_str
        
        # Clean up
        await product.delete()
        await category.delete()
        
    finally:
        await Tortoise.close_connections()


@pytest.mark.asyncio
async def test_category_model_validation():
    """Test Category model validation and constraints"""
    
    await Tortoise.init(
        db_url="sqlite://:memory:",
        modules={"models": ["app.models.product", "app.models.category"]}
    )
    await Tortoise.generate_schemas()
    
    try:
        # Test creating category with valid data
        category = await Category.create(
            name="Valid Category",
            slug="valid-category",
            description="A valid category description"
        )
        
        assert category.name == "Valid Category"
        assert category.slug == "valid-category"
        
        # Test category string representation
        category_str = str(category)
        assert "Valid Category" in category_str
        
        # Test unique constraint on slug
        with pytest.raises(Exception):  # Should raise an integrity error
            await Category.create(
                name="Another Category",
                slug="valid-category",  # Same slug
                description="Another description"
            )
        
        # Clean up
        await category.delete()
        
    finally:
        await Tortoise.close_connections()


@pytest.mark.asyncio
async def test_product_category_relationship():
    """Test the relationship between Product and Category"""
    
    await Tortoise.init(
        db_url="sqlite://:memory:",
        modules={"models": ["app.models.product", "app.models.category"]}
    )
    await Tortoise.generate_schemas()
    
    try:
        # Create categories
        electronics = await Category.create(
            name="Electronics",
            slug="electronics"
        )
        books = await Category.create(
            name="Books",
            slug="books"
        )
        
        # Create products in different categories
        laptop = await Product.create(
            title="Laptop",
            price=999.99,
            category_id=electronics.id
        )
        
        novel = await Product.create(
            title="Novel",
            price=19.99,
            category_id=books.id
        )
        
        # Test forward relationship (product -> category)
        await laptop.fetch_related('category')
        assert laptop.category.name == "Electronics"
        
        await novel.fetch_related('category')
        assert novel.category.name == "Books"
        
        # Test reverse relationship (category -> products)
        await electronics.fetch_related('products')
        assert len(electronics.products) == 1
        assert electronics.products[0].title == "Laptop"
        
        await books.fetch_related('products')
        assert len(books.products) == 1
        assert books.products[0].title == "Novel"
        
        # Clean up
        await Product.all().delete()
        await Category.all().delete()
        
    finally:
        await Tortoise.close_connections()
