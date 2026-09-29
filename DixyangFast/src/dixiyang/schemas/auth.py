from pydantic import BaseModel


class AuthDTO(BaseModel):
    username: str
    password: str


class RegisterDTO(BaseModel):
    username: str
    password: str
    nickname: str | None = None
    email: str | None = None
    code: str | None = None  # 验证码


class LoginByCodeDTO(BaseModel):
    email: str
    code: str


class SendCodeDTO(BaseModel):
    email: str
    purpose: str = "LOGIN"  # LOGIN / REGISTER / CHG_EMAIL（更换邮箱）


class LoginResponse(BaseModel):
    token: str
    user_id: int
    username: str
    nickname: str | None = None
    email: str | None = None
