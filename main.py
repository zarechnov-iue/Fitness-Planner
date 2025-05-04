from fastapi import FastAPI

from routes.auth import router as auth_router
from routes.users import router as users_router
from routes.workouts import router as workouts_router

app = FastAPI()

app.include_router(users_router)
app.include_router(workouts_router)
app.include_router(auth_router)


@app.on_event("startup")
def startup_event():
    from core.database import Base, engine
    Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
    return {"message": "Welcome to Fitness Planner API"}
