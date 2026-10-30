from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Messages
from app.repositories.menuItem import MenuRepository
from app.schemas.menuItem import (
    FilterParams,
    MenuItemBase,
    MenuItemCreateResponse,
    MenuItemDeleteResponse,
    MenuItemUpdateRequest,
    MenuItemUpdateResponse,
)
from app.utils.utils import raise_http_error


class MenuItemService:
    """Handles business logic, ownership checks, and transactions for menu items."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = MenuRepository(db)

    async def create_menu_item(
        self, body_data: MenuItemBase, user_id: int
    ) -> MenuItemCreateResponse:
        """Creates and commits a new menu item if the user owns the restaurant."""
        restaurant = await self.repo.get_restaurant_by_id(
            restaurant_id=body_data.restaurantId, active_only=True
        )
        if not restaurant:
            raise_http_error(status.HTTP_404_NOT_FOUND, Messages.RESTAURANT_NOT_FOUND)

        if restaurant.owner_id != user_id:
            raise_http_error(
                status.HTTP_403_FORBIDDEN,
                Messages.MENU_ITEM_ADD_FORBIDDEN,
            )

        menu_item = await self.repo.create_menu_item(body_data)
        try:
            await self.db.commit()
            await self.db.refresh(menu_item)
        except Exception:
            await self.db.rollback()
            raise

        return {
            **body_data.model_dump(),
            "id": menu_item.id,
            "message": Messages.MENU_ITEM_CREATED,
        }

    async def get_categorized_menu_items(
        self, user_id: int, filter_query: FilterParams, restaurant_id
    ) -> dict[str, list]:
        """Fetches paginated menu items for an active restaurant and groups them by category."""
        restaurant = await self.repo.get_restaurant_by_id(restaurant_id, active_only=True)
        if not restaurant:
            raise_http_error(status.HTTP_404_NOT_FOUND, Messages.RESTAURANT_NOT_FOUND)

        offset = (filter_query.offset) * filter_query.limit

        menu_items = await self.repo.get_menu_items_by_restaurant(
            restaurant_id, filter_query.limit, offset
        )

        categorized_menu = {}
        for item in menu_items:
            category = item.category
            if category not in categorized_menu:
                categorized_menu[category] = []
            categorized_menu[category].append(item)

        return categorized_menu

    async def update_menu_item(
        self, menu_item_id: int, body_data: MenuItemUpdateRequest, user_id: int
    ) -> MenuItemUpdateResponse:
        """Updates and commits an existing menu item after verifying restaurant ownership."""
        menu_item = await self.repo.get_menu_item_by_id(menu_item_id)
        if not menu_item:
            raise_http_error(status.HTTP_404_NOT_FOUND, Messages.MENU_ITEM_NOT_FOUND)

        restaurant = await self.repo.get_restaurant_by_id(menu_item.restaurant_id, active_only=True)
        if not restaurant or restaurant.owner_id != user_id:
            raise_http_error(
                status.HTTP_403_FORBIDDEN,
                Messages.MENU_ITEM_EDIT_FORBIDDEN,
            )

        updated_item = await self.repo.update_menu_item(menu_item, body_data)

        try:
            await self.db.commit()
            await self.db.refresh(updated_item)
        except Exception:
            await self.db.rollback()
            raise

        return updated_item

    async def delete_menu_item(self, menu_item_id: int, user_id: int) -> MenuItemDeleteResponse:
        """Deletes a menu item and commits the change after verifying restaurant ownership."""
        menu_item = await self.repo.get_menu_item_by_id(menu_item_id)
        if not menu_item:
            raise_http_error(status.HTTP_404_NOT_FOUND, Messages.MENU_ITEM_NOT_FOUND)

        restaurant = await self.repo.get_restaurant_by_id(menu_item.restaurant_id, active_only=True)
        if not restaurant or restaurant.owner_id != user_id:
            raise_http_error(status.HTTP_403_FORBIDDEN, Messages.MENU_ITEM_DELETE_FORBIDDEN)

        await self.repo.delete_menu_item(menu_item)
        try:
            await self.db.commit()
        except Exception:
            await self.db.rollback()
            raise

        return {"id": menu_item_id, "message": Messages.MENU_ITEM_DELETED, "success": True}
