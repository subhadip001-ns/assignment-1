from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from src.db.postgres import get_db
from src.schemas.course import CourseCreate, CourseUpdate, CourseResponse
from src.schemas.student import StudentResponse
from src.services.course_service import CourseService

router = APIRouter(prefix="/courses", tags=["courses"])


@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(
    course_data: CourseCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new course
    
    - **name**: Course name (required)
    - **description**: Course description (optional)
    - **instructor**: Instructor name (required)
    """
    return CourseService.create_course(db, course_data)


@router.get("/{course_id}", response_model=CourseResponse)
def get_course(
    course_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a course by ID
    
    - **course_id**: ID of the course to retrieve
    """
    return CourseService.get_course(db, course_id)


@router.get("/", response_model=List[CourseResponse])
def get_all_courses(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all courses with pagination
    
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100)
    """
    return CourseService.get_all_courses(db, skip, limit)


@router.put("/{course_id}", response_model=CourseResponse)
def update_course(
    course_id: int,
    course_data: CourseUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a course's information
    
    - **course_id**: ID of the course to update
    - **name**: Updated course name (optional)
    - **description**: Updated description (optional)
    - **instructor**: Updated instructor name (optional)
    """
    return CourseService.update_course(db, course_id, course_data)


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(
    course_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a course
    
    - **course_id**: ID of the course to delete
    """
    CourseService.delete_course(db, course_id)
    return None


@router.get("/{course_id}/students", response_model=List[StudentResponse])
def get_course_students(
    course_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all students enrolled in a course
    
    - **course_id**: ID of the course
    """
    return CourseService.get_course_students(db, course_id)

