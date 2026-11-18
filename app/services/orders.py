from decimal import Decimal

from fastapi import status

from app.core.config import settings
from app.models.orders import Order, OrderItem, OrderStatus
from app.repositories.orders import OrderRepository
from app.schemas.orders import (
    OrderActionResponse,
    OrderCreateRequest,
    OrderResponse,
    OrderStatusUpdateRequest,
)
from app.utils.utils import raise_http_error

ALLOWED_STATUS_TRANSITIONS: dict[OrderStatus, set[OrderStatus]] = {
    OrderStatus.PENDING: {OrderStatus.ACCEPTED, OrderStatus.REJECTED},
    OrderStatus.ACCEPTED: {OrderStatus.PREPARING, OrderStatus.REJECTED},
    OrderStatus.PREPARING: {OrderStatus.OUT_FOR_DELIVERY},
    OrderStatus.OUT_FOR_DELIVERY: {OrderStatus.DELIVERED},
    OrderStatus.DELIVERED: set(),
    OrderStatus.REJECTED: set(),
}


class OrderService:
    def __init__(self, order_repo: OrderRepository):
        self.order_repo = order_repo

    async def create_order(self, user_id: int, request: OrderCreateRequest) -> OrderActionResponse:
        cart = await self.order_repo.get_cart_for_checkout(user_id, request.restaurant_id)
        if not cart or not cart.cart_items:
            raise_http_error(status.HTTP_404_NOT_FOUND, "active cart not found")
        menu_items_ids = [item.menu_item_id for item in cart.cart_items]
        locked_menu_items = await self.order_repo.get_menu_items_for_update(menu_items_ids)
        print(locked_menu_items)
        subtotal = Decimal("0.00")
        order_items_to_create: list[OrderItem] = []
        for cart_item in cart.cart_items:
            print(cart_item)
            menu_item = locked_menu_items.get(cart_item.menu_item_id)
            if not menu_item:
                raise_http_error(
                    status_code=status.HTTP_404_NOT_FOUND, detail="MENU_ITEM_NOT_FOUND"
                )

            if menu_item.stock < cart_item.count:
                raise_http_error(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient stock for '{menu_item.name}'. Available: {menu_item.stock}",
                )
            menu_item.stock -= cart_item.count

            item_price = Decimal(str(menu_item.price))
            subtotal += item_price * cart_item.count

            order_items_to_create.append(
                OrderItem(
                    menu_item_id=menu_item.id,
                    name=menu_item.name,
                    price=item_price,
                    quantity=cart_item.count,
                )
            )
        booking_fee = settings.BOOKING_FEE

        if subtotal >= settings.DISCOUNT_THRESHOLD:
            discounted_amount = (subtotal * settings.DISCOUNT_PERCENTAGE).quantize(Decimal("0.01"))
        else:
            discounted_amount = Decimal("0.00")

        total_price = max(
            Decimal("0.00"),
            subtotal + booking_fee - discounted_amount,
        )

        new_order = Order(
            customer_id=user_id,
            restaurant_id=request.restaurant_id,
            subtotal=subtotal,
            booking_fee=booking_fee,
            discount_amount=discounted_amount,
            total_price=total_price,
            status=OrderStatus.PENDING,
        )

        created_order = await self.order_repo.create_order(
            order=new_order,
            order_items=order_items_to_create,
            cart=cart,
        )
        await self.order_repo.db.commit()
        return OrderActionResponse(
            success=True,
            msg="Order placed successfully.",
            order=created_order,
        )

    async def get_order_details(self, user_id, order_id) -> OrderResponse:
        order = await self.order_repo.get_order_by_id(order_id)
        if not order:
            raise_http_error(404, "order not found")
        if order.customer_id != user_id or order.restaurant.owner_id != user_id:
            raise_http_error(403, "not authorized to view this order")
        return order

    async def get_all_orders(self, user_id: int) -> list[OrderResponse]:
        orders = await self.order_repo.get_all_orders(user_id)
        return [OrderResponse.model_validate(o) for o in orders]

    async def update_order_status(
        self, order_id: int, owner_id: int, request: OrderStatusUpdateRequest
    ) -> OrderActionResponse:
        """Allows only the restaurant owner to transition order status; restores stock on REJECTED."""
        order = await self.order_repo.get_order_for_update(order_id=order_id)
        if not order:
            raise_http_error(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found.",
            )

        restaurant_owner_id = order.restaurant.owner_id
        if restaurant_owner_id != owner_id:
            raise_http_error(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the owner of this restaurant can update the order status.",
            )

        if order.status == request.status:
            return OrderActionResponse(
                success=True,
                msg=f"Order status is already {order.status.value}.",
                order=OrderResponse.model_validate(order),
            )

        allowed_next = ALLOWED_STATUS_TRANSITIONS.get(order.status, set())
        if request.status not in allowed_next:
            raise_http_error(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot transition order from {order.status.value} to {request.status.value}.",
            )

        if request.status == OrderStatus.REJECTED:
            item_ids = [
                item.menu_item_id for item in order.order_items if item.menu_item_id is not None
            ]
            locked_items = await self.order_repo.get_menu_items_for_update(item_ids)
            for order_item in order.order_items:
                if order_item.menu_item_id and order_item.menu_item_id in locked_items:
                    locked_items[order_item.menu_item_id].stock += order_item.quantity

        order.status = request.status
        await self.order_repo.db.commit()

        updated_order = await self.order_repo.get_order_by_id(order.id)
        return OrderActionResponse(
            success=True,
            msg=f"Order status updated to {request.status.value}.",
            order=OrderResponse.model_validate(updated_order),
        )
