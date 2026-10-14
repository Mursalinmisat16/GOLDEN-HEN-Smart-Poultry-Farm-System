from fastapi import APIRouter, Depends

from schemas import New_User
from models import User
from database import get_db

route = APIRouter(tags=['Admin Panel'], prefix = '/admin')

@route.post('/newuser')
def create_new_user(user_info: New_User, db = Depends(get_db)):
    new_user = User.model_validate(user_info)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user.id
    