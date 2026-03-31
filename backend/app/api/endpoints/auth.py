from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import UserCreate, UserResponse, TokenResponse
from app.crud.user import get_user_by_email, create_user, authenticate_user
from app.core.security import create_access_token

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    # 1. check if email already exists → 409 if yes
    # 2. create and return the user
    ...


@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # 1. authenticate_user using form_data.username and form_data.password
    # 2. if None → raise 401
    # 3. create token with user's email as subject
    # 4. return TokenResponse
    ...