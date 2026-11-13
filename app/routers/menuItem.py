from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.middleware.auth import get_current_user_id
from app.schemas.menuItem import (
    FilterParams,
    MenuItemBase,
    MenuItemCreateResponse,
    MenuItemDeleteResponse,
    MenuItemUpdateRequest,
    MenuItemUpdateResponse,
)
from app.services.menuItem import MenuItemService

menu_item_router = APIRouter(prefix="/menuItem", tags=["menuItem"])


@menu_item_router.post(
    "/create", status_code=status.HTTP_201_CREATED, response_model=MenuItemCreateResponse
)
async def create_menu_item(
    body_data: MenuItemBase,
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: int = Depends(get_current_user_id),
):
    menu_item_service = MenuItemService(db)
    return await menu_item_service.create_menu_item(body_data, user_id)


@menu_item_router.get("/all/{restaurant_id}", status_code=status.HTTP_200_OK)
async def get_categorized_menu_items(
    filter_query: Annotated[FilterParams, Query()],
    db: Annotated[AsyncSession, Depends(get_db)],
    restaurant_id: int,
    user_id: int = Depends(get_current_user_id),
):
    menu_item_service = MenuItemService(db)
    return await menu_item_service.get_categorized_menu_items(user_id, filter_query, restaurant_id)


@menu_item_router.put(
    "/{menu_item_id}", status_code=status.HTTP_200_OK, response_model=MenuItemUpdateResponse
)
async def update_menu_item(
    menu_item_id: int,
    body_data: MenuItemUpdateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: int = Depends(get_current_user_id),
):
    menu_item_service = MenuItemService(db)
    return await menu_item_service.update_menu_item(menu_item_id, body_data, user_id)


@menu_item_router.delete(
    "/{menu_item_id}", status_code=status.HTTP_200_OK, response_model=MenuItemDeleteResponse
)
async def delete_menu_item(
    menu_item_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: int = Depends(get_current_user_id),
):
    menu_item_service = MenuItemService(db)
    return await menu_item_service.delete_menu_item(menu_item_id, user_id)
