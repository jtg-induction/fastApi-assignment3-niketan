from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class FilterParams(BaseModel):
    veg_mode: bool = Field(default=False)
    search: str | None = Field(default=None)
    limit: int = Field(default=10, ge=1, le=30)
    offset: int = Field(default=0, ge=0)


class OperatingTImes(BaseModel):
    open: str = Field(examples=["09:00 AM"])
    close: str = Field(examples=["10:00 PM"])
    is_open: bool


class OperatingHours(BaseModel):
    monday: OperatingTImes
    tuesday: OperatingTImes
    wednesday: OperatingTImes
    thrusday: OperatingTImes
    friday: OperatingTImes
    saturday: OperatingTImes
    sunday: OperatingTImes


class RestaurantBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    cuisine: str = Field(min_length=1, max_length=100)
    mobile: str = Field(examples=["+919053573774"])
    address: str = Field(min_length=1, max_length=255)
    rating: float = Field(default=0.0, ge=0.0, le=5.0)
    image: HttpUrl
    is_veg_only: bool = True
    hours: OperatingHours


class RestaurantCreateResponse(RestaurantBase):
    id: int
    owner_id: int
    message: str


class RestaurantUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    cuisine: str | None = Field(default=None, min_length=1, max_length=100)
    mobile: str | None = Field(default=None, alias="mobile")
    address: str | None = Field(default=None, min_length=1, max_length=255)
    image: HttpUrl | None = Field(default=None)
    is_veg_only: bool | None = Field(default=None, alias="isVegOnly")
    hours: OperatingHours | None = Field(default=None)


class RestaurantUpdateResponse(BaseModel):
    id: int
    owner_id: int
    rating: float = Field(default=0.0, ge=0.0, le=5.0)
    model_config = ConfigDict(from_attributes=True)
