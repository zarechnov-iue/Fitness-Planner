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


class ExerciseType(str, Enum):
    cardio = "cardio"
    strength = "strength"
    flexibility = "flexibility"


class ExerciseBase(BaseModel):
    name: str
    description: Optional[str] = None
    calories_per_minute: int
    exercise_type: ExerciseType


class ExerciseCreate(ExerciseBase):
    pass


class ExerciseResponse(ExerciseBase):
    id: int
    created_at: Optional[str]

    class Config:
        from_attributes = True
