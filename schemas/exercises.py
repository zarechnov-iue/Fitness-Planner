from enum import Enum
from typing import Optional

from pydantic import BaseModel


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
