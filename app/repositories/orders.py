from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.cart import Cart
from app.models.menu_item import MenuItem
from app.models.orders import Order, OrderItem
from app.models.restaurant import Restaurant


class OrderRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_cart_for_checkout(self, user_id: int, restaurant_id: int) -> Cart | None:
        query = (
            select(Cart)
            .options(selectinload(Cart.cart_items))
            .where(Cart.user_id == user_id, Cart.restaurant_id == restaurant_id)
            .with_for_update()
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_menu_items_for_update(self, menu_item_ids: list[int]) -> dict[int, MenuItem]:
        if not menu_item_ids:
            return {}
        print(menu_item_ids)
        query = (
            select(MenuItem)
            .where(MenuItem.id.in_(sorted(set(menu_item_ids))))
            .order_by(MenuItem.id)
            .with_for_update()
        )
        result = await self.db.execute(query)
        items = result.scalars().all()
        return {item.id: item for item in items}

    async def get_order_by_id(self, order_id: int) -> Order | None:
        query = (
            select(Order)
            .options(
                selectinload(Order.order_items),
                selectinload(Order.restaurant),
                selectinload(Order.customer),
            )
            .where(Order.id == order_id)
            .execution_options(populate_existing=True)
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def create_order(self, order: Order, order_items: list[OrderItem], cart: Cart) -> Order:
        self.db.add(order)
        await self.db.flush()

        for item in order_items:
            item.order_id = order.id
            self.db.add(item)

        await self.db.delete(cart)
        await self.db.flush()

        return await self.get_order_by_id(order.id)

    async def get_all_orders(self, user_id) -> list[Order]:
        query = (
            select(Order)
            .options(
                selectinload(Order.order_items),
                selectinload(Order.restaurant),
                selectinload(Order.customer),
            )
            .where(
                or_(
                    Order.customer_id == user_id,
                    Order.restaurant.has(Restaurant.owner_id == user_id),
                )
            )
            .order_by(Order.created_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_order_for_update(self, order_id: int) -> Order | None:
        """Locks the Order row while loading its restaurant and items for status transitions."""
        query = (
            select(Order)
            .options(
                selectinload(Order.order_items),
                selectinload(Order.restaurant),
            )
            .where(Order.id == order_id)
            .with_for_update()
        )
        result = await self.db.execute(query)
        return result.scalars().first()
