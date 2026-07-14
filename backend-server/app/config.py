from urllib.parse import quote_plus

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Clinic Booking System"
    database_url: str | None = None
    secret_key: str = "dev-secret-key-change-me"
    frontend_origins: str = "http://localhost:5173"
    # Base URL of the deployed frontend, used to build links sent in emails
    # (e.g. the booking confirmation link). Change this when deploying to
    # Vercel or a custom domain. Falls back to the first FRONTEND_ORIGINS
    # entry if left unset.
    frontend_url: str | None = None

    # Default region used to interpret phone numbers typed without a country
    # code (e.g. "0797911909"), so they can still be matched against an
    # international-format number (e.g. "+254797911909") during magic-link
    # verification. Change this per deployment/country.
    default_phone_region: str = "KE"

    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_from_email: str | None = None

    resend_api_key: str | None = None
    resend_from_email: str | None = None

    rate_limit_booking: str = "50/minute"
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

    @property
    def frontend_base_url(self) -> str:
        if self.frontend_url:
            return self.frontend_url.rstrip("/")
        return self.frontend_origins_list[0]


settings = Settings()
