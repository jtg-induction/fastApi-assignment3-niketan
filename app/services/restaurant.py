from fastapi import status
from sqlalchemy.orm import Session

from app.models.restaurant import Restaurant
from app.repositories.restaurant import RestaurantRepository
from app.schemas.restaurant import FilterParams, RestaurantBase, RestaurantCreateResponse
from app.utils.utils import raise_http_error


def createRestaurant(
    db: Session, body_data: RestaurantBase, user_id: int
) -> RestaurantCreateResponse:
    print(body_data)
    repo = RestaurantRepository(db)

    user = repo.get_user_by_id(user_id)
    if not user or user.role == "CUSTOMER":
        raise_http_error(status.HTTP_403_FORBIDDEN, "only owner can edit restaurant")

    restaurant = repo.create_restaurant(body_data, user_id)
    return {
        **body_data.model_dump(),
        "id": restaurant.id,
        "ownerId": user_id,
        "message": "restaurant created successfully",
    }


def getRestaurant(db: Session, restaurant_id: int, user_id: int) -> Restaurant:
    repo = RestaurantRepository(db)

    user = repo.get_user_by_id(user_id)
    if not user:
        raise_http_error(status.HTTP_404_NOT_FOUND, "User not found")

    restaurant = repo.get_restaurant_by_id(restaurant_id, active_only=True)
    if not restaurant:
        raise_http_error(status.HTTP_404_NOT_FOUND, "Restaurant not found")

    if user.role != "CUSTOMER" and restaurant.ownerId != user_id:
        raise_http_error(
            status.HTTP_403_FORBIDDEN, "You do not have permission to view this restaurant"
        )

    return restaurant


def updateRestaurant(
    db: Session, restaurant_id: int, body_data: RestaurantBase, user_id: int
) -> Restaurant:
    repo = RestaurantRepository(db)

    user = repo.get_user_by_id(user_id)
    if not user or user.role == "CUSTOMER":
        raise_http_error(status.HTTP_403_FORBIDDEN, "only owner can edit restaurant")

    restaurant = repo.get_restaurant_by_id(restaurant_id, active_only=True)
    if not restaurant:
        raise_http_error(status.HTTP_404_NOT_FOUND, "restaurant not found")

    if restaurant.ownerId != user_id:
        raise_http_error(status.HTTP_403_FORBIDDEN, "you do not own this restaurant")

    return repo.update_restaurant(restaurant, body_data)


def deleteRestaurant(db: Session, restaurant_id: int, user_id: int) -> dict:
    repo = RestaurantRepository(db)

    user = repo.get_user_by_id(user_id)
    if not user or user.role == "CUSTOMER":
        raise_http_error(status.HTTP_401_UNAUTHORIZED, "only owner can delete restaurant")

    restaurant = repo.get_restaurant_by_id(restaurant_id, active_only=True)
    if not restaurant:
        raise_http_error(status.HTTP_404_NOT_FOUND, "restaurant not found")

    if restaurant.ownerId != user_id:
        raise_http_error(status.HTTP_403_FORBIDDEN, "you do not own this restaurant")

    repo.delete_restaurant(restaurant)
    return {"message": "restaurant deleted successfully", "id": restaurant_id}


def getAllRestaurants(db: Session, user_id: int, filter_query: FilterParams) -> list[Restaurant]:
    repo = RestaurantRepository(db)

    user = repo.get_user_by_id(user_id)
    if not user:
        raise_http_error(status.HTTP_404_NOT_FOUND, "User not found")

    return repo.get_all_restaurants(user, filter_query)
