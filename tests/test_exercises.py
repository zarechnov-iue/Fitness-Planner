from fastapi.testclient import TestClient

from fixture import registered_user, client


def test_create_exercise(client: TestClient, registered_user):
    headers = {"Authorization": f"Bearer {registered_user['token']}"}
    payload = {
        "name": "Push-ups",
        "description": "Upper body strength training",
        "calories_per_minute": 8,
        "exercise_type": "strength"
    }

    response = client.post("/exercises", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()

    assert data["name"] == payload["name"]
    assert data["description"] == payload["description"]
    assert data["calories_per_minute"] == payload["calories_per_minute"]
    assert data["exercise_type"] == payload["exercise_type"]
    assert "id" in data
    assert "created_at" in data


def test_get_exercises_list(client: TestClient, registered_user):
    headers = {"Authorization": f"Bearer {registered_user['token']}"}
    response = client.get("/exercises", headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_exercise_by_id(client: TestClient, registered_user):
    headers = {"Authorization": f"Bearer {registered_user['token']}"}

    # Сначала создаём упражнение
    create_response = client.post("/exercises", json={
        "name": "Running",
        "description": "Cardio exercise for weight loss",
        "calories_per_minute": 10,
        "exercise_type": "cardio"
    }, headers=headers)
    assert create_response.status_code == 201
    exercise_id = create_response.json()["id"]

    # Теперь получаем его по ID
    response = client.get(f"/exercises/{exercise_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert data["id"] == exercise_id
    assert data["name"] == "Running"


def test_update_exercise(client: TestClient, registered_user):
    headers = {"Authorization": f"Bearer {registered_user['token']}"}

    # Создаём упражнение
    create_response = client.post("/exercises", json={
        "name": "Pull-ups",
        "description": "Back and arm workout",
        "calories_per_minute": 9,
        "exercise_type": "strength"
    }, headers=headers)
    assert create_response.status_code == 201
    exercise_id = create_response.json()["id"]

    # Обновляем
    updated_data = {
        "name": "Updated Pull-ups",
        "description": "Improved back workout",
        "calories_per_minute": 10,
        "exercise_type": "strength"
    }

    response = client.put(f"/exercises/{exercise_id}", json=updated_data, headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert data["name"] == updated_data["name"]
    assert data["description"] == updated_data["description"]
    assert data["calories_per_minute"] == updated_data["calories_per_minute"]
    assert data["exercise_type"] == updated_data["exercise_type"]


def test_delete_exercise(client: TestClient, registered_user):
    headers = {"Authorization": f"Bearer {registered_user['token']}"}

    # Создаём упражнение
    create_response = client.post("/exercises", json={
        "name": "Jumping Jacks",
        "description": "Warm-up cardio",
        "calories_per_minute": 6,
        "exercise_type": "cardio"
    }, headers=headers)
    assert create_response.status_code == 201
    exercise_id = create_response.json()["id"]

    # Удаляем
    delete_response = client.delete(f"/exercises/{exercise_id}", headers=headers)
    assert delete_response.status_code == 204

    # Проверяем, что больше не существует
    get_response = client.get(f"/exercises/{exercise_id}", headers=headers)
    assert get_response.status_code == 404
