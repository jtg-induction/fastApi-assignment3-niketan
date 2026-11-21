from decimal import Decimal

from pydantic import Field, PostgresDsn, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: PostgresDsn
    JWT_SECRET: SecretStr = Field(max_length=30)
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    BOOKING_FEE: Decimal = Decimal("20.00")
    DISCOUNT_THRESHOLD: Decimal = Decimal("500.00")
    DISCOUNT_PERCENTAGE: Decimal = Decimal("0.10")
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
