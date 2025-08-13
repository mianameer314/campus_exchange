from pydantic import BaseModel
from decimal import Decimal
from typing import List, Dict


# ---- Predict Price ----
class PriceSuggestIn(BaseModel):
    title: str
    category: str


class PriceSuggestOut(BaseModel):
    suggested_price: Decimal
    basis: str


# ---- Check Duplicate ----
class DuplicateCheckIn(BaseModel):
    title: str


class DuplicateCheckOut(BaseModel):
    is_duplicate: bool
    similar_items: List[str]


# ---- Recommend ----
class RecommendIn(BaseModel):
    category: str
    current_item_id: int


class RecommendOut(BaseModel):
    recommendations: List[Dict]
