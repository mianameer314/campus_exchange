from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional

from app.api.deps import get_db
from app.models.listing import Listing

router = APIRouter(tags=["Search"])

@router.get("/listings/search")
def search_listings(
    q: Optional[str] = Query(None, description="Search keyword"),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    university: Optional[str] = Query(None, description="Filter by university"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db)
):
    query = db.query(Listing)

    # Full-text search
    if q:
        ts_query = func.plainto_tsquery('english', q)
        query = query.filter(Listing.search_vector.op('@@')(ts_query))

    # Filters
    if category:
        query = query.filter(Listing.category == category)
    if university:
        query = query.filter(Listing.owner.has(university=university))  # Assuming university on User model; adjust if different
    if min_price is not None:
        query = query.filter(Listing.price >= min_price)
    if max_price is not None:
        query = query.filter(Listing.price <= max_price)

    # Sorting
    sort_column = getattr(Listing, sort_by, None)
    if not sort_column:
        raise HTTPException(status_code=400, detail=f"Invalid sort field: {sort_by}")

    if sort_order == 'desc':
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Pagination
    total = query.count()
    listings = query.offset((page - 1) * page_size).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "results": [listing.to_dict() for listing in listings]
    }
