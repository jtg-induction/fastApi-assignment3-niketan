from typing import TYPE_CHECKING, Any

from sqlalchemy import CheckConstraint, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.menu_item import MenuItem
    from app.models.cart import Cart
    from app.models.orders import Order
    from app.models.user import User


class Restaurant(Base):
    __tablename__ = "restaurants"
    __table_args__ = (
        CheckConstraint("length(name) >= 2 AND length(name) <= 50", name="restaurant_name_len"),
        CheckConstraint(
            "length(cuisine) >= 2 AND length(cuisine) <= 50", name="restaurant_cuisine_len"
        ),
        CheckConstraint(
            "length(mobile) >= 10 AND length(mobile) <= 15", name="restaurant_mobile_fmt"
        ),
        CheckConstraint("rating >= 0.0 AND rating <= 5.0", name="restaurant_rating_range"),
        CheckConstraint("length(trim(address)) > 0", name="restaurant_address_not_empty"),
    )
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column()
    cuisine: Mapped[str] = mapped_column()
    rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    mobile: Mapped[str] = mapped_column()
    address: Mapped[str] = mapped_column(String(255))
    image: Mapped[str] = mapped_column()
    is_veg_only: Mapped[bool] = mapped_column(default=True)
    hours: Mapped[dict[str, Any]] = mapped_column(JSONB)
    owner: Mapped["User"] = relationship("User", back_populates="restaurants")
    menu_items: Mapped[list["MenuItem"]] = relationship(
        "MenuItem",
        back_populates="restaurant",
        cascade="all, delete-orphan",
        lazy="raise",
    )
    carts: Mapped[list["Cart"]] = relationship(
        "Cart", back_populates="restaurant", cascade="all, delete-orphan"
    )
    orders: Mapped[list["Order"]] = relationship(
        "Order", back_populates="restaurant", cascade="all, delete-orphan"
    )

    carts: Mapped[list["Cart"]] = relationship(
        "Cart", back_populates="restaurant", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"<Restaurant(id={self.id!r}, name={self.name!r}, "
            f"cuisine={self.cuisine!r}, owner_id={self.owner_id!r})>"
        )
