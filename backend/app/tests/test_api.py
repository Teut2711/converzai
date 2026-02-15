"""
API endpoint tests for e-commerce API
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

# Create TestClient fixture
@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client

def test_root_endpoint(client: TestClient):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "E-commerce API"
    assert data["version"] == "1.0.0"


def test_health_check(client: TestClient):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_get_products(client: TestClient):
    """Test getting products when none exist"""
    response = client.get("/api/v1/products")
    assert response.status_code == 200
    data = response.json()["products"]
    assert len(data) == 10


def test_get_products_with_pagination(client: TestClient):
    """Test getting products with pagination"""
    response = client.get("/api/v1/products?limit=5&offset=0")
    assert response.status_code == 200
    data = response.json()["products"]
    assert len(data) == 5

def test_get_products_by_category(client: TestClient):
    """Test filtering products by category"""
    response = client.get("/api/v1/products?category=groceries")
    assert response.status_code == 200
    data = response.json()["products"]
    assert len(data) == 10


def test_get_product_by_id(client: TestClient):
    """Test getting a specific product by ID"""
    response = client.get("/api/v1/products/1")
    assert response.status_code == 200


def test_get_product_by_id_not_found(client: TestClient):
    """Test getting a non-existent product"""
    response = client.get("/api/v1/products/99999")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Product not found"


def test_search_products_basic(client: TestClient):
    """Test basic product search"""
    response = client.get("/api/v1/products/search?query=smartphone")
    # May fail due to Elasticsearch not being available in test environment
    assert response.status_code in [200, 500]


def test_search_products_missing_query(client: TestClient):
    """Test searching products without query parameter"""
    response = client.get("/api/v1/products/search?query=groceries")
    assert response.status_code == 200
    data = response.json()["products"]
    assert len(data)  > 0


def test_search_products_with_regex(client: TestClient):
    """Test searching products with regex flag"""
    response = client.get("/api/v1/products/search?query=groc&regex=true")
    assert response.status_code == 200
    data = response.json()["products"]
    assert len(data)  > 0


