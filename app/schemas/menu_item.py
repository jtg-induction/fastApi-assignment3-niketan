from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class FilterParams(BaseModel):
    limit: int = Field(default=10, ge=1)
    offset: int = Field(default=0, ge=0)


class MenuItemBase(BaseModel):
    restaurant_id: int
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(max_length=500)
    price: Decimal = Field(ge=0)
    category: str
    is_veg: bool = Field(alias="isVeg")
    stock: int = Field(ge=0)
    image: HttpUrl
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, serialize_by_alias=True)


class MenuItemUpdateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(max_length=500)
    price: Decimal = Field(ge=0)
    category: str
    is_veg: bool = Field(alias="isVeg")
    stock: int = Field(ge=0)
    image: HttpUrl
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, serialize_by_alias=True)


class MenuItemCreateResponse(MenuItemBase):
    created_at: datetime
    updated_at: datetime
    id: int
    message: str


class MenuItemUpdateResponse(MenuItemUpdateRequest):
    id: int
    created_at: datetime
    updated_at: datetime
