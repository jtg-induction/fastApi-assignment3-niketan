from datetime import datetime, timedelta, timezone

import anyio
import jwt
from fastapi import Response, status
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Messages, settings
from app.core.constant import access_token_max_age, refresh_token_max_age
from app.repositories.user import UserRepository
from app.schemas.user import (
    LoginUserRequest,
    LoginUserResponse,
    LogOutUserResponse,
)
from app.utils.utils import raise_http_error


class AuthService:
    """Handles business logic for user authentication, sessions, and JWT tokens."""

    def __init__(self, db: AsyncSession):
        """Initialize authentication service dependencies.
        Args:
           db (AsyncSession): Asynchronous SQLAlchemy database session.
        """
        self.db = db
        self.repo = UserRepository(db)
        self.pwd_context = PasswordHash.recommended()
        self.jwt_secret = settings.JWT_SECRET.get_secret_value()

    def generate_access_token(self, id: int) -> str:
        """Create a short-lived JWT access token for API authorization.
          Args:
            id (int): The primary key ID of the user.

        Returns:
            str: Encoded JWT access token string.
        """
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode = {"id": id, "exp": expire, "type": "access"}
        return jwt.encode(to_encode, self.jwt_secret, algorithm=settings.JWT_ALGORITHM)

    def generate_refresh_token(self, id: int) -> str:
        """Create a long-lived JWT refresh token used to request new access tokens.
         Args:
            id (int): The primary key ID of the user.

        Returns:
            str: Encoded JWT refresh token string.
        """

        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode = {"id": id, "exp": expire, "type": "refresh"}
        return jwt.encode(to_encode, self.jwt_secret, algorithm=settings.JWT_ALGORITHM)

    async def login_user(
        self, response: Response, body_data: LoginUserRequest
    ) -> LoginUserResponse:
        """Authenticate user credentials, save refresh token, and set auth cookies.
        Args:
            response (Response): FastAPI Response object used to set cookies.
            body_data (LoginUserRequest): Pydantic schema containing user login credentials (email and password).

        Returns:
            LoginUserResponse: Dictionary containing user data and a login success message.
        """

        existing_user = await self.repo.get_by_email(str(body_data.email))
        if not existing_user:
            raise_http_error(status.HTTP_400_BAD_REQUEST, Messages.AUTH_FAILED)

        is_valid_password = await anyio.to_thread.run_sync(
            self.pwd_context.verify, body_data.password, existing_user.password
        )
        if not is_valid_password:
            raise_http_error(status.HTTP_400_BAD_REQUEST, Messages.AUTH_FAILED)

        if not existing_user.is_active:
            raise_http_error(status.HTTP_403_FORBIDDEN, Messages.ACCOUNT_INACTIVE)

        access_token = self.generate_access_token(existing_user.id)
        refresh_token = self.generate_refresh_token(existing_user.id)

        user_data = {
            c.name: getattr(existing_user, c.name) for c in existing_user.__table__.columns
        }
        try:
            await self.repo.update_refresh_token(existing_user, refresh_token)
            await self.db.commit()
        except Exception:
            await self.db.rollback()
            raise

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=False,
            secure=True,
            samesite="none",
            max_age=refresh_token_max_age,
        )
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=False,
            secure=True,
            samesite="none",
            max_age=access_token_max_age,
        )
        return {
            "data": user_data,
            "message": Messages.LOGIN_SUCCESS,
        }

    async def refresh_access_token(self, response: Response, refresh_token: str | None) -> dict:
        """Validate an active refresh token and issue a new access token cookie.
         Args:
            response (Response): FastAPI Response object used to set the new access token cookie.
            refresh_token (str | None): The refresh token string extracted from cookies or requests.

        Returns:
            dict: Dictionary containing a success message and the newly generated access token.
        """
        if not refresh_token:
            raise_http_error(status.HTTP_401_UNAUTHORIZED, Messages.TOKEN_MISSING)
        try:
            payload = jwt.decode(
                refresh_token, self.jwt_secret, algorithms=[settings.JWT_ALGORITHM]
            )
            if payload.get("type") != "refresh":
                raise_http_error(status.HTTP_401_UNAUTHORIZED, Messages.TOKEN_INVALID)
            user_id = payload.get("id")
        except InvalidTokenError:
            raise_http_error(status.HTTP_401_UNAUTHORIZED, Messages.TOKEN_INVALID)

        user = await self.repo.get_by_id(user_id)

        if not user or not user.refresh_token:
            raise_http_error(status.HTTP_401_UNAUTHORIZED, Messages.SESSION_EXPIRED)

        is_valid_token = await anyio.to_thread.run_sync(
            self.pwd_context.verify, refresh_token, user.refresh_token
        )
        if not is_valid_token:
            raise_http_error(status.HTTP_401_UNAUTHORIZED, Messages.TOKEN_WRONG)

        new_access_token = self.generate_access_token(user_id)
        response.set_cookie(
            key="access_token",
            value=new_access_token,
            httponly=False,
            secure=True,
            samesite="none",
            max_age=access_token_max_age,
            path="/",
        )
        return {"message": Messages.TOKEN_REFRESH_SUCCESS, "token": new_access_token}

    async def log_out_user(self, response: Response, user_id: int) -> LogOutUserResponse:
        """Log out the user by clearing their refresh token in the database and deleting auth cookies.

        Args:
            response (Response): FastAPI Response object used to delete auth cookies.
            user_id (int): The primary key ID of the user logging out.

        Returns:
            LogOutUserResponse: Dictionary containing a logout success message.
        """

        user = await self.repo.get_by_id(user_id)
        if user:
            try:
                await self.repo.update_refresh_token(user, None)
                await self.db.commit()
            except Exception:
                await self.db.rollback()
                raise

        response.delete_cookie(key="refresh_token", samesite="none", secure=True)
        response.delete_cookie(key="access_token", samesite="none", secure=True)

        return {"message": Messages.LOGOUT_SUCCESS}
