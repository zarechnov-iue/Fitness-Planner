from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from core.database import get_db
from core.security import get_current_user
from models.exercises import Exercise
from models.workouts import Workout
from schemas.exercises import ExerciseCreate, ExerciseResponse
from schemas.workouts import WorkoutCreate, WorkoutResponse

router = APIRouter(prefix="/workouts", tags=["Workouts"])


def get_workout_by_id(db: Session, workout_id: int, user_id: int):
    workout = db.query(Workout).options(joinedload(Workout.exercises)).filter(
        Workout.id == workout_id,
        Workout.user_id == user_id
    ).first()
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found or access denied")
    return workout


def get_exercise_by_id(db: Session, exercise_id: int):
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return exercise


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


@router.post("/{workout_id}/add-exercise", status_code=status.HTTP_200_OK)
def add_exercise_to_workout(workout_id: int, exercise_id: int, current_user=Depends(get_current_user),
                            db: Session = Depends(get_db)):
    workout = get_workout_by_id(db, workout_id, current_user.id)
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")

    if exercise in workout.exercises:
        raise HTTPException(status_code=400, detail="Exercise already in workout")

    workout.exercises.append(exercise)
    db.commit()
    return {"detail": "Exercise added to workout"}


@router.post("/{workout_id}/exercises", response_model=ExerciseResponse, status_code=status.HTTP_201_CREATED)
def create_exercise_and_link_to_workout(
        workout_id: int,
        exercise_data: ExerciseCreate,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Создаёт новое упражнение и сразу связывает его с указанной тренировкой.
    """
    # Получаем тренировку
    workout = get_workout_by_id(db, workout_id, current_user.id)

    # Создаём упражнение
    db_exercise = Exercise(**exercise_data.dict())
    db.add(db_exercise)
    db.flush()  # Чтобы получить ID упражнения

    # Связываем через many-to-many
    workout.exercises.append(db_exercise)
    db.commit()
    db.refresh(db_exercise)

    return db_exercise.to_dict()


@router.get("/{workout_id}/exercises", response_model=list[ExerciseResponse])
def get_exercises_in_workout(workout_id: int, current_user=Depends(get_current_user),
                             db: Session = Depends(get_db)):
    workout = get_workout_by_id(db, workout_id, current_user.id)
    return [e.to_dict() for e in workout.exercises]


@router.get("/{workout_id}/exercises/{exercise_id}", response_model=ExerciseResponse)
def get_exercise_in_workout(workout_id: int, exercise_id: int, current_user=Depends(get_current_user),
                            db: Session = Depends(get_db)):
    workout = get_workout_by_id(db, workout_id, current_user.id)
    exercise = next((e for e in workout.exercises if e.id == exercise_id), None)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found in this workout")
    return exercise.to_dict()


@router.put("/{workout_id}/exercises/{exercise_id}", response_model=ExerciseResponse)
def update_exercise_in_workout(
        workout_id: int,
        exercise_id: int,
        updated_data: ExerciseCreate,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    workout = get_workout_by_id(db, workout_id, current_user.id)
    exercise = next((e for e in workout.exercises if e.id == exercise_id), None)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found in this workout")

    for key, value in updated_data.dict(exclude_unset=True).items():
        setattr(exercise, key, value)

    db.commit()
    db.refresh(exercise)
    return exercise.to_dict()


@router.delete("/{workout_id}/exercises/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exercise_from_workout(
        workout_id: int,
        exercise_id: int,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    workout = get_workout_by_id(db, workout_id, current_user.id)
    exercise = next((e for e in workout.exercises if e.id == exercise_id), None)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found in this workout")

    workout.exercises.remove(exercise)
    db.commit()
    return {"detail": "Exercise removed from workout"}
