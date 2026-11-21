from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constant import Messages
from app.repositories.menu_item import MenuRepository
from app.repositories.restaurant import RestaurantRepository
from app.schemas.menu_item import (
    FilterParams,
    MenuItemBase,
    MenuItemCreateResponse,
    MenuItemUpdateRequest,
    MenuItemUpdateResponse,
)
from app.utils.utils import raise_http_error


class MenuItemService:
    """Handles business logic, ownership checks, and transactions for menu items."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = MenuRepository(db)
        self.restaurant_repo = RestaurantRepository(db)

    async def create_menu_item(
        self, body_data: MenuItemBase, user_id: int
    ) -> MenuItemCreateResponse:
        """Creates and commits a new menu item if the user owns the restaurant."""
        async with self.db.begin():
            restaurant = await self.restaurant_repo.get_restaurant_by_id(
                restaurant_id=body_data.restaurant_id, active_only=True
            )
            existing_item = await self.repo.get_menu_item_by_name(
                restaurant_id=body_data.restaurant_id,
                name=body_data.name.strip(),
            )
            if existing_item:
                raise_http_error(status.HTTP_409_CONFLICT, Messages.MENU_ITEM_ALREADY_EXISTS)
            if not restaurant:
                raise_http_error(status.HTTP_404_NOT_FOUND, Messages.RESTAURANT_NOT_FOUND)

            if restaurant.owner_id != user_id:
                raise_http_error(
                    status.HTTP_403_FORBIDDEN,
                    Messages.PERMISSION_DENIED,
                )

            menu_item = await self.repo.create_menu_item(body_data)
        return {
            **body_data.model_dump(),
            "id": menu_item.id,
            "message": Messages.MENU_ITEM_CREATED,
            "created_at": menu_item.created_at,
            "updated_at": menu_item.updated_at,
        }

    async def get_categorized_menu_items(
        self, user_id: int, filter_query: FilterParams, restaurant_id: int
    ) -> dict:
        restaurant = await self.restaurant_repo.get_restaurant_by_id(
            restaurant_id, active_only=True
        )
        if not restaurant:
            raise_http_error(status.HTTP_404_NOT_FOUND, Messages.RESTAURANT_NOT_FOUND)

        offset = filter_query.offset * filter_query.limit

        menu_items = await self.repo.get_menu_items_by_restaurant(
            restaurant_id, filter_query.limit, offset
        )
        category_counts = await self.repo.get_category_counts(restaurant_id)

        categorized_menu: dict[str, list] = {}
        for item in menu_items:
            categorized_menu.setdefault(item.category, []).append(item)

        return {
            "categorizedItems": categorized_menu,
            "categoryCounts": category_counts,
        }

    async def update_menu_item(
        self, menu_item_id: int, body_data: MenuItemUpdateRequest, user_id: int
    ) -> MenuItemUpdateResponse:
        """Updates and commits an existing menu item after verifying restaurant ownership."""
        async with self.db.begin():
            menu_item = await self.repo.get_menu_item_by_id(menu_item_id)
            if not menu_item:
                raise_http_error(status.HTTP_404_NOT_FOUND, Messages.MENU_ITEM_NOT_FOUND)

            restaurant = await self.restaurant_repo.get_restaurant_by_id(
                menu_item.restaurant_id, active_only=True
            )
            if not restaurant or restaurant.owner_id != user_id:
                raise_http_error(
                    status.HTTP_403_FORBIDDEN,
                    Messages.PERMISSION_DENIED,
                )

            updated_item = await self.repo.update_menu_item(menu_item, body_data)
            await self.db.flush()
            await self.db.refresh(updated_item)
        return updated_item

    async def delete_menu_item(self, menu_item_id: int, user_id: int) -> None:
        """Deletes a menu item and commits the change after verifying restaurant ownership."""
        async with self.db.begin():
            menu_item = await self.repo.get_menu_item_by_id(menu_item_id)
            if not menu_item:
                raise_http_error(status.HTTP_404_NOT_FOUND, Messages.MENU_ITEM_NOT_FOUND)

            restaurant = await self.restaurant_repo.get_restaurant_by_id(
                menu_item.restaurant_id, active_only=True
            )
            if not restaurant or restaurant.owner_id != user_id:
                raise_http_error(status.HTTP_403_FORBIDDEN, Messages.PERMISSION_DENIED)

            await self.repo.delete_menu_item(menu_item)

        return {"id": menu_item_id, "message": Messages.MENU_ITEM_DELETED, "success": True}
