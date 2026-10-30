import os

import jwt
from fastapi import Cookie, HTTPException, status
from jwt.exceptions import DecodeError

from app.core.config import settings

JWT_SECRET = settings.JWT_SECRET


def get_current_user_id(
    access_token: str | None = Cookie(default=None, alias="access_token"),
) -> int:
    print("accesstoken", access_token)
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token missing. Please log in.",
        )
    try:
        payload = jwt.decode(access_token, JWT_SECRET, algorithms=["HS256"])

        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type.",
            )

        user_id = payload.get("id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload.",
            )

        return int(user_id)

    except DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or invalid token.",
        )
