from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime

class ReportCreate(BaseModel):
    reported_listing_id: Optional[int] = None
    reported_user_id: Optional[int] = None
    reason: str

    @validator('reported_listing_id')
    def listing_id_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError('reported_listing_id must be a positive integer or null')
        return v

    @validator('reported_user_id')
    def user_id_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError('reported_user_id must be a positive integer or null')
        return v

    @validator('reason')
    def reason_not_empty(cls, v):
        if not v or v.strip() == "":
            raise ValueError('reason is required and cannot be empty')
        return v

class ReportOut(BaseModel):
    id: int
    reporter_id: int
    reported_listing_id: Optional[int]
    reported_user_id: Optional[int]
    reason: str
    status: str
    created_at: datetime
    reviewed_by: Optional[int]
    reviewed_at: Optional[datetime]
    audit_log: Optional[str]

    class Config:
        orm_mode = True
        from_attributes = True
