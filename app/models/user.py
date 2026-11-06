import re
from datetime import datetime

from pwdlib import PasswordHash
from sqlalchemy import CheckConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, validates

from app.db.session import Base
from app.types.user import UserRole

pwd_context = PasswordHash.recommended()


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("length(name) >= 2 AND length(name) <= 50", name="user_name_len"),
        CheckConstraint("length(mobile) >= 10 AND length(mobile) <= 15", name="user_mobile_len"),
    )

    name: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column(unique=True, index=True)
    password: Mapped[str] = mapped_column()
    mobile: Mapped[str] = mapped_column()
    address: Mapped[str] = mapped_column()
    role: Mapped[UserRole] = mapped_column()
    refresh_token: Mapped[str | None] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    @validates("name")
    def validate_name(self, key, value) -> str:
        if not (2 <= len(value) <= 50):
            raise ValueError("Name must be between 2 and 50 characters.")
        return value

    @validates("mobile")
    def validate_mobile(self, key, value) -> str:
        if not re.match(r"^\+?[1-9]\d{9,14}$", value):
            raise ValueError("Invalid mobile number format. Must be 10-15 digits.")
        return value

    @validates("refresh_token")
    def validate_and_hash_refresh_token(self, key, value) -> str | None:
        if value is None:
            return None
        return pwd_context.hash(value)

    def __repr__(self) -> str:
        return (
            f"User(id={self.id!r}, "
            f"name={self.name!r}, "
            f"email={self.email!r}, "
            f"mobile={self.mobile!r}, "
            f"role={self.role!r})"
        )
