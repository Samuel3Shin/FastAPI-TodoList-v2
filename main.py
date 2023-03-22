from fastapi import FastAPI
from app import models
from app.database import engine
from app.routers import users, tasks

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])