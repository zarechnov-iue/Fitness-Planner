from datetime import datetime

from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from core.database import Base
from models.associations import workout_exercises


class Workout(Base):
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    duration_minutes = Column(Integer, nullable=False)
    workout_type = Column(Enum('strength', 'cardio', 'flexibility'), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    user = relationship("User", back_populates="workouts")
    exercises = relationship("Exercise", secondary=workout_exercises, back_populates="workouts")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "duration_minutes": self.duration_minutes,
            "workout_type": self.workout_type,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "exercises": [e.to_dict() for e in self.exercises]
        }
