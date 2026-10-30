from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.middleware.auth import get_current_user_id
from app.repositories.cart import CartRepository
from app.schemas.cart import (
    CartActionResponse,
    CartResponse,
    CartUpdateRequest,
)
from app.services.cart import CartService

cart_router = APIRouter(prefix="/carts", tags=["Cart Management"])


def get_cart_service(db: Annotated[AsyncSession, Depends(get_db)]) -> CartService:
    return CartService(CartRepository(db))


@cart_router.get("/all", response_model=list[CartResponse])
async def get_all_carts(
    cart_service: Annotated[CartService, Depends(get_cart_service)],
    user_id: Annotated[int, Depends(get_current_user_id)],
):
    """Retrieves all active carts belonging to the authenticated user.

    Args:
        cart_service: Injected service handling cart operations.
        user_id: ID of the authenticated user.

    Returns:
        list[CartResponse]: All active carts and their items for the user.
    """
    return await cart_service.get_all_user_carts(user_id=user_id)


@cart_router.get("/restaurant/{restaurant_id}", response_model=CartResponse)
async def get_cart_by_restaurant(
    restaurant_id: int,
    cart_service: Annotated[CartService, Depends(get_cart_service)],
    user_id: Annotated[int, Depends(get_current_user_id)],
):
    """Retrieves the active cart for a specific restaurant and user.

    Args:
        restaurant_id: Primary key ID of the target restaurant.
        cart_service: Injected service handling cart operations.
        user_id: ID of the authenticated user.

    Returns:
        CartResponse: The user's active cart for the specified restaurant.
    """
    return await cart_service.get_cart_for_restaurant(user_id=user_id, restaurant_id=restaurant_id)


@cart_router.put("/", response_model=CartActionResponse)
async def update_cart(
    body_data: CartUpdateRequest,
    cart_service: Annotated[CartService, Depends(get_cart_service)],
    user_id: Annotated[int, Depends(get_current_user_id)],
):
    """Creates or updates a cart item quantity and removes empty carts.

    Args:
        body_data: Request payload containing restaurant ID, menu item ID, and count.
        cart_service: Injected service handling cart operations.
        user_id: ID of the authenticated user.

    Returns:
        CartActionResponse: Confirmation message and updated cart details, if any.
    """
    return await cart_service.update_cart(user_id=user_id, request=body_data)


@cart_router.delete("/{cart_id}", response_model=CartActionResponse)
async def delete_cart(
    cart_id: int,
    cart_service: Annotated[CartService, Depends(get_cart_service)],
    user_id: Annotated[int, Depends(get_current_user_id)],
):
    """Deletes a specific cart owned by the authenticated user.

    Args:
        cart_id: Primary key ID of the cart to delete.
        cart_service: Injected service handling cart operations.
        user_id: ID of the authenticated user.

    Returns:
        CartActionResponse: Confirmation message indicating the cart was deleted.
    """
    return await cart_service.delete_cart(cart_id=cart_id, user_id=user_id)
