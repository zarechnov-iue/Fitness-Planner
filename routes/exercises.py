from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database import get_db
from models.exercises import Exercise
from schemas.exercises import ExerciseCreate, ExerciseResponse

router = APIRouter(prefix="/exercises", tags=["Exercises"])


def get_exercise_by_id(db: Session, exercise_id: int):
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return exercise


@router.post("/", response_model=ExerciseResponse, status_code=status.HTTP_201_CREATED)
def create_exercise(exercise: ExerciseCreate, db: Session = Depends(get_db)):
    db_exercise = Exercise(**exercise.dict())
    db.add(db_exercise)
    db.commit()
    db.refresh(db_exercise)
    return db_exercise.to_dict()


@router.get("/", response_model=list[ExerciseResponse])
def get_exercises(db: Session = Depends(get_db)):
    exercises = db.query(Exercise).all()
    return [e.to_dict() for e in exercises]


@router.get("/{exercise_id}", response_model=ExerciseResponse)
def get_exercise(exercise_id: int, db: Session = Depends(get_db)):
    exercise = get_exercise_by_id(db, exercise_id)
    return exercise.to_dict()


@router.put("/{exercise_id}", response_model=ExerciseResponse)
def update_exercise(exercise_id: int, updated_data: ExerciseCreate, db: Session = Depends(get_db)):
    exercise = get_exercise_by_id(db, exercise_id)

    for key, value in updated_data.dict().items():
        setattr(exercise, key, value)

    db.commit()
    db.refresh(exercise)
    return exercise.to_dict()


@router.delete("/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exercise(exercise_id: int, db: Session = Depends(get_db)):
    exercise = get_exercise_by_id(db, exercise_id)
    db.delete(exercise)
    db.commit()
    return {"detail": "Exercise deleted"}
