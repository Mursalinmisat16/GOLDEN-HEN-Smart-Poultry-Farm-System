from pydantic import BaseModel, EmailStr


class New_User(BaseModel):
    email: EmailStr
    password: str