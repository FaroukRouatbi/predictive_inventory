from app.schemas.user import UserCreate
from app.models.user import User
from pydantic import EmailStr
from sqlalchemy.orm import Session
from typing import Optional
from app.core.security import hash_password, verify_password


def get_user_by_email(db: Session, email: EmailStr) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user_in: UserCreate) -> User:
    hashed_password = hash_password(user_in.password)
    db_user = User(
        email = user_in.email,
        full_name = user_in.full_name,
        hashed_password = hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

def authenticate_user(db: Session, email: EmailStr, password: str) -> Optional[User]:
    db_user = get_user_by_email(db, email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user