from fastapi import APIRouter, Depends
from datetime import datetime
from sqlmodel import select

from models import Sensor_Data
from database import get_db


route = APIRouter(tags=['Sensor Data API'], prefix = '/data')

@route.get('/{id}')
def write_sensor_data(id, t, h, fl, wl, wps, fs, fires, gs, fts, db = Depends(get_db)):
    time = datetime.now()
    new_sensor_data = Sensor_Data(
        user_id=id,
        temperature=t,
        humidity=h,
        food_level=fl,
        water_level=wl,
        water_pump_status=wps,
        fan_status=fs,
        fire_status=fires,
        gas_status=gs,
        food_time_status=fts,
        time=time
    )
    
    db.add(new_sensor_data)
    db.commit()
    db.refresh(new_sensor_data)
    return new_sensor_data.id


@route.get('/read/{id}')
def read_sensor_data(id, db = Depends(get_db)):
    data = db.exec(select(Sensor_Data).where(Sensor_Data.user_id == id).order_by(Sensor_Data.time.desc()).limit(10)).all()
    return data





