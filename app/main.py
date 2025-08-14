import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import auth, verification, listings, search, favorites, notifications, admin, ai, chat
from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import hash_password
import os

log = logging.getLogger("uvicorn.error")

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# root
@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the campus_exchange API"}

# @app.on_event("startup")
# def create_single_admin():
#     print("DEBUG: Entering create_single_admin startup event.") # Debug print
#     try:
#         with SessionLocal() as db:
#             print("DEBUG: SessionLocal created.") # Debug print
#             admin = db.query(User).filter(User.is_admin == True).first()
#             if not admin:
#                 print("DEBUG: Admin user not found. Attempting creation.") # Debug print
#                 new_admin = User(
#                     email=settings.ADMIN_EMAIL,
#                     hashed_password=hash_password(settings.ADMIN_PASSWORD),
#                     is_admin=True,
#                     is_verified=True,
#                 )
#                 db.add(new_admin)
#                 db.commit()
#                 db.refresh(new_admin) # Refresh to get ID if needed, or if other properties are populated by DB
#                 log.info("Admin user created: %s", settings.ADMIN_EMAIL)
#                 print(f"DEBUG: Admin user created: {settings.ADMIN_EMAIL}") # Debug print
#             else:
#                 log.info("Admin already exists, skipping creation")
#                 print("DEBUG: Admin already exists, skipping creation.") # Debug print
#         print("DEBUG: Exiting create_single_admin successfully.") # Debug print
#     except Exception as e:
#         log.error("Admin bootstrap failed: %s", e, exc_info=True) # exc_info=True logs full traceback
#         print(f"ERROR: Admin bootstrap failed: {e}") # Debug print
#         import traceback
#         traceback.print_exc(file=sys.stderr) # IMP: Force full traceback to stderr
#         # Re-raising ensures the container truly exits with an error for Railway to potentially catch better
#         raise e 


app.include_router(auth.router, prefix="/api/v1")
app.include_router(verification.router, prefix="/api/v1")
app.include_router(listings.router, prefix="/api/v1")
app.include_router(search.router, prefix="/api/v1")
app.include_router(favorites.router, prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(ai.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")

@app.get("/healthz", tags=["Health"])
def health():
    return {"status": "ok"}
