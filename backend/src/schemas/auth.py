from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class LoginRequest(BaseModel):
    """
    Schema for login requests.

    Attributes:
        email: User's email address
        password: User's password
        role: User role (admin or student)
    """
    email: EmailStr
    password: str = Field(..., min_length=1)
    # Allow any string here; invalid roles will be handled in service with 400
    role: str = Field(..., min_length=1)


class StudentSignupRequest(BaseModel):
    """
    Schema for student signup requests.

    Attributes:
        name: Student's full name
        email: Student's email address
        password: Password for authentication
    """
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)


class TokenResponse(BaseModel):
    """
    Schema for authentication token responses.

    Attributes:
        access_token: JWT access token
        token_type: Type of token (usually "bearer")
        user: User information
    """
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserResponse(BaseModel):
    """
    Schema for user information in responses.

    Attributes:
        id: User ID
        name: User's full name
        email: User's email address
        role: User role (admin or student)
    """
    id: int
    name: str
    email: str
    role: str
