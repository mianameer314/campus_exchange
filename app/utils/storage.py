import os
from fastapi import UploadFile
from app.core.config import settings

def save_upload(file: UploadFile, subdir: str = "ids") -> str:
    base = settings.UPLOAD_DIR or "./uploads"
    os.makedirs(os.path.join(base, subdir), exist_ok=True)
    path = os.path.join(base, subdir, file.filename)
    with open(path, "wb") as f:
        f.write(file.file.read())
    return path
