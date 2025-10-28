from src.schemas.student import StudentCreate, StudentUpdate, StudentResponse, StudentWithCourses
from src.schemas.course import CourseCreate, CourseUpdate, CourseResponse, CourseWithStudents
from src.schemas.enrollment import EnrollmentCreate, EnrollmentResponse, EnrollmentWithDetails
from src.schemas.auth import LoginRequest, StudentSignupRequest, TokenResponse, UserResponse

# Rebuild models to resolve forward references
StudentWithCourses.model_rebuild()
CourseWithStudents.model_rebuild()

__all__ = [
    "StudentCreate",
    "StudentUpdate",
    "StudentResponse",
    "StudentWithCourses",
    "CourseCreate",
    "CourseUpdate",
    "CourseResponse",
    "CourseWithStudents",
    "EnrollmentCreate",
    "EnrollmentResponse",
    "EnrollmentWithDetails",
    "LoginRequest",
    "StudentSignupRequest",
    "TokenResponse",
    "UserResponse",
]

