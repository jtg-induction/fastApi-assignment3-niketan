from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.middleware.auth import get_current_user_id
from app.schemas.user import (
    LoginUserRequest,
    LoginUserResponse,
)
from app.services.Auth import AuthService

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/login", status_code=status.HTTP_200_OK, response_model=LoginUserResponse)
async def login_users(
    user_data: LoginUserRequest, response: Response, db: Annotated[AsyncSession, Depends(get_db)]
):
    """Authenticate user credentials and return user profile details along with session tokens.

    Args:
        user_data (LoginUserRequest): Pydantic validation schema containing the user's login credentials.
        response (Response): FastAPI response instance used to inject HttpOnly session cookies.
        db (AsyncSession): Asynchronous database session dependency injected via FastAPI Depends.

    Returns:
        LoginUserResponse: Serialized API payload containing the user object and a login success notification.
    """
    auth_service = AuthService(db)
    return await auth_service.login_user(response, user_data)


@auth_router.post("/refresh", status_code=status.HTTP_200_OK, response_model=dict)
async def refreshToken(
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
    refresh_token: str | None = Cookie(default=None),
):
    """Validate the current refresh token from the browser cookie store and mint a new access token.

    Args:
        response (Response): FastAPI response instance used to refresh authorization stateful cookies.
        db (AsyncSession): Asynchronous database session dependency injected via FastAPI Depends.
        refresh_token (str | None, optional): Session validation token parsed directly from incoming client cookies. Defaults to None.

    Returns:
        dict: Object payload confirming key generation containing a success string status alongside the raw token.
    """
    auth_service = AuthService(db)
    return await auth_service.refresh_access_token(response, refresh_token)


@auth_router.post("/logout", status_code=status.HTTP_200_OK, response_model=dict)
async def logOut(
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: int = Depends(get_current_user_id),
):
    """Terminate the active authentication session by resetting database references and dropping client cookies.

    Args:
        response (Response): FastAPI response instance used to signal the destruction of stored cookies.
        db (AsyncSession): Asynchronous database session dependency injected via FastAPI Depends.
        user_id (int): Automatically decoded and verified principal identifier parsed by the security middleware layer.

    Returns:
        dict: A simple dictionary wrapper confirming execution via a standardized logout message string.
    """
    auth_service = AuthService(db)
    return await auth_service.log_out_user(response, user_id)
