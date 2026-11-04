from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class FilterParams(BaseModel):
    vegMode: bool = Field(default=False)
    search: str | None = Field(default=None)
    limit: int = Field(default=10, ge=1, le=30)
    offset: int = Field(default=0, ge=0)


class operatingTimes(BaseModel):
    open: str
    close: str
    isOpen: bool


class operatingHours(BaseModel):
    monday: operatingTimes
    tuesday: operatingTimes
    wednesday: operatingTimes
    thrusday: operatingTimes
    friday: operatingTimes
    saturday: operatingTimes
    sunday: operatingTimes


class RestaurantBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    cuisine: str
    mobileNumber: str = Field(..., examples=["+919053573774"])
    address: str
    rating: float
    image: HttpUrl
    isVegOnly: bool = True
    hours: operatingHours


class RestaurantCreateResponse(RestaurantBase):
    id: int
    ownerId: int
    message: str


class RestaurantUpdate(BaseModel):
    name: str | None
    cuisine: str | None
    mobileNumber: str | None = None
    address: str | None = None
    image: str | None = None
    isVegOnly: bool | None = None
    hours: operatingHours | None = None


class RestaurantUpdateResponse(BaseModel):
    id: int
    ownerId: int
    rating: float = 0.0
    model_config = ConfigDict(from_attributes=True)
