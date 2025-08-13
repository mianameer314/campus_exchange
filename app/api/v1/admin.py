from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_admin
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/users", dependencies=[Depends(get_current_admin)])
def list_users(db: Session = Depends(get_db)):
    rows = db.query(User).order_by(User.id).limit(100).all()
    return [{"id": u.id, "email": u.email, "is_admin": u.is_admin, "is_verified": u.is_verified} for u in rows]
