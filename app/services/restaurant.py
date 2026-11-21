from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constant import Messages
from app.models.restaurant import Restaurant
from app.models.user import UserRole
from app.repositories.restaurant import RestaurantRepository
from app.repositories.user import UserRepository
from app.schemas.restaurant import FilterParams, RestaurantBase
from app.utils.utils import raise_http_error


class RestaurantService:
    """Handles business logic, permissions, and transactions for restaurants."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = RestaurantRepository(db)
        self.user_repo = UserRepository(db)

    async def get_user(self, user_id: int):
        user = await self.user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise_http_error(status.HTTP_404_NOT_FOUND, Messages.USER_NOT_FOUND)
        return user

    async def create_restaurant(self, body_data: RestaurantBase, user_id: int) -> Restaurant:
        """Creates and commits a new restaurant if the user is an owner."""
        async with self.db.begin():
            user = await self.get_user(user_id)
            if user.role == UserRole.CUSTOMER:
                raise_http_error(status.HTTP_403_FORBIDDEN, Messages.PERMISSION_DENIED)

            restaurant = await self.repo.create_restaurant(body_data, user_id)
        return restaurant

    async def get_restaurant(self, restaurant_id: int, user_id: int) -> Restaurant:
        """Fetches an active restaurant after verifying the user's view permissions."""
        user = await self.get_user(user_id)
        restaurant = await self.repo.get_restaurant_by_id(restaurant_id, active_only=True)
        if not restaurant:
            raise_http_error(status.HTTP_404_NOT_FOUND, Messages.RESTAURANT_NOT_FOUND)

        if user.role != "CUSTOMER" and restaurant.owner_id != user_id:
            raise_http_error(status.HTTP_403_FORBIDDEN, Messages.PERMISSION_DENIED)

        return restaurant

    async def update_restaurant(
        self, restaurant_id: int, body_data: RestaurantBase, user_id: int
    ) -> Restaurant:
        """Updates and commits an existing restaurant after verifying ownership."""
        async with self.db.begin():
            user = await self.get_user(user_id)
            if user.role == "CUSTOMER":
                raise_http_error(status.HTTP_403_FORBIDDEN, Messages.PERMISSION_DENIED)

            restaurant = await self.repo.get_restaurant_by_id(restaurant_id, active_only=True)
            if not restaurant:
                raise_http_error(status.HTTP_404_NOT_FOUND, Messages.RESTAURANT_NOT_FOUND)

            if restaurant.owner_id != user_id:
                raise_http_error(status.HTTP_403_FORBIDDEN, Messages.PERMISSION_DENIED)

            updated_restaurant = await self.repo.update_restaurant(restaurant, body_data)

        await self.db.refresh(updated_restaurant)
        return updated_restaurant

    async def delete_restaurant(self, restaurant_id: int, user_id: int) -> dict:
        """Soft-deletes a restaurant and commits the change after verifying ownership."""
        async with self.db.begin():
            user = await self.get_user(user_id)
            if user.role == "CUSTOMER":
                raise_http_error(status.HTTP_401_UNAUTHORIZED, Messages.PERMISSION_DENIED)

            restaurant = await self.repo.get_restaurant_by_id(restaurant_id, active_only=True)
            if not restaurant:
                raise_http_error(status.HTTP_404_NOT_FOUND, Messages.RESTAURANT_NOT_FOUND)

            if restaurant.owner_id != user_id:
                raise_http_error(status.HTTP_403_FORBIDDEN, Messages.PERMISSION_DENIED)

            await self.repo.delete_restaurant(restaurant)
        return {"message": Messages.RESTAURANT_DELETED, "id": restaurant_id}

    async def get_all_restaurants(
        self, user_id: int, filter_query: FilterParams
    ) -> list[Restaurant]:
        """Fetches a filtered list of active restaurants accessible to the user."""
        user = await self.get_user(user_id)
        owner_id = user.id if user.role == UserRole.OWNER else None
        return await self.repo.get_all_restaurants(
            filter_query=filter_query,
            owner_id=owner_id,
        )
