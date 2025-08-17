from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session
from starlette.websockets import WebSocketState
from jose import JWTError, jwt
from app.core.config import settings

from app.api.deps import get_db
from app.models.chat import ChatMessage, BlockedUser
from app.models.listing import Listing
from app.models.user import User
from app.schemas.chat import ChatMessageOut
from typing import Dict, List
import html
import logging

router = APIRouter()
active_connections: Dict[str, List[WebSocket]] = {}


JWT_SECRET = settings.JWT_SECRET
JWT_ALGORITHM = settings.JWT_ALGORITHM

logger = logging.getLogger("chat_ws")

def room_id(listing_id: int, u1: int, u2: int):
    return f"{listing_id}-{min(u1, u2)}-{max(u1, u2)}"

def create_message(db: Session, data: dict):
    msg = ChatMessage(**data)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg

def user_blocked(db: Session, user_id: int, blocked_by: int):
    return db.query(BlockedUser).filter(
        BlockedUser.user_id == user_id,
        BlockedUser.blocked_by == blocked_by
    ).first() is not None

async def get_current_user_websocket(websocket: WebSocket, db: Session):
    auth = websocket.headers.get("authorization")
    if not auth or not auth.lower().startswith("bearer "):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise Exception("Missing or invalid authorization header")
    token = auth[7:]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            raise Exception("Invalid token: no subject")
        # Optionally verify user in DB
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            raise Exception("User not found")
        return int(user_id)
    except JWTError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise Exception("Token decode error")

@router.websocket("/ws/chat/{listing_id}/{peer_id}")
async def chat_ws(websocket: WebSocket, listing_id: int, peer_id: int, db: Session = Depends(get_db)):
    try:
        user_id = await get_current_user_websocket(websocket, db)
    except Exception as e:
        logger.error(f"Auth failed: {e}")
        return  # connection already closed by helper

    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    if user_blocked(db, user_id, peer_id) or user_blocked(db, peer_id, user_id):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    if user_id not in [listing.owner_id, peer_id] or peer_id == user_id:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    rid = room_id(listing_id, user_id, peer_id)
    await websocket.accept()
    active_connections.setdefault(rid, []).append(websocket)
    logger.info(f"User {user_id} connected to room {rid}")

    try:
        while True:
            data = await websocket.receive_json()

            if "typing" in data and data["typing"]:
                for conn in active_connections.get(rid, []):
                    if conn != websocket and conn.application_state == WebSocketState.CONNECTED:
                        await conn.send_json({"typing": True, "user": user_id})

            elif "delivery_receipt" in data:
                message_id = data["delivery_receipt"]
                for conn in active_connections.get(rid, []):
                    if conn != websocket and conn.application_state == WebSocketState.CONNECTED:
                        await conn.send_json({"delivery_receipt": message_id, "user": user_id})

            elif "edit_message" in data:
                edit_data = data["edit_message"]
                msg_db = db.query(ChatMessage).filter(ChatMessage.id == edit_data["message_id"]).first()
                if msg_db and msg_db.sender_id == user_id:
                    new_text = html.escape(edit_data["new_content"].strip())
                    if new_text:
                        msg_db.content = new_text + " (edited)"
                        msg_db.edited = True
                        db.commit()
                        msg_out = ChatMessageOut.from_orm(msg_db).dict()
                        msg_out["timestamp"] = msg_out["timestamp"].isoformat()
                        for conn in active_connections.get(rid, []):
                            if conn.application_state == WebSocketState.CONNECTED:
                                await conn.send_json({"edit_message": msg_out})
                else:
                    await websocket.send_json({"error": "Edit not allowed or message not found."})

            elif "delete_message" in data:
                message_id = data["delete_message"]
                msg_db = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
                if msg_db and msg_db.sender_id == user_id:
                    msg_db.deleted = True
                    db.commit()
                    for conn in active_connections.get(rid, []):
                        if conn.application_state == WebSocketState.CONNECTED:
                            await conn.send_json({"delete_message": message_id})
                else:
                    await websocket.send_json({"error": "Delete not allowed or message not found."})

            elif "content" in data:
                content = html.escape(data["content"].strip())
                if not content:
                    continue

                msg_in = {
                    "listing_id": listing_id,
                    "sender_id": user_id,
                    "receiver_id": peer_id,
                    "content": content
                }
                msg = create_message(db, msg_in)
                msg_out = ChatMessageOut.from_orm(msg).dict()
                msg_out["timestamp"] = msg_out["timestamp"].isoformat()
                for conn in list(active_connections.get(rid, [])):
                    if conn.application_state == WebSocketState.CONNECTED:
                        await conn.send_json(msg_out)

            else:
                await websocket.send_json({"error": "Invalid payload."})

    except WebSocketDisconnect:
        active_connections[rid].remove(websocket)
        if not active_connections[rid]:
            del active_connections[rid]
        logger.info(f"User {user_id} disconnected from room {rid}")

    except Exception as e:
        logger.error(f"Unexpected error in websocket: {e}", exc_info=True)
        if rid in active_connections and websocket in active_connections[rid]:
            active_connections[rid].remove(websocket)
            if not active_connections[rid]:
                del active_connections[rid]
        await websocket.close()
