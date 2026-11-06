from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.restaurant import Restaurant
from app.models.user import User
from app.schemas.restaurant import FilterParams, RestaurantBase


class RestaurantRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_id(self, user_id: int) -> User | None:
        return await self.db.scalar(select(User).where(User.id == user_id))

    async def get_restaurant_by_id(
        self, restaurant_id: int, active_only: bool = True
    ) -> Restaurant | None:
        stmt = select(Restaurant).where(Restaurant.id == restaurant_id)
        if active_only:
            stmt = stmt.where(Restaurant.is_active)
        return await self.db.scalar(stmt)

    async def create_restaurant(self, body_data: RestaurantBase, user_id: int) -> Restaurant:
        restaurant = Restaurant(
            name=body_data.name,
            owner_id=user_id,
            cuisine=body_data.cuisine,
            rating=body_data.rating,
            mobile=body_data.mobile,
            address=body_data.address,
            image=str(body_data.image),
            is_veg_only=body_data.is_veg_only,
            hours=body_data.hours.model_dump(),
            is_active=True,
        )
        self.db.add(restaurant)
        return restaurant

    async def update_restaurant(
        self, restaurant: Restaurant, body_data: RestaurantBase
    ) -> Restaurant:
        restaurant.name = body_data.name
        restaurant.cuisine = body_data.cuisine
        restaurant.rating = body_data.rating
        restaurant.mobile = body_data.mobile
        restaurant.address = body_data.address
        restaurant.image = str(body_data.image)
        restaurant.is_veg_only = body_data.is_veg_only
        restaurant.hours = body_data.hours.model_dump()
        return restaurant

    async def delete_restaurant(self, restaurant: Restaurant) -> None:
        restaurant.is_active = False

    async def get_all_restaurants(self, user: User, filter_query: FilterParams) -> list[Restaurant]:
        if user.role == "CUSTOMER":
            stmt = select(Restaurant).where(Restaurant.is_active)
        else:
            stmt = select(Restaurant).where(Restaurant.owner_id == user.id, Restaurant.is_active)

        if filter_query.veg_mode:
            stmt = stmt.where(Restaurant.is_veg_only)

        if filter_query.search:
            stmt = stmt.where(
                (Restaurant.name.ilike(f"%{filter_query.search}%"))
                | (Restaurant.cuisine.ilike(f"%{filter_query.search}%"))
            )

        stmt = stmt.limit(filter_query.limit).offset(filter_query.offset)
        result = await self.db.scalars(stmt)

        return list(result.all())
