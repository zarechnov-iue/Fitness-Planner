from fastapi import FastAPI

from routes.exercises import router as exercises_router
from routes.users import router as users_router

app = FastAPI()

app.include_router(users_router)
app.include_router(exercises_router)


@app.on_event("startup")
def startup_event():
    from database import Base, engine
    Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
    return {"message": "Welcome to Fitness Planner API"}
