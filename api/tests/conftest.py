"""
Pytest configuration and fixtures for e-commerce API tests
"""

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient
from tortoise import Tortoise
from tortoise.contrib.test import finalizer, initializer

from main import app


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def initialize_db() -> AsyncGenerator[None, None]:
    """Initialize test database"""
    # Use in-memory SQLite for testing
    db_url = "sqlite://:memory:"
    
    initializer(["app.models.product", "app.models.category"], db_url=db_url, app_label="models")
    
    # Initialize Tortoise ORM
    await Tortoise.init(
        db_url=db_url,
        modules={"models": ["app.models.product", "app.models.category"]}
    )
    await Tortoise.generate_schemas()
    
    yield
    
    await Tortoise.close_connections()
    finalizer()


@pytest.fixture
async def client(initialize_db: None) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client for the FastAPI app"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def sample_category():
    """Create a sample category for testing"""
    from app.models.category import Category
    
    category = await Category.create(
        name="Electronics",
        slug="electronics",
        description="Electronic devices and accessories"
    )
    yield category
    await category.delete()


@pytest.fixture
async def sample_product(sample_category):
    """Create a sample product for testing"""
    from app.models.product import Product
    
    product = await Product.create(
        title="Test Smartphone",
        description="A high-quality smartphone for testing",
        price=699.99,
        discount_percentage=10.0,
        brand="TestBrand",
        category_id=sample_category.id,
        availability_status="in_stock",
        rating=4.5,
        stock_quantity=50
    )
    yield product
    await product.delete()
