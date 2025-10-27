from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from src.db.postgres import get_db
from src.schemas.enrollment import EnrollmentCreate, EnrollmentResponse, EnrollmentWithDetails
from src.services.enrollment_service import EnrollmentService

router = APIRouter(prefix="/enrollments", tags=["enrollments"])


@router.post("/", response_model=EnrollmentResponse, status_code=status.HTTP_201_CREATED)
def create_enrollment(
    enrollment_data: EnrollmentCreate,
    db: Session = Depends(get_db)
):
    """
    Enroll a student in a course
    
    - **student_id**: ID of the student to enroll (required)
    - **course_id**: ID of the course to enroll in (required)
    """
    return EnrollmentService.create_enrollment(db, enrollment_data)


@router.get("/{enrollment_id}", response_model=EnrollmentWithDetails)
def get_enrollment(
    enrollment_id: int,
    db: Session = Depends(get_db)
):
    """
    Get an enrollment by ID with student and course details
    
    - **enrollment_id**: ID of the enrollment to retrieve
    """
    return EnrollmentService.get_enrollment(db, enrollment_id)


@router.get("/", response_model=List[EnrollmentWithDetails])
def get_all_enrollments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all enrollments with pagination
    
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100)
    """
    return EnrollmentService.get_all_enrollments(db, skip, limit)


@router.delete("/{enrollment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_enrollment(
    enrollment_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete an enrollment (unenroll a student from a course)
    
    - **enrollment_id**: ID of the enrollment to delete
    """
    EnrollmentService.delete_enrollment(db, enrollment_id)
    return None


@router.delete("/student/{student_id}/course/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_enrollment_by_student_and_course(
    student_id: int,
    course_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete an enrollment by student and course IDs
    
    - **student_id**: ID of the student
    - **course_id**: ID of the course
    """
    EnrollmentService.delete_enrollment_by_student_and_course(db, student_id, course_id)
    return None

