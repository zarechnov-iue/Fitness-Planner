import os
import sys

import faker
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Импортируем из проекта
from main import app
from models import Base
from database import get_db
import schemas

# Используем in-memory SQLite для тестов
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

fake = faker.Faker()


# Создаём таблицы перед тестами
@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Подменяем зависимость get_db
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield
    Base.metadata.drop_all(bind=engine)


# Фикстура клиента
@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def registered_user(client):
    payload = {
        "name": fake.last_name(),
        "email": fake.email(),
        "password": fake.password(),
        "experience_level": fake.enum(schemas.UserExperience),
        "goal": fake.enum(schemas.UserGoal)
    }

    response = client.post("/users", json=payload)
    assert response.status_code == 201

    # Добавляем токен в payload для удобства
    # token = response.json()["access_token"]
    payload["token"] = "token"
    return payload


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
