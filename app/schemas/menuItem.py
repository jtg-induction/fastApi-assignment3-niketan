from pydantic import BaseModel, Field, HttpUrl


class FilterParams(BaseModel):
    limit: int = Field(default=10, ge=1, le=30)
    offset: int = Field(default=0, ge=0)


class MenuItemBase(BaseModel):
    restaurantId: int
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(max_length=500)
    price: int = Field(ge=0)
    category: str
    isVeg: bool
    stock: int = Field(ge=0)
    image: HttpUrl


class MenuItemUpdateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(max_length=500)
    price: int = Field(ge=0)
    category: str
    isVeg: bool
    stock: int = Field(ge=0)
    image: HttpUrl


class MenuItemCreateResponse(MenuItemBase):
    id: int
    message: str


class MenuItemUpdateResponse(MenuItemUpdateRequest):
    id: int


class MenuItemDeleteResponse(BaseModel):
    id: int
    message: str = "Menu item deleted successfully"
    success: bool = True
