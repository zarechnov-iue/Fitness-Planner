from fastapi import APIRouter, HTTPException
from fastapi import Response, Depends
from fastapi import status
from sqlalchemy.orm import Session

from core.security import verify_password, get_db, get_password_hash, create_user_header
from models.users import User
from schemas.auth import LoginRequest
from schemas.users import UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["Security"])

ACCESS_TOKEN_EXPIRE_MINUTES = 5


@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=UserResponse,
             summary='Добавить пользователя')
def create_user(user: UserCreate, response: Response, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User with this email already exists"
        )

    db_user = User(
        name=user.name,
        email=user.email,
        password_hash=get_password_hash(user.password),
        experience_level=user.experience_level,
        goal=user.goal
    )

    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        response.headers["Authorization"] = create_user_header(user.email)

        return db_user
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while creating the user")


@router.post("/login", status_code=status.HTTP_200_OK, summary='Войти в систему')
def user_login(login_attempt: LoginRequest = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_attempt.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"User {login_attempt.username} not found"
        )

    if verify_password(login_attempt.password, user.password_hash):
        access_token = create_user_header(user.email)
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Wrong password for user {login_attempt.email}"
        )
