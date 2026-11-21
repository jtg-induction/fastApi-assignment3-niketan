from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.orders import OrderStatus


class OrderCreateRequest(BaseModel):
    restaurant_id: int = Field(alias="restaurantId")
    coupon_code: str | None = Field(default=None, max_length=50, alias="couponCode")

    model_config = ConfigDict(populate_by_name=True)


class OrderStatusUpdateRequest(BaseModel):
    status: OrderStatus


class OrderItemResponse(BaseModel):
    id: int
    name: str
    menu_item_id: int | None = Field(alias="menuItemId")
    price: float
    quantity: int

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        serialize_by_alias=True,
    )


class OrderRestaurantResponse(BaseModel):
    id: int
    owner_id: int = Field(alias="ownerId")
    name: str
    cuisine: str
    rating: float | None = Field(default=None)
    address: str
    mobile: str = Field(alias="mobileNumber")
    image: str = ""
    is_veg_only: bool = Field(alias="isVegOnly")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        serialize_by_alias=True,
    )


class OrderCustomerResponse(BaseModel):
    id: int
    name: str
    address: str | None = None
    mobile: str | None = None

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    id: int
    customer_id: int = Field(alias="customerId")
    restaurant_id: int = Field(alias="restaurantId")
    subtotal: float
    booking_fee: float = Field(alias="bookingFee")
    discount_amount: float = Field(alias="discountAmount")
    total_price: float = Field(alias="totalPrice")
    status: OrderStatus
    created_at: datetime | None = Field(default=None, alias="createdAt")
    order_items: list[OrderItemResponse] = Field(alias="items")
    restaurant: OrderRestaurantResponse
    customer: OrderCustomerResponse

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        serialize_by_alias=True,
    )


class OrderActionResponse(BaseModel):
    success: bool = True
    msg: str
    order: OrderResponse | None = None
