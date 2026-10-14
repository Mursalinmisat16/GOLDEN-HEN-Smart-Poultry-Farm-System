from sqlmodel import Field, Session, SQLModel, create_engine, select
from pydantic import EmailStr
from datetime import datetime


class User(SQLModel, table=True):
    __tabelname__ = 'users'
    
    id: int | None = Field(default=None, primary_key=True)
    email: EmailStr = Field(index=True)
    password: str
    
    
class Sensor_Data(SQLModel, table = True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int
    temperature: float
    humidity: float
    rain: float
    soil_moisture: float
    pH: float
    N: float
    P: float
    K: float
    time: datetime