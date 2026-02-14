from pydantic import BaseModel

class ProductDimensionsBase(BaseModel):
    width: float
    height: float
    depth: float
