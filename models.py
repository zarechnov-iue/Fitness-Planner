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
