from fastapi import status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.restaurant import Restaurant
from app.models.user import User
from app.schemas.restaurant import FilterParams, RestaurantBase, RestaurantCreateResponse
from app.utils.utils import raise_http_error


def createRestaurant(
    db: Session, body_data: RestaurantBase, user_id: int
) -> RestaurantCreateResponse:
    print(body_data)
    stmt = select(User).where(User.id == user_id)
    user = db.scalar(stmt)
    if user.role == "CUSTOMER":
        raise_http_error(status.HTTP_403_FORBIDDEN, "only owner can edit restaurant")

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
    db.add(restaurant)
    db.commit()
    db.refresh(restaurant)
    return {
        **body_data.model_dump(),
        "id": restaurant.id,
        "ownerId": user_id,
        "message": "restaurant created successfully",
    }


def getRestaurant(db: Session, restaurant_id: int, user_id: int) -> Restaurant:
    stmt_user = select(User).where(User.id == user_id)
    user = db.scalar(stmt_user)
    if not user:
        raise_http_error(status.HTTP_404_NOT_FOUND, "User not found")

    stmt_rest = select(Restaurant).where(Restaurant.id == restaurant_id, Restaurant.isActive)
    restaurant = db.scalar(stmt_rest)

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
    stmt_user = select(User).where(User.id == user_id)
    user = db.scalar(stmt_user)
    if user.role == "CUSTOMER":
        raise_http_error(status.HTTP_403_FORBIDDEN, "only owner can edit restaurant")

    stmt_rest = select(Restaurant).where(
        Restaurant.id == restaurant_id, Restaurant.isActive == True
    )
    restaurant = db.scalar(stmt_rest)
    if not restaurant:
        raise_http_error(status.HTTP_404_NOT_FOUND, "restaurant not found")

    if restaurant.ownerId != user_id:
        raise_http_error(status.HTTP_403_FORBIDDEN, "you do not own this restaurant")

    restaurant.name = body_data.name
    restaurant.cuisine = body_data.cuisine
    restaurant.rating = body_data.rating
    restaurant.mobileNumber = body_data.mobileNumber
    restaurant.address = body_data.address
    restaurant.image = str(body_data.image)
    restaurant.isVegOnly = body_data.isVegOnly
    restaurant.hours = body_data.hours.model_dump()

    db.commit()
    db.refresh(restaurant)
    return restaurant


def deleteRestaurant(db: Session, restaurant_id: int, user_id: int) -> dict:
    stmt_user = select(User).where(User.id == user_id)
    user = db.scalar(stmt_user)
    if user.role == "CUSTOMER":
        raise_http_error(status.HTTP_401_UNAUTHORIZED, "only owner can delete restaurant")

    stmt_rest = select(Restaurant).where(
        Restaurant.id == restaurant_id, Restaurant.isActive == True
    )
    restaurant = db.scalar(stmt_rest)
    if not restaurant:
        raise_http_error(status.HTTP_404_NOT_FOUND, "restaurant not found")

    if restaurant.ownerId != user_id:
        raise_http_error(status.HTTP_403_FORBIDDEN, "you do not own this restaurant")

    restaurant.isActive = False
    db.commit()

    return {"message": "restaurant deleted successfully", "id": restaurant_id}


def getAllRestaurants(db: Session, user_id: int, filter_query: FilterParams) -> list[Restaurant]:
    stmt_user = select(User).where(User.id == user_id)
    user = db.scalar(stmt_user)
    if not user:
        raise_http_error(status.HTTP_404_NOT_FOUND, "User not found")

    if user.role == "CUSTOMER":
        stmt_rest = select(Restaurant).where(Restaurant.isActive)
    else:
        stmt_rest = select(Restaurant).where(
            Restaurant.ownerId == user_id, Restaurant.isActive == True
        )

    if filter_query.vegMode:
        stmt_rest = stmt_rest.where(Restaurant.isVegOnly == True)

    if filter_query.search:
        stmt_rest = stmt_rest.where(
            (Restaurant.name.ilike(f"%{filter_query.search}%"))
            | (Restaurant.cuisine.ilike(f"%{filter_query.search}%"))
        )

    stmt_rest = stmt_rest.limit(filter_query.limit).offset(filter_query.offset)

    restaurants = db.scalars(stmt_rest).all()
    return restaurants
