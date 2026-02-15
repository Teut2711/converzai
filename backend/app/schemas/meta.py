



"""
Meta schemas for e-commerce API
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
 
class ProductMetaCreate(BaseModel):
    created_at: datetime
    updated_at: datetime
    barcode: Optional[str] = None
    qr_code: Optional[str] = None
    
    model_config = ConfigDict(alias_generator=to_camel)


class ProductMetaRead(BaseModel):
    created_at: datetime
    updated_at: datetime
    barcode: Optional[str] = None
    qr_code: Optional[str] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
    )


