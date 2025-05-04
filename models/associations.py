from sqlalchemy import Column, Integer, ForeignKey, Table

from core.database import Base

workout_exercises = Table(
    "workout_exercises",
    Base.metadata,
    Column("workout_id", Integer, ForeignKey("workouts.id"), primary_key=True),
    Column("exercise_id", Integer, ForeignKey("exercises.id"), primary_key=True)
)
