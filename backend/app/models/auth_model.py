"""
Pydantic models for authentication endpoints
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime


class UserRegister(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)
    username: Optional[str] = Field(None, min_length=3, max_length=100)

    @validator('password')
    def password_strength(cls, v):
        """
        Validate password strength

        Requirements:
        - At least 10 characters (increased from 8 for better security)
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - No common weak passwords
        """
        if len(v) < 10:
            raise ValueError('Password must be at least 10 characters long')

        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')

        if not any(char.islower() for char in v):
            raise ValueError('Password must contain at least one lowercase letter')

        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')

        # Check for common weak passwords
        common_passwords = [
            'password', '123456789', 'qwerty123', 'abc123456',
            '1234567890', 'password123', 'admin123', 'welcome123'
        ]
        if v.lower() in common_passwords:
            raise ValueError('Password is too common. Please choose a stronger password')

        return v


class UserLogin(BaseModel):
    """User login request"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data"""
    user_id: Optional[int] = None
    email: Optional[str] = None


class UserResponse(BaseModel):
    """User data response"""
    id: int
    email: str
    username: Optional[str]
    full_name: Optional[str]
    avatar_url: Optional[str]
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """User profile update request"""
    full_name: Optional[str] = Field(None, max_length=255)
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    avatar_url: Optional[str] = None


class PasswordChange(BaseModel):
    """Password change request"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)

    @validator('new_password')
    def password_strength(cls, v):
        """
        Validate password strength

        Requirements:
        - At least 10 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - No common weak passwords
        """
        if len(v) < 10:
            raise ValueError('Password must be at least 10 characters long')

        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')

        if not any(char.islower() for char in v):
            raise ValueError('Password must contain at least one lowercase letter')

        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')

        # Check for common weak passwords
        common_passwords = [
            'password', '123456789', 'qwerty123', 'abc123456',
            '1234567890', 'password123', 'admin123', 'welcome123'
        ]
        if v.lower() in common_passwords:
            raise ValueError('Password is too common. Please choose a stronger password')

        return v


class PasswordResetRequest(BaseModel):
    """Password reset request"""
    email: EmailStr


class PasswordReset(BaseModel):
    """Password reset with token"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)


class EmailVerification(BaseModel):
    """Email verification token"""
    token: str
