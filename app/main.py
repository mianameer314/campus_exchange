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

@app.on_event("startup")
def create_single_admin():
    # Use a 'with' statement for the session to ensure it's always closed.
    # This makes database interactions in startup more robust.
    try:
        with SessionLocal() as db: # IMP: Using 'with' statement for session
            admin = db.query(User).filter(User.is_admin == True).first()
            if not admin:
                new_admin = User(
                    email=settings.ADMIN_EMAIL,
                    hashed_password=hash_password(settings.ADMIN_PASSWORD),
                    is_admin=True,
                    is_verified=True,
                )
                db.add(new_admin)
                db.commit()
                # Optional: refresh the object to get the ID if needed later in startup
                db.refresh(new_admin)
                log.info("Admin user created: %s", settings.ADMIN_EMAIL)
            else:
                log.info("Admin already exists, skipping creation")
    except Exception as e:
        log.error("Admin bootstrap failed: %s", e)
        # Re-raise the exception to make sure Railway captures it if it's critical
        # If you want the app to start even if admin creation fails, remove 'raise e'
        raise e 


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
