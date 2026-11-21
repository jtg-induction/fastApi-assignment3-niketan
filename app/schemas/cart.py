from pydantic import BaseModel, ConfigDict, Field


class CartItemBase(BaseModel):
    menu_item_id: int = Field(alias="menuItemId")
    count: int = Field(ge=1)

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        serialize_by_alias=True,
    )


class CartItemCreateUpdate(BaseModel):
    menu_item_id: int = Field(alias="menuItemId")
    count: int = Field(ge=1)

    model_config = ConfigDict(populate_by_name=True)


class CartItemResponse(CartItemBase):
    id: int
    cart_id: int = Field(alias="cartId")

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


class CartResponse(BaseModel):
    id: int
    user_id: int = Field(alias="userId")
    restaurant_id: int = Field(alias="restaurantId")
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
