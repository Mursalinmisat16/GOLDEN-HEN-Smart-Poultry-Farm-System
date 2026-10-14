from fastapi import FastAPI
from sqlmodel import SQLModel
from fastapi.middleware.cors import CORSMiddleware

from database import get_db, engine
from routers import admin, sensor_data, predict, user
import models
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)
    
    
app.include_router(admin.route)
app.include_router(sensor_data.route)
app.include_router(predict.route)
app.include_router(user.route)
