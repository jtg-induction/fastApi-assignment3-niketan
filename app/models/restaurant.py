import re
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Float, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.db.session import Base

if TYPE_CHECKING:
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
    rating: Mapped[float] = mapped_column(Float, default=0.0)
    mobile: Mapped[str] = mapped_column()
    address: Mapped[str] = mapped_column()
    image: Mapped[str] = mapped_column()
    is_veg_only: Mapped[bool] = mapped_column(default=True)
    hours: Mapped[dict[str, any]] = mapped_column(JSONB)
    owner: Mapped["User"] = relationship("User", back_populates="restaurants")

    @validates("name", "cuisine")
    def validate_lengths(self, key: str, value: str) -> str:
        if not value or not value.strip():
            raise ValueError(f"The field '{key}' cannot be empty or whitespace.")
        stripped_value = value.strip()
        if not (2 <= len(stripped_value) <= 50):
            raise ValueError(f"The field '{key}' must be between 2 and 50 characters.")
        return stripped_value

    @validates("rating")
    def validate_rating(self, key: str, value: float) -> float:
        if not (0.0 <= value <= 5.0):
            raise ValueError("The restaurant rating must strictly fall between 0.0 and 5.0.")
        return round(float(value), 2)

    @validates("mobile")
    def validate_mobile(self, key: str, value: str) -> str:
        cleaned_mobile = re.sub(r"[\s\-()+\.]", "", value)
        if not cleaned_mobile.isdigit():
            raise ValueError("Mobile numbers must contain numeric digits only.")
        if not (10 <= len(cleaned_mobile) <= 15):
            raise ValueError("Mobile length must be between 10 and 15 digits.")
        return cleaned_mobile

    @validates("address")
    def validate_address(self, key: str, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("The physical address column cannot be blank.")
        return value.strip()
