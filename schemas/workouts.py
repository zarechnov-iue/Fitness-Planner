from enum import Enum
from typing import Optional, List

from pydantic import BaseModel

from .exercises import ExerciseResponse


class WorkoutType(str, Enum):
    strength = "strength"
    cardio = "cardio"
    flexibility = "flexibility"


class WorkoutBase(BaseModel):
    name: str
    description: Optional[str] = None
    duration_minutes: int
    workout_type: WorkoutType


class WorkoutCreate(WorkoutBase):
    pass


class WorkoutResponse(WorkoutBase):
    id: int
    user_id: int
    created_at: Optional[str]
    exercises: List[ExerciseResponse] = []

    class Config:
        from_attributes = True
