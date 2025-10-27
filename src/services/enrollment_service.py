from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import List

from src.models.enrollment import Enrollment
from src.schemas.enrollment import EnrollmentCreate
from src.services.student_service import StudentService
from src.services.course_service import CourseService


class EnrollmentService:
    """Service layer for enrollment-related business logic"""

    @staticmethod
    def create_enrollment(db: Session, enrollment_data: EnrollmentCreate) -> Enrollment:
        """
        Create a new enrollment (enroll a student in a course)
        
        Args:
            db: Database session
            enrollment_data: Enrollment creation data
            
        Returns:
            Created enrollment object
            
        Raises:
            HTTPException: If student or course not found, or enrollment already exists
        """
        # Verify student exists
        StudentService.get_student(db, enrollment_data.student_id)
        
        # Verify course exists
        CourseService.get_course(db, enrollment_data.course_id)
        
        try:
            enrollment = Enrollment(
                student_id=enrollment_data.student_id,
                course_id=enrollment_data.course_id
            )
            db.add(enrollment)
            db.commit()
            db.refresh(enrollment)
            return enrollment
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Student {enrollment_data.student_id} is already enrolled in course {enrollment_data.course_id}"
            )

    @staticmethod
    def get_enrollment(db: Session, enrollment_id: int) -> Enrollment:
        """
        Get an enrollment by ID
        
        Args:
            db: Database session
            enrollment_id: Enrollment ID
            
        Returns:
            Enrollment object
            
        Raises:
            HTTPException: If enrollment not found
        """
        enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Enrollment with id {enrollment_id} not found"
            )
        return enrollment

    @staticmethod
    def get_all_enrollments(db: Session, skip: int = 0, limit: int = 100) -> List[Enrollment]:
        """
        Get all enrollments with pagination
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of enrollments
        """
        return db.query(Enrollment).offset(skip).limit(limit).all()

    @staticmethod
    def delete_enrollment(db: Session, enrollment_id: int) -> None:
        """
        Delete an enrollment (unenroll a student from a course)
        
        Args:
            db: Database session
            enrollment_id: Enrollment ID
            
        Raises:
            HTTPException: If enrollment not found
        """
        enrollment = EnrollmentService.get_enrollment(db, enrollment_id)
        db.delete(enrollment)
        db.commit()

    @staticmethod
    def delete_enrollment_by_student_and_course(db: Session, student_id: int, course_id: int) -> None:
        """
        Delete an enrollment by student and course IDs
        
        Args:
            db: Database session
            student_id: Student ID
            course_id: Course ID
            
        Raises:
            HTTPException: If enrollment not found
        """
        enrollment = db.query(Enrollment).filter(
            Enrollment.student_id == student_id,
            Enrollment.course_id == course_id
        ).first()
        
        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Enrollment not found for student {student_id} and course {course_id}"
            )
        
        db.delete(enrollment)
        db.commit()

