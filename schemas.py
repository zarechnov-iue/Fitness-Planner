from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class UserExperience(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


class UserGoal(str, Enum):
    weight_loss = "weight_loss"
    muscle_gain = "muscle_gain"
    endurance = "endurance"


# Базовая схема
class UserBase(BaseModel):
    name: str
    email: str
    experience_level: UserExperience
    goal: UserGoal


# Для создания пользователя
class UserCreate(UserBase):
    password: str


# Для ответа API
class UserResponse(UserBase):
    id: int
    created_at: Optional[datetime]

    class Config:
        from_attributes = True
