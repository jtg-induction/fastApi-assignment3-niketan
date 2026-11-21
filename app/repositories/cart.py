from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.cart import Cart, CartItem


class CartRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_cart_by_id(self, cart_id: int) -> Cart | None:
        query = (
            select(Cart)
            .options(selectinload(Cart.cart_items))
            .where(Cart.id == cart_id)
            .execution_options(populate_existing=True)
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_all_carts_by_user(self, user_id: int) -> list[Cart]:
        query = (
            select(Cart)
            .options(selectinload(Cart.cart_items))
            .where(Cart.user_id == user_id)
            .order_by(Cart.id.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_cart_by_user_and_restaurant(
        self, user_id: int, restaurant_id: int
    ) -> Cart | None:
        query = (
            select(Cart)
            .options(selectinload(Cart.cart_items))
            .where(Cart.user_id == user_id, Cart.restaurant_id == restaurant_id)
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def create_cart(self, user_id: int, restaurant_id: int) -> Cart:
        """Stages a new empty cart and flushes to get its ID."""
        new_cart = Cart(user_id=user_id, restaurant_id=restaurant_id)
        self.db.add(new_cart)
        await self.db.flush()
        return await self.get_cart_by_id(new_cart.id)

    async def upsert_cart_item(self, cart_id: int, menu_item_id: int, count: int) -> Cart | None:
        if count == 0:
            await self.db.execute(
                delete(CartItem).where(
                    CartItem.cart_id == cart_id,
                    CartItem.menu_item_id == menu_item_id,
                )
            )
        else:
            stmt = (
                pg_insert(CartItem)
                .values(
                    cart_id=cart_id,
                    menu_item_id=menu_item_id,
                    count=count,
                )
                .on_conflict_do_update(
                    constraint="uq_cart_menu_item",  # or index_elements=["cart_id", "menu_item_id"]
                    set_={"count": count},
                )
            )
            await self.db.execute(stmt)
        await self.db.flush()

        updated_cart = await self.get_cart_by_id(cart_id)
        if updated_cart and len(updated_cart.cart_items) == 0:
            await self.db.delete(updated_cart)
            await self.db.flush()
            return None

        return updated_cart

    async def delete_cart(self, cart: Cart) -> None:
        await self.db.delete(cart)
