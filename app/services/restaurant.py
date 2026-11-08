from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.restaurant import Restaurant
from app.repositories.restaurant import RestaurantRepository
from app.schemas.restaurant import FilterParams, RestaurantBase, RestaurantCreateResponse
from app.utils.utils import raise_http_error


class RestaurantService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = RestaurantRepository(db)

    async def create_restaurant(
        self, body_data: RestaurantBase, user_id: int
    ) -> RestaurantCreateResponse:
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
            "message": "restaurant created successfully",
        }

    async def get_restaurant(self, restaurant_id: int, user_id: int) -> Restaurant:

        user = await self.repo.get_user_by_id(user_id)
        if not user:
            raise_http_error(status.HTTP_404_NOT_FOUND, "User not found")

        restaurant = await self.repo.get_restaurant_by_id(restaurant_id, active_only=True)
        if not restaurant:
            raise_http_error(status.HTTP_404_NOT_FOUND, "Restaurant not found")

        if user.role != "CUSTOMER" and restaurant.owner_id != user_id:
            raise_http_error(
                status.HTTP_403_FORBIDDEN, "You do not have permission to view this restaurant"
            )

        return restaurant

    async def update_restaurant(
        self, restaurant_id: int, body_data: RestaurantBase, user_id: int
    ) -> Restaurant:

        user = await self.repo.get_user_by_id(user_id)
        if not user or user.role == "CUSTOMER":
            raise_http_error(status.HTTP_403_FORBIDDEN, "only owner can edit restaurant")

        restaurant = await self.repo.get_restaurant_by_id(restaurant_id, active_only=True)
        if not restaurant:
            raise_http_error(status.HTTP_404_NOT_FOUND, "restaurant not found")

        if restaurant.owner_id != user_id:
            raise_http_error(status.HTTP_403_FORBIDDEN, "you do not own this restaurant")

        updated_restaurant = await self.repo.update_restaurant(restaurant, body_data)

        try:
            await self.db.commit()
            await self.db.refresh(updated_restaurant)
        except Exception:
            await self.db.rollback()
            raise

        return updated_restaurant

    async def delete_restaurant(self, restaurant_id: int, user_id: int) -> dict:

        user = await self.repo.get_user_by_id(user_id)
        if not user or user.role == "CUSTOMER":
            raise_http_error(status.HTTP_401_UNAUTHORIZED, "only owner can delete restaurant")

        restaurant = await self.repo.get_restaurant_by_id(restaurant_id, active_only=True)
        if not restaurant:
            raise_http_error(status.HTTP_404_NOT_FOUND, "restaurant not found")

        if restaurant.owner_id != user_id:
            raise_http_error(status.HTTP_403_FORBIDDEN, "you do not own this restaurant")

        await self.repo.delete_restaurant(restaurant)
        try:
            await self.db.commit()
        except Exception:
            await self.db.rollback()
            raise
        return {"message": "restaurant deleted successfully", "id": restaurant_id}

    async def get_all_restaurant(
        self, user_id: int, filter_query: FilterParams
    ) -> list[Restaurant]:

        user = await self.repo.get_user_by_id(user_id)
        if not user:
            raise_http_error(status.HTTP_404_NOT_FOUND, "User not found")

        return await self.repo.get_all_restaurants(user, filter_query)
