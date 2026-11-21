from pydantic import BaseModel, ConfigDict, Field


class CartItemBase(BaseModel):
    menu_item_id: int = Field(alias="menuItemId")
    count: int = Field(ge=1)

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        serialize_by_alias=True,
    )


class CartMenuItemResponse(BaseModel):
    id: int
    restaurant_id: int = Field(alias="restaurantId")
    name: str
    description: str | None = None
    price: float
    category: str
    is_veg: bool = Field(alias="isVeg")
    image: str | None = None
    stock: int

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        serialize_by_alias=True,
    )


class CartItemCreateUpdate(BaseModel):
    menu_item_id: int = Field(alias="menuItemId")
    count: int = Field(ge=1)

    model_config = ConfigDict(populate_by_name=True)


class CartItemResponse(BaseModel):
    id: int
    menu_item_id: int = Field(alias="menuItemId")
    count: int
    menu_item: CartMenuItemResponse = Field(alias="menuItem")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        serialize_by_alias=True,
    )


class CartBase(BaseModel):
    restaurant_id: int = Field(alias="restaurantId")

    model_config = ConfigDict(populate_by_name=True)


class CartCreate(CartBase):
    pass


class CartRestaurantResponse(BaseModel):
    id: int
    owner_id: int = Field(alias="ownerId")
    name: str
    cuisine: str
    rating: float | None = None
    address: str
    mobile: str = Field(alias="mobileNumber")
    image: str = ""
    is_veg_only: bool = Field(alias="isVegOnly")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        serialize_by_alias=True,
    )


class CartResponse(BaseModel):
    id: int
    user_id: int = Field(alias="userId")
    restaurant_id: int = Field(alias="restaurantId")
    restaurant: CartRestaurantResponse
    cart_items: list[CartItemResponse] = Field(default=[], alias="items")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        serialize_by_alias=True,
    )


class AddToCartRequest(BaseModel):
    restaurant_id: int = Field(alias="restaurantId")
    menu_item_id: int = Field(alias="menuItemId")
    count: int = Field(default=1, ge=1)

    model_config = ConfigDict(populate_by_name=True)


class CartUpdateRequest(BaseModel):
    restaurant_id: int = Field(alias="restaurantId")
    menu_item_id: int = Field(alias="menuItemId")
    count: int = Field(ge=0, description="Set to 0 to remove the item from the cart")

    model_config = ConfigDict(populate_by_name=True)


class UpdateCartItemRequest(BaseModel):
    count: int = Field(ge=0)


class CartActionResponse(BaseModel):
    success: bool = True
    message: str
    cart: CartResponse | None = None
