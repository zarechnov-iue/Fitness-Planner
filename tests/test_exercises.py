from fastapi.testclient import TestClient

from fixture import registered_user, client
from schemas.exercises import ExerciseType
from schemas.workouts import WorkoutType


def test_get_exercises_in_workout(client: TestClient, registered_user):
    headers = {"Authorization": registered_user["token"]}

    # Создаём тренировку
    workout_response = client.post("/workouts", json={
        "name": "Test Workout",
        "description": "For testing linked exercises",
        "duration_minutes": 60,
        "workout_type": WorkoutType.cardio
    }, headers=headers)
    assert workout_response.status_code == 201
    workout_id = workout_response.json()["id"]

    # Добавляем упражнение в тренировку
    exercise_payload = {
        "name": "Jumping Jacks",
        "description": "Warm-up cardio",
        "calories_per_minute": 10,
        "exercise_type": ExerciseType.cardio
    }

    link_response = client.post(f"/workouts/{workout_id}/exercises", json=exercise_payload, headers=headers)
    assert link_response.status_code == 201

    # Получаем список упражнений
    get_response = client.get(f"/workouts/{workout_id}/exercises", headers=headers)
    assert get_response.status_code == 200
    data = get_response.json()

    assert len(data) >= 1
    assert any(e["name"] == "Jumping Jacks" for e in data)


def test_get_exercise_in_workout(client: TestClient, registered_user):
    headers = {"Authorization": registered_user["token"]}

    # Создаём тренировку
    workout_response = client.post("/workouts", json={
        "name": "Another Workout",
        "description": "For detailed exercise",
        "duration_minutes": 45,
        "workout_type": WorkoutType.strength.value
    }, headers=headers)
    assert workout_response.status_code == 201
    workout_id = workout_response.json()["id"]

    # Добавляем упражнение
    exercise_payload = {
        "name": "Push-ups",
        "description": "Classic bodyweight exercise",
        "calories_per_minute": 8,
        "exercise_type": ExerciseType.strength.value
    }
    link_response = client.post(f"/workouts/{workout_id}/exercises", json=exercise_payload, headers=headers)
    assert link_response.status_code == 201
    exercise_id = link_response.json()["id"]

    # Проверяем GET по ID
    get_response = client.get(f"/workouts/{workout_id}/exercises/{exercise_id}", headers=headers)
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == exercise_id
    assert data["name"] == "Push-ups"


# test/test_workouts.py

from fastapi.testclient import TestClient


# Вспомогательная функция: создаём тестовую тренировку
def create_test_workout(client: TestClient, headers: dict):
    payload = {
        "name": "Test Workout",
        "description": "For testing exercises",
        "duration_minutes": 60,
        "workout_type": WorkoutType.cardio.value
    }
    response = client.post("/workouts", json=payload, headers=headers)
    assert response.status_code == 201
    return response.json()["id"]


# Вспомогательная функция: добавляем упражнение к тренировке
def add_exercise_to_workout(client: TestClient, headers: dict, workout_id: int):
    payload = {
        "name": "Push-ups",
        "description": "Classic bodyweight exercise",
        "calories_per_minute": 8,
        "exercise_type": ExerciseType.strength.value
    }
    response = client.post(f"/workouts/{workout_id}/exercises", json=payload, headers=headers)
    assert response.status_code == 201
    return response.json()["id"]


def test_update_exercise_in_workout(client: TestClient, registered_user):
    headers = {"Authorization": registered_user["token"]}

    # Создаём тренировку и упражнение
    workout_id = create_test_workout(client, headers)
    exercise_id = add_exercise_to_workout(client, headers, workout_id)

    # Обновляем упражнение
    updated_data = {
        "name": "Updated Push-ups",
        "description": "More intense version",
        "calories_per_minute": 9,
        "exercise_type": ExerciseType.strength.value
    }

    put_response = client.put(f"/workouts/{workout_id}/exercises/{exercise_id}", json=updated_data, headers=headers)
    assert put_response.status_code == 200
    data = put_response.json()

    assert data["name"] == updated_data["name"]
    assert data["calories_per_minute"] == updated_data["calories_per_minute"]


def test_delete_exercise_from_workout(client: TestClient, registered_user):
    headers = {"Authorization": registered_user["token"]}

    workout_id = create_test_workout(client, headers)
    exercise_id = add_exercise_to_workout(client, headers, workout_id)

    del_response = client.delete(f"/workouts/{workout_id}/exercises/{exercise_id}", headers=headers)
    assert del_response.status_code == 204

    # Проверяем, что его больше нет
    get_response = client.get(f"/workouts/{workout_id}/exercises/{exercise_id}", headers=headers)
    assert get_response.status_code == 404
