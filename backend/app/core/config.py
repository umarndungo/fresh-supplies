from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "Fresh Supplies API"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/freshroute"
    GEOCODING_URL: str = "https://nominatim.openstreetmap.org/search"
    GEOCODING_USER_AGENT: str = "FreshRouteAI/1.0 (location search)"

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    FRONTEND_ORIGIN: str = "http://localhost:3000"
    REFRESH_COOKIE_NAME: str = "frs_refresh_token"
    COOKIE_SECURE: bool = True

    ML_MODEL_PATH: str = (
        "../post_harvest_data_engine/data/processed/food/food_model_inference.joblib"
    )
    ML_MARKET_PRICES_PATH: str = (
        "../post_harvest_data_engine/data/processed/food/market_prices.csv"
    )

    OTP_EXPIRE_MINUTES: int = 5
    OTP_RATE_LIMIT_PER_MINUTE: int = 3
    OTP_RATE_LIMIT_WINDOW_MINUTES: int = 10

    # SMTP — sends the mobile app's login OTP by email. SMTP_PASSWORD must be
    # a Gmail *App Password* (Google Account -> Security -> 2-Step
    # Verification -> App passwords), never the real account password —
    # Gmail rejects plain-password SMTP AUTH outright. Set it in backend/.env
    # (gitignored), never here or in .env.example.
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USE_TLS: bool = True
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "amosndungo@gmail.com"
    SMTP_FROM_NAME: str = "Fresh Supplies"
    # When false (no SMTP_PASSWORD configured), OTP codes are logged instead
    # of emailed — keeps local dev working without real credentials.
    SMTP_ENABLED: bool = False
    PHOTO_STORAGE_PATH: str = "./media/shipment_photos"
    PHOTO_MAX_LONG_EDGE: int = 1600
    PHOTO_JPEG_QUALITY: int = 80
    RECONCILIATION_INTERVAL_MINUTES: int = 5


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
