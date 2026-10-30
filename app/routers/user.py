from fastapi import APIRouter, Cookie, Depends, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.middleware.auth import get_current_user_id
from app.schemas.user import (
    UserResponse,
    loginUserRequest,
    loginUserResponse,
    signUpUserRequest,
)
from app.services.user import (
    getProfile,
    loginUser,
    logOutUser,
    refreshAccessToken,
    register_user,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def create_user(body_data: signUpUserRequest, db: Session = Depends(get_db)):
    return register_user(db, body_data)


@router.post("/login", status_code=status.HTTP_201_CREATED, response_model=loginUserResponse)
def login_user(body_data: loginUserRequest, response: Response, db: Session = Depends(get_db)):
    return loginUser(db, response, body_data)


@router.post("/refresh", status_code=status.HTTP_200_OK, response_model=dict)
def refreshToken(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
):
    return refreshAccessToken(db, response, refresh_token)


@router.post("/logout", status_code=200, response_model=dict)
def logOut(
    response: Response, db: Session = (Depends(get_db)), user_id: int = Depends(get_current_user_id)
):
    return logOutUser(db, response, user_id)


@router.get("/me", status_code=status.HTTP_200_OK, response_model=UserResponse)
def get_current_user_profile(
    db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)
):
    return getProfile(db, user_id)
