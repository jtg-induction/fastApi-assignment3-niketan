from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.restaurant import Restaurant
from app.models.user import User
from app.schemas.restaurant import FilterParams, RestaurantBase


class RestaurantRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_id(self, user_id: int) -> User | None:
        return self.db.scalar(select(User).where(User.id == user_id))

    def get_restaurant_by_id(
        self, restaurant_id: int, active_only: bool = True
    ) -> Restaurant | None:
        stmt = select(Restaurant).where(Restaurant.id == restaurant_id)
        if active_only:
            stmt = stmt.where(Restaurant.isActive == True)
        return self.db.scalar(stmt)

    def create_restaurant(self, body_data: RestaurantBase, user_id: int) -> Restaurant:
        restaurant = Restaurant(
            name=body_data.name,
            ownerId=user_id,
            cuisine=body_data.cuisine,
            rating=body_data.rating,
            mobileNumber=body_data.mobileNumber,
            address=body_data.address,
            image=str(body_data.image),
            isVegOnly=body_data.isVegOnly,
            hours=body_data.hours.model_dump(),
            isActive=True,
        )
        self.db.add(restaurant)
        self.db.commit()
        self.db.refresh(restaurant)
        return restaurant

    def update_restaurant(self, restaurant: Restaurant, body_data: RestaurantBase) -> Restaurant:
        restaurant.name = body_data.name
        restaurant.cuisine = body_data.cuisine
        restaurant.rating = body_data.rating
        restaurant.mobileNumber = body_data.mobileNumber
        restaurant.address = body_data.address
        restaurant.image = str(body_data.image)
        restaurant.isVegOnly = body_data.isVegOnly
        restaurant.hours = body_data.hours.model_dump()
        self.db.commit()
        self.db.refresh(restaurant)
        return restaurant

    def delete_restaurant(self, restaurant: Restaurant) -> None:
        restaurant.isActive = False
        self.db.commit()

    def get_all_restaurants(self, user: User, filter_query: FilterParams) -> list[Restaurant]:
        if user.role == "CUSTOMER":
            stmt = select(Restaurant).where(Restaurant.isActive == True)
        else:
            stmt = select(Restaurant).where(
                Restaurant.ownerId == user.id, Restaurant.isActive == True
            )

        if filter_query.vegMode:
            stmt = stmt.where(Restaurant.isVegOnly == True)

        if filter_query.search:
            stmt = stmt.where(
                (Restaurant.name.ilike(f"%{filter_query.search}%"))
                | (Restaurant.cuisine.ilike(f"%{filter_query.search}%"))
            )

        stmt = stmt.limit(filter_query.limit).offset(filter_query.offset)
        return list(self.db.scalars(stmt).all())
