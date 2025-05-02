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
        "name": fake.first_name() + " " + fake.last_name(),
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
