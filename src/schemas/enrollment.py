from pydantic import BaseModel, Field
from typing import Optional
from src.schemas.student import StudentResponse
from src.schemas.course import CourseResponse


class EnrollmentBase(BaseModel):
    """Base schema for Enrollment with common attributes"""
    student_id: int = Field(..., gt=0, description="Student ID")
    course_id: int = Field(..., gt=0, description="Course ID")


class EnrollmentCreate(EnrollmentBase):
    """Schema for creating a new enrollment"""
    pass


class EnrollmentResponse(EnrollmentBase):
    """Schema for enrollment response"""
    id: int

    model_config = {"from_attributes": True}


class EnrollmentWithDetails(BaseModel):
    """Schema for enrollment response with student and course details"""
    id: int
    student: StudentResponse
    course: CourseResponse

    model_config = {"from_attributes": True}

