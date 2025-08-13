from pydantic_settings import BaseSettings
from typing import List
from pydantic import AnyHttpUrl, field_validator


class Settings(BaseSettings):
    APP_NAME: str = "Campus_Exchange API"
    APP_VERSION: str = "1.0.0"

    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60

    CORS_ORIGINS: List[AnyHttpUrl] | List[str] = []

    ADMIN_EMAIL: str
    ADMIN_PASSWORD: str

    # Email / SMTP settings (mapped from MAIL_... in .env)
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_PORT: int = 587
    MAIL_FROM_NAME: str = "Campus Exchange"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False

    ALLOWED_EMAIL_DOMAINS: str = "uni.edu,college.edu,cuiatk.edu,cuiatk.edu.pk"
    OTP_TTL_SECONDS: int = 600

    UPLOAD_DIR: str = "./uploads"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors(cls, v):
        if isinstance(v, str):
            return [s.strip() for s in v.split(",") if s.strip()]
        return v

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()


def allowed_domains() -> list[str]:
    """Return allowed email domains as lowercase list."""
    return [
        d.strip().lower()
        for d in settings.ALLOWED_EMAIL_DOMAINS.split(",")
        if d.strip()
    ]
