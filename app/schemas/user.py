from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.types.user import UserRole

DataType = TypeVar("DataType")


class ApiResponse(BaseModel, Generic[DataType]):
    message: str
    data: DataType | None = None


class UserBase(BaseModel):
    name: str = Field(min_length=2, max_length=50, description="The name of the user")
    email: EmailStr
    mobile: str = Field(min_length=10, max_length=15, description="Mobile number of the user")
    address: str = Field(min_length=5, max_length=255)
    role: UserRole
    model_config = ConfigDict(str_strip_whitespace=True)


class SignUpUserRequest(UserBase):
    password: str = Field(min_length=8, max_length=64, strip_whitespace=False)


class LoginUserRequest(BaseModel):
    email: EmailStr = Field(strip_whitespace=True)
    password: str = Field(min_length=8, max_length=64, strip_whitespace=False)


class UserResponse(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


LoginUserResponse = ApiResponse[UserResponse]
LogOutUserResponse = ApiResponse[None]
