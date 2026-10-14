from fastapi import APIRouter, Depends
from sqlmodel import select

from models import User
from schemas import New_User
from database import get_db

route = APIRouter(tags=['User Login'], prefix = '/login')

@route.post('/')
def user_login(userReq: New_User, db = Depends(get_db)):
    result = db.exec(select(User).where(User.email == userReq.email)).first()

    if result:
        if result.password == userReq.password:
            return result.id
        else:
            return 'incorrect'
        
    else:
        return 'incorrect'