import hashlib

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.database import get_db
from models.users import User
from schemas.users import UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["Users"])


# Хэширование пароля
def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()


# GET /users - получить всех пользователей
@router.get("/", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users


# GET /users/{user_email} - получить пользователя по email
@router.get("/{user_email}", response_model=UserResponse)
def get_user(user_email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# POST /users - создать нового пользователя
@router.post("/", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User with this email already exists"
        )

    db_user = User(
        name=user.name,
        email=user.email,
        password_hash=hash_password(user.password),
        experience_level=user.experience_level,
        goal=user.goal
    )

    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while creating the user")


# PUT /users/{user_email} - обновить пользователя
@router.put("/{user_email}", response_model=UserResponse)
def update_user(user_email: str, user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user_email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.name:
        db_user.name = user.name
    if user.email:
        db_user.email = user.email
    if user.password:
        db_user.password_hash = hash_password(user.password)
    if user.experience_level:
        db_user.experience_level = user.experience_level
    if user.goal:
        db_user.goal = user.goal

    db.commit()
    db.refresh(db_user)
    return db_user


# DELETE /users/{user_email}
@router.delete("/{user_email}", status_code=204)
def delete_user(user_email: str, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user_email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"detail": "User deleted"}
