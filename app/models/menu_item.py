from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.restaurant import Restaurant


class MenuItem(Base):
    __tablename__ = "menu_items"
    __table_args__ = (
        UniqueConstraint("restaurant_id", "name", name="uq_restaurant_menu_item_name"),
        CheckConstraint("length(name) >= 2 AND length(name) <= 50", name="menu_item_name_len"),
        CheckConstraint("price >= 1", name="menu_item_price_min"),
        CheckConstraint("stock >= 0", name="menu_item_stock_min"),
        CheckConstraint("length(trim(description)) > 0", name="menu_item_desc_not_empty"),
        CheckConstraint("length(trim(category)) > 0", name="menu_item_category_not_empty"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    restaurant_id: Mapped[int] = mapped_column(
        ForeignKey("restaurants.id", ondelete="CASCADE"),
        index=True,
    )
    name: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(String(500))
    price: Mapped[Decimal] = mapped_column()
    category: Mapped[str] = mapped_column(String(50))
    is_active: Mapped[bool] = mapped_column(default=True)
    stock: Mapped[int] = mapped_column(default=0)
    is_veg: Mapped[bool] = mapped_column(default=True)
    image: Mapped[str] = mapped_column(String(2048))

    restaurant: Mapped["Restaurant"] = relationship("Restaurant", back_populates="menu_items")

    def __repr__(self) -> str:
        return (
            f"<MenuItem(id={self.id!r}, name={self.name!r}, price={self.price!r}, "
            f"category={self.category!r}, restaurant_id={self.restaurant_id!r}, stock={self.stock!r})>"
        )
