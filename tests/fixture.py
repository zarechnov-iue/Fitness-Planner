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
from core.database import get_db, Base
from schemas.users import UserExperience, UserGoal
from core.config import SQLALCHEMY_TEST_DATABASE_URL

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False}
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
        "experience_level": fake.enum(UserExperience),
        "goal": fake.enum(UserGoal)
    }

    response = client.post("auth/signup", json=payload)
    assert response.status_code == 201

    payload["token"] = response.headers["authorization"]
    return payload
