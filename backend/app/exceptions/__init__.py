"""
Custom exceptions for the e-commerce API
"""

class ProductNotFound(Exception):
    """Raised when a product is not found"""
    pass

class CategoryNotFound(Exception):
    """Raised when a category is not found"""
    pass

class BrandNotFound(Exception):
    """Raised when a brand is not found"""
    pass

class SearchError(Exception):
    """Raised when search operation fails"""
    pass

class InternalServerError(Exception):
    """Raised for internal server errors"""
    pass