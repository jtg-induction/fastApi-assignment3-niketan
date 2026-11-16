from typing import Annotated

import jwt
from fastapi import Cookie, Depends, HTTPException, status
from jwt.exceptions import DecodeError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.utils.Exceptions import UnauthorizedException

JWT_SECRET = settings.JWT_SECRET.get_secret_value()


def get_current_user_id(
    access_token: str | None = Cookie(default=None, alias="access_token"),
) -> int:
    """this function is used to validate the access token from cookie and return the user id if token is valid
    Args:
        access_token: take access_token from cookie
    Returns:
        return the user id
    """
    if not access_token:
        raise UnauthorizedException("Authentication token missing. Please log in.")
    try:
        payload = jwt.decode(access_token, JWT_SECRET, algorithms=["HS256"])

        if payload.get("type") != "access":
            raise UnauthorizedException("Invalid token type.")

        user_id = payload.get("id")
        if user_id is None:
            raise UnauthorizedException("Invalid token payload.")

        return int(user_id)

    except DecodeError as err:
        raise UnauthorizedException("Session expired or invalid token.") from err


async def get_customer_user_id(
    user_id: Annotated[int, Depends(get_current_user_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> int:
    """Fetches user role from DB, blocks OWNERs, and returns user_id."""
    result = await db.execute(select(User.role).where(User.id == user_id))
    role = result.scalar_one_or_none()

    if role is None:
        raise UnauthorizedException("User not found.")

    if role == "OWNER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owners are not permitted to create carts or place orders.",
        )

    return user_id


async def get_owner_user_id(
    user_id: Annotated[int, Depends(get_current_user_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> int:
    """Ensures the authenticated user has the OWNER role and returns user_id."""
    result = await db.execute(select(User.role).where(User.id == user_id))
    role = result.scalar_one_or_none()

    if role is None:
        raise UnauthorizedException("User not found.")

    if role != "OWNER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only restaurant owners can update order status.",
        )

    return user_id
