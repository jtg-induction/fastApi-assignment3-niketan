from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.middleware.auth import get_current_user_id
from app.schemas.restaurant import FilterParams, RestaurantBase, RestaurantCreateResponse
from app.services.restaurant import RestaurantService

restaurant_router = APIRouter(prefix="/restaurant", tags=["restaurant"])


@restaurant_router.post(
    "/create", status_code=status.HTTP_201_CREATED, response_model=RestaurantCreateResponse
)
async def create_restaurant(
    body_data: RestaurantBase,
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: int = Depends(get_current_user_id),
):
    """Creates a new restaurant profile for the authenticated user.

    Args:
        body_data: Validated payload containing restaurant details.
        db: Active asynchronous database session.
        user_id: ID of the authenticated user creating the restaurant.

    Returns:
        RestaurantCreateResponse: Details of the newly created restaurant.
    """
    restaurant_service = RestaurantService(db)
    return await restaurant_service.create_restaurant(body_data, user_id)


@restaurant_router.get("/all", status_code=status.HTTP_200_OK)
async def get_all_restaurants(
    filter_query: Annotated[FilterParams, Query()],
    db: Annotated[AsyncSession, Depends(get_db)],
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
    restaurant_service = RestaurantService(db)
    return await restaurant_service.get_all_restaurant(user_id, filter_query)


@restaurant_router.get("/{restaurant_id}", status_code=status.HTTP_200_OK)
async def get_restaurant(
    restaurant_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
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
    restaurant_service = RestaurantService(db)
    return await restaurant_service.get_restaurant(restaurant_id, user_id)


@restaurant_router.put("/{restaurant_id}", status_code=status.HTTP_200_OK)
async def update_restaurant(
    restaurant_id: int,
    body_data: RestaurantBase,
    db: Annotated[AsyncSession, Depends(get_db)],
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
    restaurant_service = RestaurantService(db)
    return await restaurant_service.update_restaurant(restaurant_id, body_data, user_id)


@restaurant_router.delete("/{restaurant_id}", status_code=status.HTTP_200_OK)
async def delete_restaurant(
    restaurant_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
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
    restaurant_service = RestaurantService(db)
    return await restaurant_service.delete_restaurant(restaurant_id, user_id)
