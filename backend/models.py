# from sqlmodel import Field, Session, SQLModel, create_engine, select
# from pydantic import EmailStr
# from datetime import datetime


# class User(SQLModel, table=True):
#     __tabelname__ = 'users'
    
#     id: int | None = Field(default=None, primary_key=True)
#     email: EmailStr = Field(index=True)
#     password: str
#     activated: bool | None = Field(default = False)
    
    
# class Sensor_Data(SQLModel, table = True):
#     id: int | None = Field(default=None, primary_key=True)
#     user_id: int
#     temperature: float
#     humidity: float
#     food_level: float
#     water_level: float
#     water_pump_status: float
#     fan_status: float
#     fire_status: float
#     gas_status: float
#     food_time_status: str
#     time: datetime


# class Otp(SQLModel, table = True):
#     __tablename__ = "otps"
    
#     id: int | None = Field(primary_key=True, default=None)
#     otp: str
#     email : str





from typing import Optional
from datetime import datetime

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: EmailStr = Field(index=True)
    password: str
    activated: bool = Field(default=False)


class Sensor_Data(SQLModel, table=True):
    __tablename__ = "sensor_data"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int

    # Core readings
    temperature: float
    humidity: float
    food_level: float
    water_level: float

    # Actuators / status (use 0/1)
    water_pump_status: int
    fan_status: int                         # REAL fan status

    fire_status: int
    gas_status: int                         # boolean-ish flag

    # Legacy (kept for compatibility)
    food_time_status: Optional[int] = None

    # NEW fields so the UI can show last/next feed/water & air quality
    feeding_food_status: Optional[int] = None   # 0/1 while dispensing food
    feeding_water_status: Optional[int] = None  # 0/1 while dispensing water
    next_food_eta_ms: Optional[int] = None      # ms until next food dispense
    next_water_eta_ms: Optional[int] = None     # ms until next water dispense
    gas_ppm: Optional[float] = None             # air quality (e.g., NH₃ proxy)

    time: datetime = Field(default_factory=datetime.utcnow)


class Otp(SQLModel, table=True):
    __tablename__ = "otps"

    id: Optional[int] = Field(primary_key=True, default=None)
    otp: str
    email: str
