from enum import Enum

from pydantic import BaseModel, EmailStr


class RoleEnum(str, Enum):
    OWNER = "OWNER"
    CUSTOMER = "CUSTOMER"


class signUpUserRequest(BaseModel):
    name: str
    email: EmailStr
    phone: str
    address: str
    password: str
    accountType: RoleEnum


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    mobile: str
    role: RoleEnum

    class Config:
        from_attributes = True


class loginUserResponse(UserResponse):
    message: str


class loginUserRequest(BaseModel):
    email: EmailStr
    password: str
