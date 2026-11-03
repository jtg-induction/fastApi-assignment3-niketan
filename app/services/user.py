from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException, Response, status
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from app.core.config import msg, settings
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import loginUserRequest, loginUserResponse, signUpUserRequest
from app.utils.utils import raise_http_error

pwd_context = PasswordHash.recommended()


def generateAccessToken(id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"id": id, "exp": expire, "type": "access"}
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def generateRefreshToken(id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"id": id, "exp": expire, "type": "refresh"}
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def register_user(db: Session, schema_data: signUpUserRequest) -> User:
    repo = UserRepository(db)

    existing_user = repo.get_by_email(schema_data.email)
    if existing_user:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, msg.EMAIL_EXISTS)

    hashed_password = pwd_context.hash(schema_data.password)
    return repo.create_user(schema_data, hashed_password)


def loginUser(db: Session, response: Response, body_data: loginUserRequest) -> loginUserResponse:
    repo = UserRepository(db)

    existing_user = repo.get_by_email(body_data.email)
    if not existing_user:
        raise_http_error(status.HTTP_400_BAD_REQUEST, msg.AUTH_FAILED)

    if not pwd_context.verify(body_data.password, existing_user.password):
        raise_http_error(status.HTTP_400_BAD_REQUEST, msg.AUTH_FAILED)

    if existing_user.isActive == False:
        raise_http_error(status.HTTP_403_FORBIDDEN, msg.ACCOUNT_INACTIVE)

    access_token = generateAccessToken(existing_user.id)
    refresh_token = generateRefreshToken(existing_user.id)

    repo.update_refresh_token(existing_user, pwd_context.hash(refresh_token))

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

    repo = UserRepository(db)
    user = repo.get_by_id(user_id)

    if not user or not user.refreshToken:
        raise_http_error(status.HTTP_401_UNAUTHORIZED, msg.SESSION_EXPIRED)

    if not pwd_context.verify(refresh_token, user.refreshToken):
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
    repo = UserRepository(db)
    user = repo.get_by_id(user_id)
    if user:
        repo.update_refresh_token(user, None)
    response.delete_cookie(key="refresh_token", samesite="none", secure=True)
    response.delete_cookie(key="access_token", samesite="none", secure=True)

    return {"message": msg.LOGOUT_SUCCESS}


def getProfile(db: Session, user_id: int):
    repo = UserRepository(db)
    user = repo.get_by_id(user_id)
    if not user:
        raise_http_error(status.HTTP_404_NOT_FOUND, msg.USER_NOT_FOUND)
    return user
