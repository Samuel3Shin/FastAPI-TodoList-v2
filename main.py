from fastapi import FastAPI
from app import api, models
from app.database import engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(api.router)