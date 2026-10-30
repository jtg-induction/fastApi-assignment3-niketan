from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException, Response, status
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import msg, settings
from app.models.user import User
from app.schemas.user import loginUserRequest, loginUserResponse, signUpUserRequest
from app.utils.utils import raise_http_error

pwd_context = PasswordHash.recommended()


def get_user_by_email(db: Session, email: str) -> User | None:
    stmt = select(User).where(User.email == email)
    return db.scalar(stmt)


def register_user(db: Session, schema_data: signUpUserRequest) -> User:
    existing_user = get_user_by_email(db, schema_data.email)
    if existing_user:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, msg.EMAIL_EXISTS)
    hashed_password = pwd_context.hash(schema_data.password)
    new_user = User(
        name=schema_data.name,
        email=schema_data.email,
        password=hashed_password,
        mobile=schema_data.phone,
        role=schema_data.accountType,
        address=schema_data.address,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def generateAccessToken(id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"id": id, "exp": expire, "type": "access"}
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def generateRefreshToken(id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"id": id, "exp": expire, "type": "refresh"}
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def loginUser(db: Session, response: Response, body_data: loginUserRequest) -> loginUserResponse:
    email = body_data.email
    password = body_data.password
    existing_user: User = get_user_by_email(db, email)
    if not existing_user:
        raise_http_error(status.HTTP_400_BAD_REQUEST, msg.AUTH_FAILED)
    ismatch = pwd_context.verify(password, existing_user.password)
    print(ismatch)
    if not ismatch:
        raise_http_error(status.HTTP_400_BAD_REQUEST, msg.AUTH_FAILED)
    if existing_user.isActive == False:
        raise_http_error(status.HTTP_403_FORBIDDEN, msg.ACCOUNT_INACTIVE)
    access_token = generateAccessToken(existing_user.id)
    refresh_token = generateRefreshToken(existing_user.id)
    existing_user.refreshToken = pwd_context.hash(refresh_token)
    db.commit()
    user_data = {c.name: getattr(existing_user, c.name) for c in existing_user.__table__.columns}

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=False,
        secure=True,
        samesite="none",
        max_age=7 * 24 * 3600,
    )
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=False,
        secure=True,
        samesite="none",
        max_age=15 * 60,
    )
    return {
        **user_data,
        "message": msg.LOGIN_SUCCESS,
    }


def refreshAccessToken(db: Session, response: Response, refresh_token: str | None) -> dict:
    if not refresh_token:
        raise_http_error(status.HTTP_401_UNAUTHORIZED, msg.TOKEN_MISSING)
    try:
        payload = jwt.decode(
            refresh_token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        if payload.get("type") != "refresh":
            raise_http_error(status.HTTP_401_UNAUTHORIZED, msg.TOKEN_INVALID)
        user_id = payload.get("id")
    except InvalidTokenError:
        raise_http_error(status.HTTP_401_UNAUTHORIZED, msg.TOKEN_INVALID)
    stmt = select(User).where(User.id == user_id)
    user = db.scalar(stmt)
    if not user or not user.refreshToken:
        raise_http_error(status.HTTP_401_UNAUTHORIZED, msg.SESSION_EXPIRED)
    isValid = pwd_context.verify(refresh_token, user.refreshToken)
    if not isValid:
        raise_http_error(status.HTTP_401_UNAUTHORIZED, msg.TOKEN_WRONG)
    newAccessToken = generateAccessToken(user_id)
    response.set_cookie(
        key="access_token",
        value=newAccessToken,
        httponly=False,
        secure=True,
        samesite="none",
        max_age=15 * 60,
        path="/",
    )
    return {"message": msg.TOKEN_REFRESH_SUCCESS, "token": newAccessToken}


def logOutUser(db: Session, response: Response, user_id: int) -> dict:
    stmt = select(User).where(User.id == user_id)
    user = db.scalar(stmt)
    if user:
        user.refreshToken = None
        db.commit()
    response.delete_cookie(key="refresh_token", samesite="none", secure=True)
    response.delete_cookie(key="access_token", samesite="none", secure=True)

    return {"message": msg.LOGOUT_SUCCESS}


def getProfile(db: Session, user_id: int):
    print("User,id", user_id)
    stmt = select(User).where(User.id == user_id)
    user = db.scalar(stmt)
    print(user)
    if not user:
        raise_http_error(status.HTTP_404_NOT_FOUND, msg.USER_NOT_FOUND)
    return user
