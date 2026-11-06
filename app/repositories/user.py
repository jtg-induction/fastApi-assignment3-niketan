from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import SignUpUserRequest


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    async def get_by_id(self, user_id: int) -> User | None:
        stmt = select(User).where(User.id == user_id)
        return await self.db.scalar(stmt)

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        return await self.db.scalar(stmt)

    async def create_user(self, user_payload: SignUpUserRequest, hashed_password: str) -> User:
        new_user = User(
            name=user_payload.name,
            email=user_payload.email,
            password=hashed_password,
            mobile=user_payload.mobile,
            role=user_payload.role,
            address=user_payload.address,
        )
        self.db.add(new_user)
        return new_user

    async def update_refresh_token(self, user: User, hashed_refresh_token: str | None) -> None:
        user.refresh_token = hashed_refresh_token
