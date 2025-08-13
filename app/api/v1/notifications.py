from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.notification import Notification

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("")
def list_notifications(db: Session = Depends(get_db), user=Depends(get_current_user)):
    rows = db.query(Notification).filter(Notification.user_id == user.id).order_by(Notification.id.desc()).limit(50).all()
    return [{"id": n.id, "type": n.type, "payload": n.payload, "is_read": n.is_read, "created_at": n.created_at.isoformat()} for n in rows]
