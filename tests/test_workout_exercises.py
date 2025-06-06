from fastapi.testclient import TestClient

from fixture import registered_user, client
from schemas.exercises import ExerciseType
from schemas.workouts import WorkoutType


def test_create_workout(client: TestClient, registered_user):
    headers = {"Authorization": registered_user["token"]}
    payload = {
        "name": "Morning Cardio",
        "description": "30 minutes of light jogging",
        "duration_minutes": 30,
        "workout_type": WorkoutType.cardio
    }

    response = client.post("/workouts", json=payload, headers=headers)
    assert response.status_code == 201

    data = response.json()
    assert data["name"] == payload["name"]
    assert data["description"] == payload["description"]
    assert data["duration_minutes"] == payload["duration_minutes"]
    assert data["workout_type"] == payload["workout_type"]
    assert "id" in data
    assert "created_at" in data


def test_get_all_workouts(client: TestClient, registered_user):
    headers = {"Authorization": registered_user["token"]}

    # Создаём несколько тренировок
    workout1 = {
        "name": "Morning Run",
        "description": "Light running",
        "duration_minutes": 45,
        "workout_type": WorkoutType.cardio
    }
    workout2 = {
        "name": "Upper Body Strength",
        "description": "Push-ups and pull-ups",
        "duration_minutes": 30,
        "workout_type": WorkoutType.strength
    }

    client.post("/workouts", json=workout1, headers=headers)
    client.post("/workouts", json=workout2, headers=headers)

    response = client.get("/workouts", headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert len(data) >= 2
    assert any(item["name"] == workout1["name"] for item in data)
    assert any(item["name"] == workout2["name"] for item in data)


def test_get_workout_by_id(client: TestClient, registered_user):
    headers = {"Authorization": registered_user["token"]}

    # Создаём тренировку
    create_response = client.post("/workouts", json={
        "name": "Flexibility Training",
        "description": "Yoga session",
        "duration_minutes": 60,
        "workout_type": WorkoutType.flexibility
    }, headers=headers)
    assert create_response.status_code == 201
    workout_id = create_response.json()["id"]

    # Получаем по ID
    response = client.get(f"/workouts/{workout_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert data["id"] == workout_id
    assert data["name"] == "Flexibility Training"
    assert data["workout_type"] == WorkoutType.flexibility


def test_update_workout(client: TestClient, registered_user):
    headers = {"Authorization": registered_user["token"]}

    # Создаём тренировку
    create_response = client.post("/workouts", json={
        "name": "Old Name",
        "description": "Old Description",
        "duration_minutes": 30,
        "workout_type": WorkoutType.cardio
    }, headers=headers)
    assert create_response.status_code == 201
    workout_id = create_response.json()["id"]

    # Обновляем
    updated_data = {
        "name": "Updated Workout",
        "description": "New description",
        "duration_minutes": 45,
        "workout_type": WorkoutType.strength
    }

    update_response = client.put(f"/workouts/{workout_id}", json=updated_data, headers=headers)
    assert update_response.status_code == 200
    data = update_response.json()

    assert data["name"] == updated_data["name"]
    assert data["description"] == updated_data["description"]
    assert data["duration_minutes"] == updated_data["duration_minutes"]
    assert data["workout_type"] == updated_data["workout_type"]


def test_delete_workout(client: TestClient, registered_user):
    headers = {"Authorization": registered_user["token"]}

    # Создаём тренировку
    create_response = client.post("/workouts", json={
        "name": "To Be Deleted",
        "description": "This will be deleted",
        "duration_minutes": 30,
        "workout_type": WorkoutType.strength
    }, headers=headers)
    assert create_response.status_code == 201
    workout_id = create_response.json()["id"]

    # Удаляем
    delete_response = client.delete(f"/workouts/{workout_id}", headers=headers)
    assert delete_response.status_code == 204

    # Проверяем, что не существует
    get_response = client.get(f"/workouts/{workout_id}", headers=headers)
    assert get_response.status_code == 404


def test_create_exercise_linked_to_workout(client: TestClient, registered_user):
    headers = {"Authorization": registered_user["token"]}

    # Сначала создаём тренировку
    workout_response = client.post("/workouts", json={
        "name": "Test Workout",
        "description": "For testing linked exercises",
        "duration_minutes": 60,
        "workout_type": WorkoutType.cardio.value
    }, headers=headers)
    assert workout_response.status_code == 201
    workout_id = workout_response.json()["id"]

    # Теперь создаём упражнение и сразу привязываем к тренировке
    exercise_payload = {
        "name": "Jumping Jacks",
        "description": "Warm-up cardio",
        "calories_per_minute": 10,
        "exercise_type": ExerciseType.cardio
    }

    link_response = client.post(f"/workouts/{workout_id}/exercises", json=exercise_payload, headers=headers)
    assert link_response.status_code == 201
    data = link_response.json()

    # Проверяем поля
    assert data["name"] == exercise_payload["name"]
    assert data["calories_per_minute"] == exercise_payload["calories_per_minute"]
    assert data["exercise_type"] == exercise_payload["exercise_type"]

    # Проверяем, что упражнение появилось в тренировке
    workout_details = client.get(f"/workouts/{workout_id}", headers=headers)
    assert len(workout_details.json()["exercises"]) >= 1
    assert any(e["name"] == "Jumping Jacks" for e in workout_details.json()["exercises"])
