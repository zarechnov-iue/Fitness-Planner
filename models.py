import datetime

from sqlalchemy import Column, Integer, String, Enum, DateTime

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(100), nullable=False)
    experience_level = Column(Enum('beginner', 'intermediate', 'advanced'), nullable=False)
    goal = Column(Enum('weight_loss', 'muscle_gain', 'endurance'), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now)


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
