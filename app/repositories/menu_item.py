from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.menu_item import MenuItem
from app.schemas.menu_item import MenuItemBase, MenuItemUpdateRequest


class MenuRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_category_counts(self, restaurant_id: int) -> dict[str, int]:
        stmt = (
            select(MenuItem.category, func.count(MenuItem.id))
            .where(MenuItem.restaurant_id == restaurant_id, MenuItem.is_active)
            .group_by(MenuItem.category)
            .order_by(MenuItem.category)
        )
        result = await self.db.execute(stmt)
        return {category: count for category, count in result.all()}

    async def get_menu_item_by_name(self, restaurant_id: int, name: str) -> MenuItem | None:
        stmt = select(MenuItem).where(
            MenuItem.restaurant_id == restaurant_id,
            func.lower(MenuItem.name) == name.lower(),
        )
        return await self.db.scalar(stmt)

    async def get_menu_item_by_id(self, menu_item_id: int) -> MenuItem | None:
        stmt = select(MenuItem).where(MenuItem.id == menu_item_id)
        return await self.db.scalar(stmt)

    async def create_menu_item(self, body_data: MenuItemBase) -> MenuItem:
        menu_item = MenuItem(
            restaurant_id=body_data.restaurant_id,
            name=body_data.name,
            description=body_data.description,
            price=body_data.price,
            category=body_data.category,
            is_veg=body_data.is_veg,
            stock=body_data.stock,
            image=str(body_data.image),
        )
        self.db.add(menu_item)
        return menu_item

    async def delete_menu_item(self, menu_item: MenuItem) -> None:
        await self.db.delete(menu_item)

    async def get_menu_items_by_restaurant(
        self, restaurant_id: int, limit: int = 20, offset: int = 0
    ) -> list[MenuItem]:
        stmt = (
            select(MenuItem)
            .where(MenuItem.restaurant_id == restaurant_id)
            .order_by(MenuItem.category, MenuItem.name)
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.scalars(stmt)
        return list(result.all())

    async def update_menu_item(
        self, menu_item: MenuItem, body_data: MenuItemUpdateRequest
    ) -> MenuItem:
        menu_item.name = body_data.name
        menu_item.description = body_data.description
        menu_item.price = body_data.price
        menu_item.category = body_data.category
        menu_item.is_veg = body_data.is_veg
        menu_item.stock = body_data.stock
        menu_item.image = str(body_data.image)
        return menu_item
