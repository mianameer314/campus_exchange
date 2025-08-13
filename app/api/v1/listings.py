import os
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.api import deps as local_deps
from app.models.listing import Listing
from app.schemas.listing import ListingOut, ListingUpdate
from app.models.user import User # Ensure User model is imported for type hinting and access to is_verified

# Directory for uploads
UPLOAD_DIR = "app/uploads/listings"
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter(prefix="/listings", tags=["Listings"])


@router.post("", response_model=ListingOut, status_code=201)
def create_listing(
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    price: float = Form(...),
    images: List[UploadFile] = File([]),
    db: Session = Depends(local_deps.get_db),
    user: User = Depends(local_deps.get_current_user)
):
    """Create a new listing with optional image uploads."""

    # Check if the user is verified
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="User must be verified to create a listing.")

    saved_files = []
    for img in images:
        ext = img.filename.split(".")[-1]
        file_name = f"{uuid.uuid4()}.{ext}"
        file_path = os.path.join(UPLOAD_DIR, file_name)
        with open(file_path, "wb") as buffer:
            buffer.write(img.file.read())
        saved_files.append(file_name)

    obj = Listing(
        title=title,
        description=description,
        category=category,
        price=price,
        # Corrected line: Pass the list directly to the JSON column
        images=saved_files if saved_files else None,
        owner_id=user.id
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)

    return ListingOut.from_orm(obj)


@router.get("/{listing_id}", response_model=ListingOut)
def get_listing(listing_id: int, db: Session = Depends(local_deps.get_db)):
    """
    Retrieve a listing by ID.
    Viewing listings is generally public, but you can add a verification check here
    if only verified users should be able to view any listing.
    """
    obj = db.query(Listing).filter(Listing.id == listing_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    # Optional: If you want to restrict viewing ONLY to verified users, uncomment this:
    # user: User = Depends(local_deps.get_current_user) # Needs to be defined as a dependency here
    # if not user.is_verified:
    #     raise HTTPException(status_code=403, detail="User must be verified to view listings.")

    return ListingOut.from_orm(obj)


@router.patch("/{listing_id}", response_model=ListingOut)
def update_listing(
    listing_id: int,
    payload: ListingUpdate,
    db: Session = Depends(local_deps.get_db),
    user: User = Depends(local_deps.get_current_user) # Type hint for clarity
):
    """
    Update a listing (owner only).
    Only verified users can update their listings.
    """
    # Check if the user is verified
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="User must be verified to update a listing.")

    obj = db.query(Listing).filter(Listing.id == listing_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Listing not found")
    if obj.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not owner of this listing.")

    for f, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, f, v)

    db.commit()
    db.refresh(obj)
    return ListingOut.from_orm(obj)


@router.delete("/{listing_id}", status_code=204)
def delete_listing(
    listing_id: int,
    db: Session = Depends(local_deps.get_db),
    user: User = Depends(local_deps.get_current_user) # Type hint for clarity
):
    """
    Delete a listing (owner only).
    Only verified users can delete their listings.
    """
    # Check if the user is verified
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="User must be verified to delete a listing.")

    obj = db.query(Listing).filter(Listing.id == listing_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Listing not found")
    if obj.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not owner of this listing.")

    db.delete(obj)
    db.commit()
    return

