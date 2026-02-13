from pydantic import BaseModel

class Register(BaseModel):
    email: str
    username: str
    password: str

class Login(BaseModel):
    email: str
    password: str

class SendOTPSchema(BaseModel):
    email: str

class VerifyOTPSchema(BaseModel):
    email: str
    code: str

class FinalResetPassword(BaseModel):
    reset_token: str
    new_password: str

