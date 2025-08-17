from pydantic import BaseModel
from datetime import datetime

class ChatMessageBase(BaseModel):
    content: str

class ChatMessageCreate(ChatMessageBase):
    listing_id: int
    sender_id: int
    receiver_id: int

class ChatMessageOut(ChatMessageBase):
    id: int
    listing_id: int
    sender_id: int
    receiver_id: int
    timestamp: datetime
    edited: bool = False
    deleted: bool = False

    class Config:
        orm_mode = True
        from_attributes = True

# Optional: Schemas for editing/deleting messages
class ChatMessageEdit(BaseModel):
    message_id: int
    new_content: str

class ChatMessageDelete(BaseModel):
    message_id: int
