from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal

class ListingCreate(BaseModel):
    title: str
    description: str
    category: str
    price: Decimal

class ListingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    price: Optional[Decimal] = None

class ListingOut(BaseModel):
    id: int
    title: str
    description: str
    category: str
    price: Decimal
    images: Optional[List[str]] = None
    owner_id: int

    class Config:
        from_attributes = True
