from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "Fresh Supplies API"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/freshroute"

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    FRONTEND_ORIGIN: str = "http://localhost:3000"
    REFRESH_COOKIE_NAME: str = "frs_refresh_token"
    COOKIE_SECURE: bool = False

    ML_MODEL_PATH: str = (
        "../post_harvest_data_engine/data/processed/food/food_model_inference.joblib"
    )
    ML_MARKET_PRICES_PATH: str = (
        "../post_harvest_data_engine/data/processed/food/market_prices.csv"
    )

    OTP_EXPIRE_MINUTES: int = 5
    OTP_RATE_LIMIT_PER_MINUTE: int = 3
    OTP_RATE_LIMIT_WINDOW_MINUTES: int = 10
    PHOTO_STORAGE_PATH: str = "./media/shipment_photos"
    PHOTO_MAX_LONG_EDGE: int = 1600
    PHOTO_JPEG_QUALITY: int = 80
    RECONCILIATION_INTERVAL_MINUTES: int = 5


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
