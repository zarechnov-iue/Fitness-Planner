from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import get_current_user
from models.workouts import Workout
from schemas.workouts import WorkoutCreate, WorkoutResponse

router = APIRouter(prefix="/workouts", tags=["Workouts"])


def get_workout_by_id(db: Session, workout_id: int, user_id: int):
    workout = db.query(Workout).filter(
        Workout.id == workout_id,
        Workout.user_id == user_id
    ).first()
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found or access denied")
    return workout


@router.get("/", response_model=list[WorkoutResponse])
def get_workouts(current_user: int = Depends(get_current_user), db: Session = Depends(get_db)):
    workouts = db.query(Workout).filter(Workout.user_id == current_user.id).all()
    return [w.to_dict() for w in workouts]


@router.get("/{workout_id}", response_model=WorkoutResponse)
def get_workout(workout_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    workout = get_workout_by_id(db, workout_id, current_user.id)
    return workout.to_dict()


@router.post("/", response_model=WorkoutResponse, status_code=status.HTTP_201_CREATED)
def create_workout(workout: WorkoutCreate, current_user=Depends(get_current_user),
                   db: Session = Depends(get_db)):
    db_workout = Workout(
        name=workout.name,
        description=workout.description,
        duration_minutes=workout.duration_minutes,
        workout_type=workout.workout_type,
        user_id=current_user.id
    )

    db.add(db_workout)
    db.commit()
    db.refresh(db_workout)
    return db_workout.to_dict()


@router.put("/{workout_id}", response_model=WorkoutResponse)
def update_workout(workout_id: int, updated_data: WorkoutCreate, current_user=Depends(get_current_user),
                   db: Session = Depends(get_db)):
    workout = get_workout_by_id(db, workout_id, current_user.id)

    for key, value in updated_data.dict().items():
        setattr(workout, key, value)

    db.commit()
    db.refresh(workout)
    return workout.to_dict()


@router.delete("/{workout_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workout(workout_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    workout = get_workout_by_id(db, workout_id, current_user.id)
    db.delete(workout)
    db.commit()
    return {"detail": "Workout deleted"}
