from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Messages
from app.models.restaurant import Restaurant
from app.repositories.restaurant import RestaurantRepository
from app.schemas.restaurant import FilterParams, RestaurantBase, RestaurantCreateResponse
from app.utils.utils import raise_http_error


class RestaurantService:
    """Handles business logic, permissions, and transactions for restaurants."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = RestaurantRepository(db)

    async def create_restaurant(
        self, body_data: RestaurantBase, user_id: int
    ) -> RestaurantCreateResponse:
        """Creates and commits a new restaurant if the user is an owner."""
        user = await self.repo.get_user_by_id(user_id)
        if not user or user.role == "CUSTOMER":
            raise_http_error(status.HTTP_403_FORBIDDEN, "only owner can edit restaurant")

        restaurant = await self.repo.create_restaurant(body_data, user_id)
        try:
            await self.db.commit()
            await self.db.refresh(restaurant)
        except Exception:
            await self.db.rollback()
            raise
        return {
            **body_data.model_dump(),
            "id": restaurant.id,
            "owner_id": user_id,
            "message": Messages.RESTAURANT_CREATED,
        }

    async def get_restaurant(self, restaurant_id: int, user_id: int) -> Restaurant:
        """Fetches an active restaurant after verifying the user's view permissions."""
        user = await self.repo.get_user_by_id(user_id)
        if not user:
            raise_http_error(status.HTTP_404_NOT_FOUND, Messages.USER_NOT_FOUND)

        restaurant = await self.repo.get_restaurant_by_id(restaurant_id, active_only=True)
        if not restaurant:
            raise_http_error(status.HTTP_404_NOT_FOUND, Messages.RESTAURANT_NOT_FOUND)

        if user.role != "CUSTOMER" and restaurant.owner_id != user_id:
            raise_http_error(status.HTTP_403_FORBIDDEN, Messages.RESTAURANT_VIEW_FORBIDDEN)

        return restaurant

    async def update_restaurant(
        self, restaurant_id: int, body_data: RestaurantBase, user_id: int
    ) -> Restaurant:
        """Updates and commits an existing restaurant after verifying ownership."""
        user = await self.repo.get_user_by_id(user_id)
        if not user or user.role == "CUSTOMER":
            raise_http_error(status.HTTP_403_FORBIDDEN, Messages.RESTAURANT_EDIT_FORBIDDEN)

        restaurant = await self.repo.get_restaurant_by_id(restaurant_id, active_only=True)
        if not restaurant:
            raise_http_error(status.HTTP_404_NOT_FOUND, Messages.RESTAURANT_NOT_FOUND)

        if restaurant.owner_id != user_id:
            raise_http_error(status.HTTP_403_FORBIDDEN, Messages.RESTAURANT_NOT_OWNED)

        updated_restaurant = await self.repo.update_restaurant(restaurant, body_data)

        try:
            await self.db.commit()
            await self.db.refresh(updated_restaurant)
        except Exception:
            await self.db.rollback()
            raise

        return updated_restaurant

    async def delete_restaurant(self, restaurant_id: int, user_id: int) -> dict:
        """Soft-deletes a restaurant and commits the change after verifying ownership."""
        user = await self.repo.get_user_by_id(user_id)
        if not user or user.role == "CUSTOMER":
            raise_http_error(status.HTTP_401_UNAUTHORIZED, Messages.RESTAURANT_DELETE_FORBIDDEN)

        restaurant = await self.repo.get_restaurant_by_id(restaurant_id, active_only=True)
        if not restaurant:
            raise_http_error(status.HTTP_404_NOT_FOUND, Messages.RESTAURANT_NOT_FOUND)

        if restaurant.owner_id != user_id:
            raise_http_error(status.HTTP_403_FORBIDDEN, Messages.RESTAURANT_NOT_OWNED)

        await self.repo.delete_restaurant(restaurant)
        try:
            await self.db.commit()
        except Exception:
            await self.db.rollback()
            raise
        return {"message": Messages.RESTAURANT_DELETED, "id": restaurant_id}

    async def get_all_restaurant(
        self, user_id: int, filter_query: FilterParams
    ) -> list[Restaurant]:
        """Fetches a filtered list of active restaurants accessible to the user."""
        user = await self.repo.get_user_by_id(user_id)
        if not user:
            raise_http_error(status.HTTP_404_NOT_FOUND, Messages.USER_NOT_FOUND)

        return await self.repo.get_all_restaurants(user, filter_query)
