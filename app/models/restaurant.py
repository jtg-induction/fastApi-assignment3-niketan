from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.user import User


class Restaurant(Base):
    __tablename__ = "restaurants"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    ownerId: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    cuisine: Mapped[str] = mapped_column(nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    mobileNumber: Mapped[str] = mapped_column(nullable=False)
    address: Mapped[str] = mapped_column(nullable=False)
    image: Mapped[str] = mapped_column(nullable=False)
    isActive: Mapped[bool] = mapped_column(nullable=False, default=True)
    isVegOnly: Mapped[bool] = mapped_column(nullable=False, default=True)
    hours: Mapped[dict[str, any]] = mapped_column(JSONB, nullable=False)
    owner: Mapped["User"] = relationship("User", back_populates="restaurants")
