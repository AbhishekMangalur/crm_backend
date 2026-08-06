from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginUserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    dashboard_path: str
    user: LoginUserResponse


class CurrentUserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str
    dashboard_path: str