from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from app.core.constant import Messages


class FilterParams(BaseModel):
    veg_mode: bool = Field(default=False)
    search: str | None = Field(default=None)
    limit: int = Field(default=10, ge=1, le=30)
    offset: int = Field(default=0, ge=0)


class OperatingTimes(BaseModel):
    open: str = Field(examples=["09:00 AM"])
    close: str = Field(examples=["10:00 PM"])
    is_open: bool = Field(alias="isOpen")
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        serialize_by_alias=True,
    )


class OperatingHours(BaseModel):
    monday: OperatingTimes
    tuesday: OperatingTimes
    wednesday: OperatingTimes
    thrusday: OperatingTimes
    friday: OperatingTimes
    saturday: OperatingTimes
    sunday: OperatingTimes


class RestaurantBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    cuisine: str = Field(min_length=1, max_length=100)
    mobile: str = Field(
        examples=["+919053573774"], alias="mobileNumber", min_length=10, max_length=13
    )
    address: str = Field(min_length=1, max_length=255)
    image: HttpUrl
    is_veg_only: bool = Field(default=True, alias="isVegOnly")
    hours: OperatingHours
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        serialize_by_alias=True,
    )


class GetRestaurantResponse(RestaurantBase):
    id: int
    rating: float | None = Field(default=None, ge=0.0, le=5.0)


class RestaurantCreateResponse(GetRestaurantResponse):
    owner_id: int
    message: str = Messages.RESTAURANT_CREATED


class RestaurantUpdateResponse(BaseModel):
    id: int
    owner_id: int
    rating: float = Field(default=0.0, ge=0.0, le=5.0)
    model_config = ConfigDict(from_attributes=True)
