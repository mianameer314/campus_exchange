from pydantic import BaseModel, field_validator
from typing import Optional, List
from decimal import Decimal


class ListingCreate(BaseModel):
    title: str
    description: str
    category: str
    price: Decimal
    images: Optional[List[str]] = None  # URLs of uploaded images

    @field_validator("images")
    @classmethod
    def clean_images(cls, v):
        return v or []


class ListingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    price: Optional[Decimal] = None
    images: Optional[List[str]] = None  # replace all if provided


class ListingStatusPatch(BaseModel):
    status: str  # ACTIVE, SOLD, ARCHIVED


class ListingOut(BaseModel):
    id: int
    title: str
    description: str
    category: str
    price: Decimal
    images: Optional[List[str]] = None
    status: str
    owner_id: int

    class Config:
        from_attributes = True
