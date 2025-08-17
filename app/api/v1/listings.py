import uuid
from typing import List, Optional
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.api import deps
from app.core.config import settings
from app.models.listing import Listing
from app.models.user import User
from app.schemas.listing import ListingOut, ListingUpdate, ListingStatusPatch
from app.utils.storage import (
    save_upload,
    gen_object_key,
    public_url_for_key,
    get_s3_client,
)

router = APIRouter(prefix="/listings", tags=["Listings"])


# -------- Create listing (LOCAL or S3 based on settings) --------
@router.post("", response_model=ListingOut)
async def create_listing(
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    price: Decimal = Form(...),
    images: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(deps.get_db),
    user: User = Depends(deps.get_current_user),
):
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="User must be verified")

    urls = []

    if settings.STORAGE_BACKEND == "LOCAL":
        # Save files locally
        for f in images or []:
            url = save_upload(f, subdir="listings")
            urls.append(url)


    elif settings.STORAGE_BACKEND == "S3":
        # Upload files to S3 directly
        s3_client = get_s3_client()
        for f in images or []:
            key = gen_object_key("listings", f.filename)
            s3_client.upload_fileobj(f.file, settings.S3_BUCKET, key)
            urls.append(public_url_for_key(key))

    else:
        raise HTTPException(status_code=500, detail="Invalid storage backend")

    obj = Listing(
        title=title,
        description=description,
        category=category,
        price=float(price),
        images=urls,
        owner_id=user.id,
        status="ACTIVE",
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


# -------- Get listing --------
@router.get("/{listing_id}", response_model=ListingOut)
def get_listing(listing_id: int, db: Session = Depends(deps.get_db)):
    obj = db.query(Listing).filter(Listing.id == listing_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Listing not found")
    return obj


# -------- Update listing --------
@router.patch("/{listing_id}", response_model=ListingOut)
def update_listing(
    listing_id: int,
    payload: ListingUpdate,
    db: Session = Depends(deps.get_db),
    user: User = Depends(deps.get_current_user),
):
    obj = db.query(Listing).filter(Listing.id == listing_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Listing not found")
    if obj.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not owner")
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="User must be verified")

    for f, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, f, v)

    db.commit()
    db.refresh(obj)
    return obj


# -------- Patch status --------
@router.patch("/{listing_id}/status", response_model=ListingOut)
def patch_status(
    listing_id: int,
    payload: ListingStatusPatch,
    db: Session = Depends(deps.get_db),
    user: User = Depends(deps.get_current_user),
):
    obj = db.query(Listing).filter(Listing.id == listing_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Listing not found")
    if obj.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not owner")
    if payload.status not in {"ACTIVE", "SOLD", "ARCHIVED"}:
        raise HTTPException(status_code=422, detail="Invalid status")

    obj.status = payload.status
    db.commit()
    db.refresh(obj)
    return obj


# -------- Delete listing --------
@router.delete("/{listing_id}", status_code=204)
def delete_listing(
    listing_id: int,
    db: Session = Depends(deps.get_db),
    user: User = Depends(deps.get_current_user),
):
    obj = db.query(Listing).filter(Listing.id == listing_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Listing not found")
    if obj.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not owner")
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="User must be verified")

    db.delete(obj)
    db.commit()
