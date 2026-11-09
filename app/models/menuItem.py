from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.restaurant import Restaurant


class MenuItem(Base):
    __tablename__ = "menu_items"
    __table_args__ = (
        CheckConstraint("length(name) >= 2 AND length(name) <= 50", name="menu_item_name_len"),
        CheckConstraint("price >= 1", name="menu_item_price_min"),
        CheckConstraint("stock >= 0", name="menu_item_stock_min"),
        CheckConstraint("length(trim(description)) > 0", name="menu_item_desc_not_empty"),
        CheckConstraint("length(trim(category)) > 0", name="menu_item_category_not_empty"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    restaurant_id: Mapped[int] = mapped_column(
        ForeignKey("restaurants.id", ondelete="CASCADE"),
    )
    name: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    price: Mapped[int] = mapped_column()
    category: Mapped[str] = mapped_column()
    is_active: Mapped[bool] = mapped_column(default=True)
    stock: Mapped[int] = mapped_column(default=0)
    is_veg: Mapped[bool] = mapped_column(default=True)
    image: Mapped[str] = mapped_column()

    restaurant: Mapped["Restaurant"] = relationship("Restaurant", back_populates="menu_items")

    @validates("name")
    def validate_name(self, key: str, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Menu item name cannot be empty or whitespace.")
        stripped_value = value.strip()
        if not (2 <= len(stripped_value) <= 50):
            raise ValueError("Menu item name must be between 2 and 50 characters.")
        return stripped_value

    @validates("description", "category")
    def validate_empty_strings(self, key: str, value: str) -> str:
        if not value or not value.strip():
            raise ValueError(f"The field '{key}' cannot be blank.")
        return value.strip()

    @validates("price")
    def validate_price(self, key: str, value: int) -> int:
        if value < 1:
            raise ValueError("Price must be at least 1 unit.")
        return value

    @validates("stock")
    def validate_stock(self, key: str, value: int) -> int:
        if value < 0:
            raise ValueError("Stock balance cannot drop below 0 items.")
        return value

    def __repr__(self) -> str:
        return (
            f"<MenuItem(id={self.id!r}, name={self.name!r}, price={self.price!r}, "
            f"category={self.category!r}, restaurant_id={self.restaurant_id!r}, stock={self.stock!r})>"
        )
