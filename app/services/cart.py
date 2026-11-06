from fastapi import HTTPException, status

from app.core.config import Messages
from app.repositories.cart import CartRepository
from app.schemas.cart import (
    CartActionResponse,
    CartResponse,
    CartUpdateRequest,
)


class CartService:
    def __init__(self, cart_repo: CartRepository):
        self.cart_repo = cart_repo

    async def get_all_user_carts(self, user_id: int) -> list[CartResponse]:
        """Returns all active carts for the user."""
        carts = await self.cart_repo.get_all_carts_by_user(user_id=user_id)
        return [CartResponse.model_validate(cart) for cart in carts]

    async def get_cart_for_restaurant(self, user_id: int, restaurant_id: int) -> CartResponse:
        """Returns a single cart for a user and restaurant combination."""
        cart = await self.cart_repo.get_cart_by_user_and_restaurant(
            user_id=user_id, restaurant_id=restaurant_id
        )
        if not cart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=Messages.CART_ACTIVE_NOT_FOUND,
            )
        return CartResponse.model_validate(cart)

    async def update_cart(self, user_id: int, request: CartUpdateRequest) -> CartActionResponse:
        """Creates the cart if needed, updates item quantity, and cleans up empty carts."""
        restaurant = await self.cart_repo.get_restaurant_by_id(request.restaurantId)
        if not restaurant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=Messages.RESTAURANT_NOT_FOUND,
            )

        menu_item = await self.cart_repo.get_menu_item_by_id(request.menuItemId)
        if not menu_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=Messages.MENU_ITEM_NOT_FOUND,
            )

        if menu_item.restaurant_id != request.restaurantId:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=Messages.CART_ITEM_WRONG_RESTAURANT,
            )

        cart = await self.cart_repo.get_cart_by_user_and_restaurant(
            user_id=user_id, restaurant_id=request.restaurantId
        )

        if request.count > 0:
            if menu_item.stock <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=Messages.CART_ITEM_OUT_OF_STOCK.format(name=menu_item.name),
                )
            if request.count > menu_item.stock:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=Messages.CART_ITEM_INSUFFICIENT_STOCK.format(
                        stock=menu_item.stock, name=menu_item.name
                    ),
                )

        if not cart:
            if request.count == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=Messages.CART_DOES_NOT_EXIST,
                )
            cart = await self.cart_repo.create_cart(
                user_id=user_id, restaurant_id=request.restaurantId
            )

        updated_cart = await self.cart_repo.upsert_cart_item(
            cart_id=cart.id,
            menu_item_id=request.menuItemId,
            count=request.count,
        )
        cart_data = CartResponse.model_validate(updated_cart) if updated_cart else None
        await self.cart_repo.db.commit()

        if not cart_data:
            return CartActionResponse(
                success=True,
                message=Messages.CART_ITEM_REMOVED_EMPTY,
                cart=None,
            )

        return CartActionResponse(
            success=True,
            message=Messages.CART_UPDATED,
            cart=cart_data,
        )

    async def delete_cart(self, cart_id: int, user_id: int) -> CartActionResponse:
        cart = await self.cart_repo.get_cart_by_id(cart_id=cart_id)
        if not cart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart not found.",
            )
        if cart.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=Messages.CART_DELETE_FORBIDDEN,
            )

        await self.cart_repo.delete_cart(cart=cart)
        await self.cart_repo.db.commit()

        return CartActionResponse(
            success=True,
            message=Messages.CART_DELETED,
            cart=None,
        )
