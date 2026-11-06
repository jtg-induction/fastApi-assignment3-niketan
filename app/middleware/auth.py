import jwt
from fastapi import Cookie
from jwt.exceptions import DecodeError

from app.core.config import settings
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
