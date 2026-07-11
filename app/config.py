from urllib.parse import quote_plus

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Clinic Booking System"
    database_url: str | None = None
    secret_key: str = "dev-secret-key-change-me"
    frontend_origins: str = "http://localhost:5173"

    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_from_email: str | None = None

    rate_limit_booking: str = "5/minute"
    rate_limit_default: str = "60/minute"

    class Config:
        env_file = ".env"
        extra = "ignore"

    def __init__(self, **values):
        super().__init__(**values)
        if not self.database_url:
            self.database_url = "sqlite:///./clinic.db"

    @property
    def frontend_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.frontend_origins.split(",") if origin.strip()]


settings = Settings()
