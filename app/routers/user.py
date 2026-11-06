from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.middleware.auth import get_current_user_id
from app.schemas.user import ApiResponse, SignUpUserRequest, UserResponse
from app.services.user import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiResponse[UserResponse],
)
async def create_user(user_data: SignUpUserRequest, db: Annotated[AsyncSession, Depends(get_db)]):
    """Register a new user account after validating the input details.

    Args:
        user_data (SignUpUserRequest): Pydantic schema containing registration details such as email and password.
        db (AsyncSession): Asynchronous database session dependency injected via FastAPI Depends.

    Returns:
        ApiResponse[UserResponse]: Wrapped API response containing a success message and the created user's profile details.
    """
    user_service = UserService(db)
    new_user = await user_service.register_user(user_data)

    return ApiResponse(
        message="User registered successfully", data=UserResponse.model_validate(new_user)
    )


@router.get("/me", status_code=status.HTTP_200_OK, response_model=ApiResponse[UserResponse])
async def get_current_user_profile(
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: Annotated[int, Depends(get_current_user_id)],
):
    """Retrieve the profile data of the currently authenticated user session.

    Args:
        db (AsyncSession): Asynchronous database session dependency injected via FastAPI Depends.
        user_id (int): Primary key ID of the user, extracted and validated from the active auth token.

    Returns:
        ApiResponse[UserResponse]: Wrapped API response containing a success message and the user's current profile data.
    """
    user_service = UserService(db)
    user = await user_service.get_profile(user_id)

    return ApiResponse(
        message="Profile fetched successfully", data=UserResponse.model_validate(user)
    )
