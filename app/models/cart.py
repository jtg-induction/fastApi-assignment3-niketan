from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.menuItem import MenuItem
    from app.models.restaurant import Restaurant
    from app.models.user import User


class Cart(Base):
    """Represents an active shopping cart linking a user to a specific restaurant."""

    __tablename__ = "carts"
    __table_args__ = (UniqueConstraint("user_id", "restaurant_id", name="uq_user_restaurant_cart"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    restaurant_id: Mapped[int] = mapped_column(
        ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False
    )
    user: Mapped["User"] = relationship("User", back_populates="carts")
    restaurant: Mapped["Restaurant"] = relationship("Restaurant", back_populates="carts")
    cart_items: Mapped[list["CartItem"]] = relationship(
        "CartItem", back_populates="cart", cascade="all, delete-orphan"
    )


class CartItem(Base):
    __tablename__ = "cart_items"
    __table_args__ = (
        CheckConstraint("count >= 1", name="cart_item_count_min"),
        UniqueConstraint("cart_id", "menu_item_id", name="uq_cart_menu_item"),
    )
    """Represents an individual menu item and its quantity inside a shopping cart."""
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    cart_id: Mapped[int] = mapped_column(ForeignKey("carts.id", ondelete="CASCADE"), nullable=False)
    menu_item_id: Mapped[int] = mapped_column(
        ForeignKey("menu_items.id", ondelete="CASCADE"), nullable=False
    )
    count: Mapped[int] = mapped_column(default=1)

    cart: Mapped["Cart"] = relationship("Cart", back_populates="cart_items")
    menu_item: Mapped["MenuItem"] = relationship("MenuItem")

    @validates("count")
    def validate_count(self, key: str, value: int) -> int:
        if value < 1:
            raise ValueError("Item quantity count in cart must be at least 1.")
        return value

    def __repr__(self) -> str:
        return (
            f"<CartItem(id={self.id!r}, cart_id={self.cart_id!r}, "
            f"menu_item_id={self.menu_item_id!r}, count={self.count!r})>"
        )
