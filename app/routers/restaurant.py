from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.middleware.auth import get_current_user_id
from app.schemas.restaurant import (
    FilterParams,
    GetRestaurantResponse,
    RestaurantBase,
    RestaurantCreateResponse,
)
from app.services.restaurant import RestaurantService

restaurant_router = APIRouter(prefix="/restaurants", tags=["restaurant"])


async def get_restaurant_service(db: Annotated[AsyncSession, Depends(get_db)]):
    return RestaurantService(db)


@restaurant_router.post(
    "", status_code=status.HTTP_201_CREATED, response_model=RestaurantCreateResponse
)
async def create_restaurant(
    body_data: RestaurantBase,
    restaurant_service: Annotated[RestaurantService, Depends(get_restaurant_service)],
    user_id: Annotated[int, Depends(get_current_user_id)],
):
    """Creates a new restaurant profile for the authenticated user.

    Args:
        body_data: Validated payload containing restaurant details.
        db: Active asynchronous database session.
        user_id: ID of the authenticated user creating the restaurant.

    Returns:
        RestaurantCreateResponse: Details of the newly created restaurant.
    """
    return await restaurant_service.create_restaurant(body_data, user_id)


@restaurant_router.get(
    "", status_code=status.HTTP_200_OK, response_model=list[GetRestaurantResponse]
)
async def get_all_restaurants(
    filter_query: Annotated[FilterParams, Query()],
    restaurant_service: Annotated[RestaurantService, Depends(get_restaurant_service)],
    user_id: int = Depends(get_current_user_id),
):
    """Retrieves a filtered and paginated list of restaurants.

    Args:
        filter_query: Query parameters for search, veg mode, limit, and offset.
        db: Active asynchronous database session.
        user_id: ID of the authenticated user requesting the list.

    Returns:
        list[RestaurantResponse]: Matching active restaurants based on user role and filters.
    """
    return await restaurant_service.get_all_restaurants(user_id, filter_query)


@restaurant_router.get("/{restaurant_id}", status_code=status.HTTP_200_OK)
async def get_restaurant(
    restaurant_id: Annotated[int, Path(gt=0)],
    restaurant_service: Annotated[RestaurantService, Depends(get_restaurant_service)],
    user_id: int = Depends(get_current_user_id),
):
    """Retrieves details for a specific restaurant by ID.

    Args:
        restaurant_id: Primary key ID of the restaurant to fetch.
        db: Active asynchronous database session.
        user_id: ID of the authenticated user making the request.

    Returns:
        RestaurantResponse: Detailed information for the requested restaurant.
    """
    return await restaurant_service.get_restaurant(restaurant_id, user_id)


@restaurant_router.put("/{restaurant_id}", status_code=status.HTTP_200_OK)
async def update_restaurant(
    restaurant_id: Annotated[int, Path(gt=0)],
    body_data: RestaurantBase,
    restaurant_service: Annotated[RestaurantService, Depends(get_restaurant_service)],
    user_id: int = Depends(get_current_user_id),
):
    """Updates an existing restaurant's information.

    Args:
        restaurant_id: Primary key ID of the restaurant to update.
        body_data: Validated payload containing updated restaurant fields.
        db: Active asynchronous database session.
        user_id: ID of the authenticated owner attempting the update.

    Returns:
        RestaurantResponse: The updated restaurant record.
    """
    return await restaurant_service.update_restaurant(restaurant_id, body_data, user_id)


@restaurant_router.delete("/{restaurant_id}", status_code=status.HTTP_200_OK)
async def delete_restaurant(
    restaurant_id: Annotated[int, Path(gt=0)],
    restaurant_service: Annotated[RestaurantService, Depends(get_restaurant_service)],
    user_id: int = Depends(get_current_user_id),
):
    """Soft-deletes a restaurant owned by the authenticated user.

    Args:
        restaurant_id: Primary key ID of the restaurant to delete.
        db: Active asynchronous database session.
        user_id: ID of the authenticated owner attempting the deletion.

    Returns:
        dict: Confirmation message indicating the restaurant was deleted.
    """
    return await restaurant_service.delete_restaurant(restaurant_id, user_id)
