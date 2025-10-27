from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from src.db.postgres import get_db
from src.schemas.student import StudentCreate, StudentUpdate, StudentResponse
from src.schemas.course import CourseResponse
from src.services.student_service import StudentService

router = APIRouter(prefix="/students", tags=["students"])


@router.post("/", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(
    student_data: StudentCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new student
    
    - **name**: Student's full name (required)
    - **email**: Student's email address (required, must be unique)
    """
    return StudentService.create_student(db, student_data)


@router.get("/{student_id}", response_model=StudentResponse)
def get_student(
    student_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a student by ID
    
    - **student_id**: ID of the student to retrieve
    """
    return StudentService.get_student(db, student_id)


@router.get("/", response_model=List[StudentResponse])
def get_all_students(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all students with pagination
    
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100)
    """
    return StudentService.get_all_students(db, skip, limit)


@router.put("/{student_id}", response_model=StudentResponse)
def update_student(
    student_id: int,
    student_data: StudentUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a student's information
    
    - **student_id**: ID of the student to update
    - **name**: Updated name (optional)
    - **email**: Updated email (optional)
    """
    return StudentService.update_student(db, student_id, student_data)


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(
    student_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a student
    
    - **student_id**: ID of the student to delete
    """
    StudentService.delete_student(db, student_id)
    return None


@router.get("/{student_id}/courses", response_model=List[CourseResponse])
def get_student_courses(
    student_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all courses a student is enrolled in
    
    - **student_id**: ID of the student
    """
    return StudentService.get_student_courses(db, student_id)

