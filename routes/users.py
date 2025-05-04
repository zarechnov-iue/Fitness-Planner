from fastapi import APIRouter, Depends, HTTPException
from fastapi import status
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import get_current_user
from core.security import get_password_hash
from models.users import User
from schemas.users import UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["Users"])


# GET /users - получить всех пользователей
@router.get("/", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users


# GET /users/{user_email} - получить пользователя по email
@router.get("/{user_email}", response_model=UserResponse)
def get_user(user_email: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if user_email != current_user.email:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                            detail="You can watch information only by your user.")
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


# PUT /users/{user_email} - обновить пользователя
@router.put("/{user_email}", response_model=UserResponse)
def update_user(user_email: str, user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user_email).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user.name:
        db_user.name = user.name
    if user.email:
        db_user.email = user.email
    if user.password:
        db_user.password_hash = get_password_hash(user.password)
    if user.experience_level:
        db_user.experience_level = user.experience_level
    if user.goal:
        db_user.goal = user.goal

    db.commit()
    db.refresh(db_user)
    return db_user


# DELETE /users/{user_email}
@router.delete("/{user_email}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_email: str, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user_email).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"detail": "User deleted"}
