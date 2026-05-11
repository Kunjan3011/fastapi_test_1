from fastapi import FastAPI

from app.database import Base, engine
from app.routers import auth, users, admin, tasks

app = FastAPI()

Base.metadata.create_all(bind=engine)


@app.get("/")
def welcome_page():
    return {"message": "Welcome to Task Management System!"}


app.include_router(auth.router)

app.include_router(users.router)

app.include_router(admin.router)

app.include_router(tasks.router)
