import anyio
from fastapi import HTTPException, status
from pwdlib import PasswordHash
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Messages
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import (
    SignUpUserRequest,
)
from app.utils.utils import raise_http_error


class UserService:
    """Handles business logic for user management."""

    def __init__(self, db: AsyncSession):
        """Initialize service with async database session.
        Args:
            db (AsyncSession): Asynchronous SQLAlchemy database session.
        """
        self.db = db
        self.pwd_context = PasswordHash.recommended()

        self.repo = UserRepository(db)

    async def register_user(self, schema_data: SignUpUserRequest) -> User:
        """Validate email, hash password in a background thread, and save user.
         Args:
            schema_data (SignUpUserRequest): Pydantic schema containing registration details (email, password, etc.).

        Returns:
            User: The newly created and persisted SQLAlchemy User model instance.
        """
        existing_user = await self.repo.get_by_email(schema_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=Messages.EMAIL_EXISTS
            )

        hashed_password = await anyio.to_thread.run_sync(
            self.pwd_context.hash, schema_data.password
        )
        try:
            new_user = await self.repo.create_user(schema_data, hashed_password)
            await self.db.commit()
            await self.db.refresh(new_user)
            return new_user
        except Exception:
            await self.db.rollback()
            raise

    async def get_profile(self, user_id: int) -> User:
        """Fetch user profile by ID or raise 404 error if not found.
        Args:
            user_id (int): The primary key ID of the user whose profile is being requested.

        Returns:
            User: The SQLAlchemy User model instance representing the user's profile.
        """
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise_http_error(status.HTTP_404_NOT_FOUND, Messages.USER_NOT_FOUND)
        return user
