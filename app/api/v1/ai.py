from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal
from typing import List

from app.api.deps import get_db
from app.models.listing import Listing
from app.schemas.ai import PriceSuggestIn, PriceSuggestOut, DuplicateCheckIn, DuplicateCheckOut, RecommendIn, RecommendOut

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/predict-price", response_model=PriceSuggestOut)
def predict_price(payload: PriceSuggestIn, db: Session = Depends(get_db)):
    avg = db.query(func.avg(Listing.price)).filter(Listing.category == payload.category).scalar()
    if avg is None:
        return PriceSuggestOut(suggested_price=Decimal("0.00"), basis="no_category_data")
    return PriceSuggestOut(
        suggested_price=Decimal(avg).quantize(Decimal('0.01')),
        basis="category_average"
    )


@router.post("/check-duplicate", response_model=DuplicateCheckOut)
def check_duplicate(payload: DuplicateCheckIn, db: Session = Depends(get_db)):
    # Very simple duplicate check based on title similarity
    duplicates = db.query(Listing).filter(Listing.title.ilike(f"%{payload.title}%")).all()
    return DuplicateCheckOut(
        is_duplicate=len(duplicates) > 0,
        similar_items=[item.title for item in duplicates]
    )


@router.post("/recommend", response_model=RecommendOut)
def recommend_items(payload: RecommendIn, db: Session = Depends(get_db)):
    # Basic recommendation: same category but different item
    items = db.query(Listing).filter(
        Listing.category == payload.category,
        Listing.id != payload.current_item_id
    ).limit(5).all()
    return RecommendOut(
        recommendations=[{"id": item.id, "title": item.title, "price": item.price} for item in items]
    )
