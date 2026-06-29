from pydantic import BaseModel


class AuthDTO(BaseModel):
    username: str
    password: str


class RegisterDTO(BaseModel):
    username: str
    password: str
    nickname: str | None = None
    email: str | None = None


class LoginResponse(BaseModel):
    token: str
    user_id: int
    username: str
    nickname: str | None = None
    email: str | None = None
