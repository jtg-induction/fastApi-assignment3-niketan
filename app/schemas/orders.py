from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.orders import OrderStatus


class OrderCreateRequest(BaseModel):
    restaurant_id: int
    coupon_code: str | None = Field(default=None, max_length=50)


class OrderStatusUpdateRequest(BaseModel):
    status: OrderStatus


class OrderItemResponse(BaseModel):
    id: int
    name: str
    menu_item_id: int | None
    price: int
    quantity: int
    model_config = ConfigDict(from_attributes=True)


class OrderRestaurantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    cuisine: str
    address: str
    mobile: str
    image: str | None = None
    is_veg_only: bool


class OrderResponse(BaseModel):
    id: int
    customer_id: int
    restaurant_id: int
    subtotal: Decimal
    booking_fee: Decimal
    discount_amount: Decimal
    total_price: Decimal
    status: OrderStatus
    order_items: list[OrderItemResponse]
    restaurant: OrderRestaurantResponse
    model_config = ConfigDict(from_attributes=True)


class OrderActionResponse(BaseModel):
    success: bool = True
    msg: str
    order: OrderResponse | None
