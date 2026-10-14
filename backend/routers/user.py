from fastapi import APIRouter, Depends
from sqlmodel import select
from email.message import EmailMessage
import smtplib
import random

from models import User, Otp
from schemas import New_User, User_Activation
from database import get_db

route = APIRouter(tags=['User Login'], prefix = '/login')

@route.post('/')
def user_login(userReq: New_User, db = Depends(get_db)):
    result = db.exec(select(User).where(User.email == userReq.email)).first()

    if result:
        if result.password == userReq.password and result.activated == True:
            return result.id
        elif result.activated == False:
            return 'not_activated'
        else:
            return 'incorrect'
        
    else:
        return 'incorrect'
    

@route.get('/send_otp/{email}')
def send_email(email, db = Depends(get_db)):
    genarated_otp = get_otp()

    send_otp(genarated_otp, email)

    new_otp = Otp(otp = genarated_otp, email = email)
    db.add(new_otp)
    db.commit()
    db.refresh(new_otp)
    return {"sent"}


@route.post('/active')
def active_email(reqbody: User_Activation, db = Depends(get_db)):

    result_set = db.query(Otp).filter(Otp.email == reqbody.email).first()

    if result_set.otp == reqbody.otp:
        user = db.exec(select(User).where(User.email == reqbody.pre_email)).first()
        user.email = reqbody.email
        user.password = reqbody.password
        user.activated = True
        db.add(user)
        db.commit()


        return {"active"}
    else:
        return {"detail" : "Wrong"}













def get_otp():
    otp = ""
    for i in range(6):
        otp += str(random.randint(0,9))
    return otp


def send_otp(otp, mail):
    from_mail = "mursalinhossainmisat.robo@gmail.com"
    password = "yhtj njbg xlaf ewjf"
    to_mail = mail

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(from_mail, password)


    message = EmailMessage()
    message["Subject"] = "OTP Verification"
    message["From"] = from_mail
    message["To"] = to_mail
    message.set_content("Your OTP is: " + otp + "\nThank You From Team GolTable")

    server.send_message(message)
    return "Ok"