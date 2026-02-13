"""
Service layer tests for e-commerce API
"""

import pytest
from unittest.mock import AsyncMock, patch
from app.services import ProductService
from app.services import SearchService

@pytest.mark.asyncio
async def test_product_service_get_all_products_empty(sample_category):
    """Test ProductService.get_all_products when no products exist"""
    service = ProductService()
    products = await service.get_all_products()
    assert products == []


@pytest.mark.asyncio
async def test_product_service_get_all_products_with_data(sample_product):
    """Test ProductService.get_all_products when products exist"""
    service = ProductService()
    products = await service.get_all_products()
    assert len(products) == 1
    assert products[0].title == "Test Smartphone"


@pytest.mark.asyncio
async def test_product_service_get_product_by_id(sample_product):
    """Test ProductService.get_product_by_id"""
    service = ProductService()
    product = await service.get_product_by_id(sample_product.id)
    assert product is not None
    assert product.title == "Test Smartphone"
    assert product.id == sample_product.id


@pytest.mark.asyncio
async def test_product_service_get_product_by_id_not_found():
    """Test ProductService.get_product_by_id with non-existent ID"""
    service = ProductService()
    product = await service.get_product_by_id(99999)
    assert product is None


@pytest.mark.asyncio
async def test_product_service_get_products_by_category(sample_product, sample_category):
    """Test ProductService.get_products_by_category"""
    service = ProductService()
    products = await service.get_products_by_category("Electronics")
    assert len(products) == 1
    assert products[0].title == "Test Smartphone"


@pytest.mark.asyncio
async def test_product_service_get_products_by_category_not_found():
    """Test ProductService.get_products_by_category with non-existent category"""
    service = ProductService()
    products = await service.get_products_by_category("NonExistent")
    assert products == []


@pytest.mark.asyncio
async def test_category_service_get_all_categories_empty():
    """Test CategoryService.get_all_categories when no categories exist"""
    service = CategoryService()
    categories = await service.get_all_categories()
    assert categories == []


@pytest.mark.asyncio
async def test_category_service_get_all_categories_with_data(sample_category):
    """Test CategoryService.get_all_categories when categories exist"""
    service = CategoryService()
    categories = await service.get_all_categories()
    assert len(categories) == 1
    assert categories[0].name == "Electronics"
    assert categories[0].slug == "electronics"


@pytest.mark.asyncio
async def test_search_service_search_products():
    """Test SearchService.search_products with mocked Elasticsearch"""
    with patch('app.services.search_service.Elasticsearch') as mock_es:
        # Mock Elasticsearch client
        mock_client = AsyncMock()
        mock_es.return_value = mock_client
        
        # Mock search response
        mock_response = {
            "hits": {
                "hits": [
                    {
                        "_source": {
                            "id": 1,
                            "title": "Test Smartphone",
                            "description": "A test smartphone",
                            "price": 699.99,
                            "discount_percentage": 10.0,
                            "brand": "TestBrand",
                            "category": "Electronics",
                            "availability_status": "in_stock",
                            "rating": 4.5,
                            "stock_quantity": 50,
                            "final_price": 629.99,
                            "created_at": "2024-01-01T00:00:00",
                            "updated_at": "2024-01-01T00:00:00"
                        }
                    }
                ]
            }
        }
        
        mock_client.search.return_value = mock_response
        
        # Test the service
        service = SearchService("http://fake-elasticsearch:9200")
        products = await service.search_products("smartphone")
        
        assert len(products) == 1
        assert products[0]["title"] == "Test Smartphone"
        mock_client.search.assert_called_once()


@pytest.mark.asyncio
async def test_search_service_search_products_no_results():
    """Test SearchService.search_products with no results"""
    with patch('app.services.search_service.Elasticsearch') as mock_es:
        # Mock Elasticsearch client
        mock_client = AsyncMock()
        mock_es.return_value = mock_client
        
        # Mock empty search response
        mock_response = {
            "hits": {
                "hits": []
            }
        }
        
        mock_client.search.return_value = mock_response
        
        # Test the service
        service = SearchService("http://fake-elasticsearch:9200")
        products = await service.search_products("nonexistent")
        
        assert len(products) == 0
        mock_client.search.assert_called_once()


@pytest.mark.asyncio
async def test_search_service_connection_error():
    """Test SearchService.search_products with connection error"""
    with patch('app.services.search_service.Elasticsearch') as mock_es:
        # Mock Elasticsearch client that raises connection error
        mock_client = AsyncMock()
        mock_es.return_value = mock_client
        mock_client.search.side_effect = Exception("Connection error")
        
        # Test the service
        service = SearchService("http://fake-elasticsearch:9200")
        
        with pytest.raises(Exception, match="Connection error"):
            await service.search_products("smartphone")
