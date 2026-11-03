from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import signUpUserRequest


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> User | None:
        stmt = select(User).where(User.id == user_id)
        return self.db.scalar(stmt)

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        return self.db.scalar(stmt)

    def create_user(self, schema_data: signUpUserRequest, hashed_password: str) -> User:
        new_user = User(
            name=schema_data.name,
            email=schema_data.email,
            password=hashed_password,
            mobile=schema_data.phone,
            role=schema_data.accountType,
            address=schema_data.address,
        )
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user

    def update_refresh_token(self, user: User, hashed_refresh_token: str | None) -> None:
        user.refreshToken = hashed_refresh_token
        self.db.commit()
