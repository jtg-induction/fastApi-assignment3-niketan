from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.middleware.auth import get_current_user_id, get_customer_user_id, get_owner_user_id
from app.models.user import User
from app.repositories.orders import OrderRepository
from app.schemas.orders import (
    OrderActionResponse,
    OrderCreateRequest,
    OrderResponse,
    OrderStatusUpdateRequest,
)
from app.services.orders import OrderService

order_router = APIRouter(prefix="/orders", tags=["orders"])


@order_router.post(
    "/create", status_code=status.HTTP_201_CREATED, response_model=OrderActionResponse
)
async def create_order(
    body_data: OrderCreateRequest,
    customer_id: Annotated[User, Depends(get_customer_user_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    order_repo = OrderRepository(db)
    order_service = OrderService(order_repo)
    return await order_service.create_order(user_id=customer_id, request=body_data)


@order_router.get("/all", response_model=list[OrderResponse], status_code=status.HTTP_200_OK)
async def get_all_orders(
    current_user: Annotated[User, Depends(get_current_user_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    order_repo = OrderRepository(db)
    order_service = OrderService(order_repo)
    return await order_service.get_all_orders(user_id=current_user)


@order_router.patch("/{order_id}/status", response_model=OrderActionResponse)
async def update_order_status(
    order_id: int,
    request: OrderStatusUpdateRequest,
    owner_id: Annotated[int, Depends(get_owner_user_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Updates the status of an order (restricted to the restaurant owner)."""
    order_repo = OrderRepository(db)
    order_service = OrderService(order_repo)
    return await order_service.update_order_status(
        order_id=order_id, owner_id=owner_id, request=request
    )


@order_router.get("/{order_id}", response_model=OrderResponse, status_code=status.HTTP_200_OK)
async def get_order_by_id(
    order_id: int,
    current_user: Annotated[User, Depends(get_current_user_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    order_repo = OrderRepository(db)
    order_service = OrderService(order_repo)
    return await order_service.get_order_details(user_id=current_user, order_id=order_id)
