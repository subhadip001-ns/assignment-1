from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from src.schemas.course import CourseResponse


class StudentBase(BaseModel):
    """Base schema for Student with common attributes"""
    name: str = Field(..., min_length=1, max_length=100, description="Student's full name")
    email: EmailStr = Field(..., description="Student's email address")


class StudentCreate(StudentBase):
    """Schema for creating a new student"""
    pass


class StudentUpdate(BaseModel):
    """Schema for updating a student (all fields optional)"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None


class StudentResponse(StudentBase):
    """Schema for student response"""
    id: int

    model_config = {"from_attributes": True}


class StudentWithCourses(StudentResponse):
    """Schema for student response with enrolled courses"""
    courses: List["CourseResponse"] = []

    model_config = {"from_attributes": True}

