import os
import sys

import faker
from fastapi.testclient import TestClient

from fixture import registered_user, client

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Импортируем из проекта
import schemas

fake = faker.Faker()


# === ТЕСТЫ НАЧИНАЮТСЯ ЗДЕСЬ ===

def test_create_user(client: TestClient, registered_user):
    payload = {
        "name": fake.last_name(),
        "email": fake.email(),
        "password": fake.password(),
        "experience_level": fake.enum(schemas.UserExperience),
        "goal": fake.enum(schemas.UserGoal)
    }

    response = client.post("/users", json=payload)

    assert response.status_code == 201, f"Expected status code 201, got {response.status_code}. Response: {response.json()}"
    data = response.json()

    # Проверяем обязательные поля
    assert data["name"] == payload["name"]
    assert data["email"] == payload["email"]
    assert data["experience_level"] == payload["experience_level"]
    assert data["goal"] == payload["goal"]

    # created_at должен быть строкой
    assert isinstance(data["created_at"], str)

    # ID должен быть целым числом
    assert isinstance(data["id"], int)

    # Пароль не должен возвращаться
    assert "password_hash" not in data


def test_get_users_list(client: TestClient, registered_user):
    headers = {"Authorization": f"Bearer {registered_user['token']}"}
    response = client.get("/users", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(u["email"] == registered_user["email"] for u in data)


def test_get_user_by_email(client: TestClient, registered_user):
    headers = {"Authorization": f"Bearer {registered_user['token']}"}
    response = client.get(f"/users/{registered_user['email']}", headers=headers)

    assert response.status_code == 200
    data = response.json()

    assert data["name"] == registered_user["name"]
    assert data["email"] == registered_user["email"]
    assert data["experience_level"] == registered_user["experience_level"]
    assert data["goal"] == registered_user["goal"]


def test_update_user(client: TestClient, registered_user):
    headers = {"Authorization": f"Bearer {registered_user['token']}"}

    updated_data = {
        "name": fake.last_name(),
        "email": fake.email(),
        "password": fake.password(),
        "experience_level": fake.enum(schemas.UserExperience),
        "goal": fake.enum(schemas.UserGoal)
    }

    response = client.put(f"/users/{registered_user['email']}", json=updated_data, headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert data["name"] == updated_data["name"]
    assert data["email"] == updated_data["email"]
    assert data["experience_level"] == updated_data["experience_level"]
    assert data["goal"] == updated_data["goal"]


def test_delete_user(client: TestClient, registered_user):
    headers = {"Authorization": f"Bearer {registered_user['token']}"}

    response = client.delete(f"/users/{registered_user['email']}", headers=headers)
    assert response.status_code == 204 or response.status_code == 200

    # Проверяем, что пользователь больше не существует
    response_after_delete = client.get(f"/users/{registered_user['email']}", headers=headers)
    assert response_after_delete.status_code == 404
