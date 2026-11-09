from enum import Enum

from pydantic import Field, PostgresDsn, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Messages(str, Enum):
    EMAIL_EXISTS = "Email already exists"
    AUTH_FAILED = "Email or password is incorrect"
    ACCOUNT_INACTIVE = "Your account is inactive. Please contact support."
    TOKEN_MISSING = "Refresh token missing"
    TOKEN_INVALID = "Invalid token"
    SESSION_EXPIRED = "Session expired or user inactive"
    TOKEN_WRONG = "Wrong token"
    USER_NOT_FOUND = "User not found"
    LOGIN_SUCCESS = "User logged in successfully"
    TOKEN_REFRESH_SUCCESS = "New Access Token generated successfully"
    LOGOUT_SUCCESS = "Logged out successfully"

    RESTAURANT_CREATED = "Restaurant created successfully"
    RESTAURANT_DELETED = "Restaurant deleted successfully"
    RESTAURANT_NOT_FOUND = "Restaurant not found"
    RESTAURANT_EDIT_FORBIDDEN = "Only owner can edit restaurant"
    RESTAURANT_DELETE_FORBIDDEN = "Only owner can delete restaurant"
    RESTAURANT_VIEW_FORBIDDEN = "You do not have permission to view this restaurant"
    RESTAURANT_NOT_OWNED = "You do not own this restaurant"

    MENU_ITEM_CREATED = "Menu item created successfully"
    MENU_ITEM_DELETED = "Menu item deleted successfully"
    MENU_ITEM_NOT_FOUND = "Menu item not found"
    MENU_ITEM_ADD_FORBIDDEN = "You do not have permission to add menu items to this restaurant"
    MENU_ITEM_EDIT_FORBIDDEN = "You do not have permission to edit items for this restaurant"
    MENU_ITEM_DELETE_FORBIDDEN = "You do not have permission to delete this menu item"


class Settings(BaseSettings):
    DATABASE_URL: PostgresDsn
    JWT_SECRET: SecretStr = Field(max_length=30)
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
