# Fitness Planner

Fitness Planner — это REST-сервис на FastAPI, который помогает пользователям планировать тренировки и добавлять
упражнения.

Установка зависимостей

```shell
pip install -r requirements.txt
```

Запуск сервера

```shell
uvicorn main:app --reload
```

Запуск тестов

```shell
pytest .\tests -v -W ignore
```

Документация [swagger](http://127.0.0.1:8000/docs#/)

## Ендпойнты

### Аутентификация

- `POST /auth/signup` — регистрация нового пользователя
- `POST /auth/login` — вход и получение JWT-токена

> JWT токен нужно передавать в заголовке:
>
> `Authorization: Bearer <your_token_here>`

### Пользователи

- `GET /users` — получить список пользователей (только авторизованный)
- `GET /users/me` — получить свой профиль
- `GET /users/{id}` — получить пользователя по ID
- `PUT /users/{id}` — обновить профиль
- `DELETE /users/{id}` — удалить пользователя

### Тренировки

`POST /workouts` — создать новую тренировку
`GET /workouts` — получить список своих тренировок
`GET /workouts/{id}` — получить детали тренировки (включая упражнения)
`PUT /workouts/{id}` — обновить тренировку
`DELETE /workouts/{id}` — удалить тренировку

### Упражнения

Все упражнения связаны с тренировками

- `POST /workouts/{workout_id}/exercises` — создать новое упражнение и добавить его в тренировку
- `GET /workouts/{workout_id}/exercises` — получить все упражнения тренировки
- `GET /workouts/{workout_id}/exercises/{exercise_id}` — получить конкретное упражнение из тренировки
- `PUT /workouts/{workout_id}/exercises/{exercise_id}` — обновить упражнение
- `DELETE /workouts/{workout_id}/exercises/{exercise_id}` — удалить упражнение из тренировки

## База данных

### `users`

| Поле             | Тип             | Описание                            |
|------------------|-----------------|-------------------------------------|
| id               | Integer         | Уникальный ID                       |
| name             | String          | Имя пользователя                    |
| email            | String (unique) | Email                               |
| password_hash    | String          | Хэшированный пароль                 |
| experience_level | Enum            | beginner, intermediate, advanced    |
| goal             | Enum            | weight_loss, muscle_gain, endurance |
| created_at       | DateTime        | Время регистрации                   |

### `exercises`

| Поле                | Тип      | Описание                      |
|---------------------|----------|-------------------------------|
| id                  | Integer  | Уникальный ID                 |
| name                | String   | Название упражнения           |
| description         | String   | Описание                      |
| calories_per_minute | Integer  | Калории за минуту             |
| exercise_type       | Enum     | cardio, strength, flexibility |
| created_at          | DateTime | Время создания                |

### `workouts`

| Поле             | Тип      | Описание                      |
|------------------|----------|-------------------------------|
| id               | Integer  | Уникальный ID                 |
| name             | String   | Название тренировки           |
| description      | String   | Описание тренировки           |
| duration_minutes | Integer  | Длительность тренировки       |
| workout_type     | Enum     | strength, cardio, flexibility |
| user_id          | Integer  | Ссылка на пользователя        |
| created_at       | DateTime | Время создания                |

### `workout_exercises` (many-to-many)

| Поле        | Тип     | Описание             |
|-------------|---------|----------------------|
| workout_id  | Integer | Ссылка на тренировку |
| exercise_id | Integer | Ссылка на упражнение |
