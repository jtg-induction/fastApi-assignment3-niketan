from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.restaurant import Restaurant

if TYPE_CHECKING:
    from app.models.restaurant import Restaurant


class UserRole(str, Enum):
    OWNER = "OWNER"
    CUSTOMER = "CUSTOMER"


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    mobile: Mapped[str] = mapped_column(nullable=False)
    address: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[UserRole] = mapped_column(nullable=False)
    isActive: Mapped[bool] = mapped_column(nullable=False, default=True)
    refreshToken: Mapped[str] = mapped_column(nullable=True)
    restaurants: Mapped[list["Restaurant"]] = relationship(
        "Restaurant", back_populates="owner", cascade="all, delete-orphan"
    )
