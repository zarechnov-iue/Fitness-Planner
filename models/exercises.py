import datetime

from sqlalchemy import Column, Integer, String, Enum, DateTime

from core.database import Base


class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    calories_per_minute = Column(Integer, nullable=False)
    exercise_type = Column(Enum('cardio', 'strength', 'flexibility'), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "calories_per_minute": self.calories_per_minute,
            "exercise_type": self.exercise_type,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
