from pydantic import BaseModel, Field
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from src.schemas.student import StudentResponse


class CourseBase(BaseModel):
    """Base schema for Course with common attributes"""
    name: str = Field(..., min_length=1, max_length=200, description="Course name")
    description: Optional[str] = Field(None, description="Course description")
    instructor: str = Field(..., min_length=1, max_length=100, description="Instructor name")


class CourseCreate(CourseBase):
    """Schema for creating a new course"""
    pass


class CourseUpdate(BaseModel):
    """Schema for updating a course (all fields optional)"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    instructor: Optional[str] = Field(None, min_length=1, max_length=100)


class CourseResponse(CourseBase):
    """Schema for course response"""
    id: int

    model_config = {"from_attributes": True}


class CourseWithStudents(CourseResponse):
    """Schema for course response with enrolled students"""
    students: List["StudentResponse"] = []

    model_config = {"from_attributes": True}

