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
    def _validate_positive_id(value: int, field_name: str) -> None:
        """
        Validate that an ID is a positive integer
        
        Args:
            value: The ID value to validate
            field_name: Name of the field for error message
            
        Raises:
            HTTPException: If ID is not positive
        """
        if value <= 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"{field_name} must be a positive integer, got {value}"
            )

    @staticmethod
    def _validate_pagination(skip: int, limit: int) -> None:
        """
        Validate pagination parameters
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Raises:
            HTTPException: If pagination parameters are invalid
        """
        if skip < 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Skip parameter must be non-negative, got {skip}"
            )
        if limit <= 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Limit parameter must be positive, got {limit}"
            )
        if limit > 1000:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Limit parameter cannot exceed 1000, got {limit}"
            )

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
            HTTPException: If student or course not found, invalid IDs, or enrollment already exists
        """
        # Validate IDs are positive integers
        EnrollmentService._validate_positive_id(enrollment_data.student_id, "Student ID")
        EnrollmentService._validate_positive_id(enrollment_data.course_id, "Course ID")
        
        # Check if enrollment already exists (explicit check before attempting to create)
        existing_enrollment = db.query(Enrollment).filter(
            Enrollment.student_id == enrollment_data.student_id,
            Enrollment.course_id == enrollment_data.course_id
        ).first()
        
        if existing_enrollment:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Student with ID {enrollment_data.student_id} is already enrolled in course with ID {enrollment_data.course_id}"
            )
        
        # Verify student exists (will raise 404 if not found)
        student = StudentService.get_student(db, enrollment_data.student_id)
        
        # Verify course exists (will raise 404 if not found)
        course = CourseService.get_course(db, enrollment_data.course_id)
        
        try:
            enrollment = Enrollment(
                student_id=enrollment_data.student_id,
                course_id=enrollment_data.course_id
            )
            db.add(enrollment)
            db.commit()
            db.refresh(enrollment)
            return enrollment
        except IntegrityError as e:
            db.rollback()
            # This should not happen due to our explicit check above, but handle it just in case
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Failed to create enrollment due to database constraint violation"
            )
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An unexpected error occurred while creating enrollment: {str(e)}"
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
            HTTPException: If enrollment not found or invalid ID
        """
        # Validate enrollment ID
        EnrollmentService._validate_positive_id(enrollment_id, "Enrollment ID")
        
        enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Enrollment with ID {enrollment_id} not found"
            )
        return enrollment

    @staticmethod
    def get_all_enrollments(db: Session, skip: int = 0, limit: int = 100) -> List[Enrollment]:
        """
        Get all enrollments with pagination
        
        Args:
            db: Database session
            skip: Number of records to skip (default: 0)
            limit: Maximum number of records to return (default: 100, max: 1000)
            
        Returns:
            List of enrollments
            
        Raises:
            HTTPException: If pagination parameters are invalid
        """
        # Validate pagination parameters
        EnrollmentService._validate_pagination(skip, limit)
        
        return db.query(Enrollment).offset(skip).limit(limit).all()

    @staticmethod
    def delete_enrollment(db: Session, enrollment_id: int) -> None:
        """
        Delete an enrollment (unenroll a student from a course)
        
        Args:
            db: Database session
            enrollment_id: Enrollment ID
            
        Raises:
            HTTPException: If enrollment not found, invalid ID, or deletion fails
        """
        # Validate enrollment ID (also done in get_enrollment, but explicit here)
        EnrollmentService._validate_positive_id(enrollment_id, "Enrollment ID")
        
        # Get enrollment (will raise 404 if not found)
        enrollment = EnrollmentService.get_enrollment(db, enrollment_id)
        
        try:
            db.delete(enrollment)
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete enrollment with ID {enrollment_id}: {str(e)}"
            )

    @staticmethod
    def delete_enrollment_by_student_and_course(db: Session, student_id: int, course_id: int) -> None:
        """
        Delete an enrollment by student and course IDs
        
        Args:
            db: Database session
            student_id: Student ID
            course_id: Course ID
            
        Raises:
            HTTPException: If enrollment not found, invalid IDs, or deletion fails
        """
        # Validate IDs are positive integers
        EnrollmentService._validate_positive_id(student_id, "Student ID")
        EnrollmentService._validate_positive_id(course_id, "Course ID")
        
        # Verify student exists (will raise 404 if not found)
        StudentService.get_student(db, student_id)
        
        # Verify course exists (will raise 404 if not found)
        CourseService.get_course(db, course_id)
        
        # Find the enrollment
        enrollment = db.query(Enrollment).filter(
            Enrollment.student_id == student_id,
            Enrollment.course_id == course_id
        ).first()
        
        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No enrollment found for student with ID {student_id} in course with ID {course_id}. The student may not be enrolled in this course."
            )
        
        try:
            db.delete(enrollment)
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete enrollment for student {student_id} and course {course_id}: {str(e)}"
            )

