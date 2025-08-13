from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional
from app.db.session import SessionLocal
from app.models.listing import Listing
from app.schemas.listing import ListingOut

router = APIRouter(prefix="/search", tags=["Search"])

@router.get("", response_model=List[ListingOut])
def search_listings(q: Optional[str] = None, category: Optional[str] = None, min_price: Optional[float] = None, max_price: Optional[float] = None, db: Session = Depends(SessionLocal)):
    stmt = select(Listing)
    if q:
        stmt = stmt.filter(Listing.title.ilike(f"%{q}%"))
    if category:
        stmt = stmt.filter(Listing.category == category)
    if min_price is not None:
        stmt = stmt.filter(Listing.price >= min_price)
    if max_price is not None:
        stmt = stmt.filter(Listing.price <= max_price)
    rows = db.execute(stmt).scalars().all()
    return [ListingOut(id=o.id, title=o.title, description=o.description, category=o.category, price=o.price, owner_id=o.owner_id) for o in rows]
