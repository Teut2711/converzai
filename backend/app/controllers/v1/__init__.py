"""V1 API views"""

from fastapi import APIRouter
from .product import router as product_router
from .search import router as search_router

v1_router = APIRouter(prefix="/api/v1", tags=["v1"])

v1_router.include_router(product_router)
v1_router.include_router(search_router)

__all__ = ["v1_router"]
