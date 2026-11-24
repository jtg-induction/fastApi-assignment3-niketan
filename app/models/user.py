from datetime import datetime
from typing import TYPE_CHECKING

from pwdlib import PasswordHash
from sqlalchemy import CheckConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.restaurant import Restaurant
from app.types.user import UserRole

if TYPE_CHECKING:
    from app.models.cart import Cart
    from app.models.orders import Order
    from app.models.restaurant import Restaurant

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
    restaurants: Mapped[list["Restaurant"]] = relationship(
        "Restaurant", back_populates="owner", cascade="all, delete-orphan"
    )
    carts: Mapped[list["Cart"]] = relationship(
        "Cart", back_populates="user", cascade="all, delete-orphan", lazy="raise"
    )
    orders: Mapped[list["Order"]] = relationship(
            "Order", back_populates="customer", cascade="all, delete-orphan"
        )
    def __repr__(self) -> str:
        return (
            f"User(id={self.id!r}, "
            f"name={self.name!r}, "
            f"email={self.email!r}, "
            f"mobile={self.mobile!r}, "
            f"role={self.role!r})"
        )
