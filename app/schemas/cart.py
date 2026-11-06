from pydantic import BaseModel, ConfigDict, Field


class CartItemBase(BaseModel):
    menuItemId: int = Field(alias="menu_item_id")
    count: int = Field(ge=1)
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class CartItemCreateUpdate(BaseModel):
    menuItemId: int
    count: int = Field(ge=1)


class CartItemResponse(CartItemBase):
    id: int
    cartId: int = Field(alias="cart_id")

    model_config = ConfigDict(from_attributes=True)


class CartBase(BaseModel):
    restaurantId: int


class CartCreate(CartBase):
    pass


class CartResponse(BaseModel):
    id: int
    userId: int = Field(alias="user_id")
    restaurantId: int = Field(alias="restaurant_id")
    items: list[CartItemResponse] = Field(default=[], alias="cart_items")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class AddToCartRequest(BaseModel):
    restaurantId: int
    menuItemId: int
    count: int = Field(default=1, ge=1)


class CartUpdateRequest(BaseModel):
    restaurantId: int
    menuItemId: int
    count: int = Field(ge=0, description="Set to 0 to remove the item from the cart")


class UpdateCartItemRequest(BaseModel):
    count: int = Field(ge=0)


class CartActionResponse(BaseModel):
    success: bool = True
    message: str
    cart: CartResponse | None = None
