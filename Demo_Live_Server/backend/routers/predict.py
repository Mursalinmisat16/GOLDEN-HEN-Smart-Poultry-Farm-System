from fastapi import APIRouter, Depends
from sqlmodel import select
import pandas as pd
import joblib
from models import Sensor_Data
from database import get_db

route = APIRouter(tags=['Machine Learning'], prefix = '/predict')


model = joblib.load('model.pkl')
@route.get('/{id}')
def crop_predictions(id, db = Depends(get_db)):
    latest_values = db.exec(select(Sensor_Data).where(Sensor_Data.user_id == id).order_by(Sensor_Data.time.desc())).first()
    
    data = {
        'N': [latest_values.N],
        'P': [latest_values.P],
        'K': [latest_values.K],
        'temperature': [latest_values.temperature],
        'humidity': [latest_values.humidity],
        'ph': [latest_values.pH],
        'rainfall': [latest_values.rain]
    }
    
    df = pd.DataFrame(data)
    prediction = model.predict(df)
    
    return {'predicted_crop': prediction[0]}