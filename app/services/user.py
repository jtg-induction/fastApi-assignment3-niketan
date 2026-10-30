import os
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, Response, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import loginUserRequest, loginUserResponse, signUpUserRequest
from app.utils.utils import raise_http_error

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

JWT_SECRET = os.getenv("JWT_SECRET", "supersecretkey")


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def register_user(db: Session, schema_data: signUpUserRequest) -> User:
    existing_user = get_user_by_email(db, schema_data.email)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="email already exists")
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
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
    )
    to_encode = {"id": id, "exp": expire, "type": "access"}
    return jwt.encode(to_encode, JWT_SECRET, algorithm="HS256")


def generateRefreshToken(id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        days=int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))
    )
    to_encode = {"id": id, "exp": expire, "type": "refresh"}
    return jwt.encode(to_encode, JWT_SECRET, algorithm="HS256")


def loginUser(db: Session, response: Response, body_data: loginUserRequest) -> loginUserResponse:
    email = body_data.email
    password = body_data.password
    existing_user: User = get_user_by_email(db, email)
    if not existing_user:
        raise_http_error(status.HTTP_400_BAD_REQUEST, "Email or password is incorrect")
    ismatch = pwd_context.verify(password, existing_user.password)
    print(ismatch)
    if not ismatch:
        raise_http_error(status.HTTP_400_BAD_REQUEST, "Email or password is incorrect")
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
        "message": "user logged in successfully",
    }


def refreshAccessToken(db: Session, response: Response, refresh_token: str | None) -> dict:
    if not refresh_token:
        raise_http_error(status.HTTP_401_UNAUTHORIZED, "Refresh token missing")
    try:
        payload = jwt.decode(refresh_token, JWT_SECRET, algorithms=["HS256"])
        if payload.get("type") != "refresh":
            raise_http_error(status.HTTP_401_UNAUTHORIZED, "Invalid Token")
        user_id = payload.get("id")
    except JWTError:
        raise_http_error(status.HTTP_401_UNAUTHORIZED, "invalid Token")
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.refreshToken:
        raise_http_error(status.HTTP_401_UNAUTHORIZED, "Session expired")
    isValid = pwd_context.verify(refresh_token, user.refreshToken)
    if not isValid:
        raise_http_error(status.HTTP_401_UNAUTHORIZED, "wrong token")
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
    return {"message": "new Access Token generated successfully", "token": newAccessToken}


def logOutUser(db: Session, response: Response, user_id: int) -> dict:
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.refreshToken = None
        db.commit()
    response.delete_cookie(key="refresh_token", samesite="none", secure=True)
    response.delete_cookie(key="access_token", samesite="none", secure=True)

    return {"message": "Logged out successfully"}


def getProfile(db: Session, user_id: int):
    print("User,id", user_id)
    user = db.query(User).filter(User.id == user_id).first()
    print(user)
    if not user:
        raise_http_error(status.HTTP_404_NOT_FOUND, "User not found")
    return user
