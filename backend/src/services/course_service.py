from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List

from src.models.course import Course
from src.schemas.course import CourseCreate, CourseUpdate
from src.services.rag_service import rag_service


class CourseService:
    """Service layer for course-related business logic"""

    @staticmethod
    def create_course(db: Session, course_data: CourseCreate) -> Course:
        """
        Create a new course

        Args:
            db: Database session
            course_data: Course creation data

        Returns:
            Created course object
        """
        course = Course(
            name=course_data.name,
            description=course_data.description,
            instructor=course_data.instructor
        )
        db.add(course)
        db.commit()
        db.refresh(course)

        # Ingest course document into RAG system
        try:
            rag_service.ingest_course_document(
                course_id=course.id,
                course_name=course.name,
                course_description=course.description or ""
            )
        except Exception as e:
            # Log the error but don't fail course creation
            print(f"Warning: Failed to ingest course {course.id} into RAG system: {e}")

        return course

    @staticmethod
    def get_course(db: Session, course_id: int) -> Course:
        """
        Get a course by ID
        
        Args:
            db: Database session
            course_id: Course ID
            
        Returns:
            Course object
            
        Raises:
            HTTPException: If course not found
        """
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Course with id {course_id} not found"
            )
        return course

    @staticmethod
    def get_all_courses(db: Session, skip: int = 0, limit: int = 100) -> List[Course]:
        """
        Get all courses with pagination
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of courses
        """
        return db.query(Course).offset(skip).limit(limit).all()

    @staticmethod
    def update_course(db: Session, course_id: int, course_data: CourseUpdate) -> Course:
        """
        Update a course
        
        Args:
            db: Database session
            course_id: Course ID
            course_data: Course update data
            
        Returns:
            Updated course object
            
        Raises:
            HTTPException: If course not found
        """
        course = CourseService.get_course(db, course_id)
        
        update_data = course_data.model_dump(exclude_unset=True)
        if not update_data:
            return course
        
        for key, value in update_data.items():
            setattr(course, key, value)
        
        db.commit()
        db.refresh(course)
        return course

    @staticmethod
    def delete_course(db: Session, course_id: int) -> None:
        """
        Delete a course
        
        Args:
            db: Database session
            course_id: Course ID
            
        Raises:
            HTTPException: If course not found
        """
        course = CourseService.get_course(db, course_id)
        db.delete(course)
        db.commit()

    @staticmethod
    def get_course_students(db: Session, course_id: int):
        """
        Get all students enrolled in a course
        
        Args:
            db: Database session
            course_id: Course ID
            
        Returns:
            List of students
            
        Raises:
            HTTPException: If course not found
        """
        course = CourseService.get_course(db, course_id)
        return [enrollment.student for enrollment in course.enrollments]

