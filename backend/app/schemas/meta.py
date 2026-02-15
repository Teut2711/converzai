



"""
Meta schemas for e-commerce API
"""

from typing import Optional
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from tortoise.contrib.pydantic import pydantic_queryset_creator, pydantic_model_creator

class ProductMetaCreate(BaseModel):
    created_at: str
    updated_at: str
    barcode: Optional[str] = None
    qr_code: Optional[str] = None
    
    model_config = ConfigDict(alias_generator=to_camel)


class ProductMetaRead(BaseModel):
    created_at: str
    updated_at: str
    barcode: Optional[str] = None
    qr_code: Optional[str] = None
    
    model_config = ConfigDict(alias_generator=to_camel)


