from pydantic import BaseModel, EmailStr
from uuid import UUID
from typing import Optional
from ..models.user import Roles
from datetime import datetime

# Schema for creating a user
class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: Roles
    location: Optional[str] = None

# Signup with OTP Schemas
class SignupOTPRequest(BaseModel):
    email: EmailStr

class SignupVerifyOTP(BaseModel):
    email: EmailStr
    otp: str
    full_name: str
    password: str
    role: Roles
    location: Optional[str] = None

# Schema for reading user data (response)
class UserRead(BaseModel):
    id: UUID
    full_name: str
    email: EmailStr
    role: Roles
    location: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True  # allows reading SQLAlchemy models directly

# Schema for updating user
class UserUpdate(BaseModel):
    full_name: Optional[str]
    location: Optional[str]

class UserLogin(BaseModel):
    email: str
    password: str

# Password Reset Schemas
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str
    new_password: str