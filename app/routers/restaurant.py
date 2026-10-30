from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.middleware.auth import get_current_user_id
from app.schemas.restaurant import FilterParams, RestaurantBase, RestaurantCreateResponse
from app.services.restaurant import (
    createRestaurant,
    deleteRestaurant,
    getAllRestaurants,
    getRestaurant,
    updateRestaurant,
)

restaurantRouter = APIRouter(prefix="/restaurant", tags=["restaurant"])


@restaurantRouter.post(
    "/create", status_code=status.HTTP_201_CREATED, response_model=RestaurantCreateResponse
)
def CreateRestaurant(
    body_data: RestaurantBase,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return createRestaurant(db, body_data, user_id)


@restaurantRouter.get("/all", status_code=status.HTTP_200_OK)
def GetAllRestaurants(
    filter_query: Annotated[FilterParams, Query()],
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return getAllRestaurants(db, user_id, filter_query)


@restaurantRouter.get("/{restaurant_id}", status_code=status.HTTP_200_OK)
def GetRestaurant(
    restaurant_id: int, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)
):
    return getRestaurant(db, restaurant_id, user_id)


@restaurantRouter.put("/{restaurant_id}", status_code=status.HTTP_200_OK)
def UpdateRestaurant(
    restaurant_id: int,
    body_data: RestaurantBase,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return updateRestaurant(db, restaurant_id, body_data, user_id)


@restaurantRouter.delete("/{restaurant_id}", status_code=status.HTTP_200_OK)
def DeleteRestaurant(
    restaurant_id: int, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)
):
    return deleteRestaurant(db, restaurant_id, user_id)
