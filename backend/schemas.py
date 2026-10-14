from pydantic import BaseModel, EmailStr


class New_User(BaseModel):
    email: EmailStr
    password: str


class User_Activation(BaseModel):
    pre_email: EmailStr
    email: EmailStr
    password: str
    otp: str