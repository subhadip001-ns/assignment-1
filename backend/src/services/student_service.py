from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import List, Optional

from src.models.student import Student
from src.schemas.student import StudentCreate, StudentUpdate


class StudentService:
    """Service layer for student-related business logic"""

    # Student creation is now handled by AuthService during login/signup

    @staticmethod
    def get_student(db: Session, student_id: int) -> Student:
        """
        Get a student by ID
        
        Args:
            db: Database session
            student_id: Student ID
            
        Returns:
            Student object
            
        Raises:
            HTTPException: If student not found
        """
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student with id {student_id} not found"
            )
        return student

    @staticmethod
    def get_all_students(db: Session, skip: int = 0, limit: int = 100) -> List[Student]:
        """
        Get all students with pagination
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of students
        """
        return db.query(Student).offset(skip).limit(limit).all()

    @staticmethod
    def update_student(db: Session, student_id: int, student_data: StudentUpdate) -> Student:
        """
        Update a student
        
        Args:
            db: Database session
            student_id: Student ID
            student_data: Student update data
            
        Returns:
            Updated student object
            
        Raises:
            HTTPException: If student not found or email already exists
        """
        student = StudentService.get_student(db, student_id)
        
        update_data = student_data.model_dump(exclude_unset=True)
        if not update_data:
            return student
        
        try:
            for key, value in update_data.items():
                setattr(student, key, value)
            
            db.commit()
            db.refresh(student)
            return student
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Student with email {student_data.email} already exists"
            )

    @staticmethod
    def delete_student(db: Session, student_id: int) -> None:
        """
        Delete a student
        
        Args:
            db: Database session
            student_id: Student ID
            
        Raises:
            HTTPException: If student not found
        """
        student = StudentService.get_student(db, student_id)
        db.delete(student)
        db.commit()

    @staticmethod
    def get_student_courses(db: Session, student_id: int):
        """
        Get all courses a student is enrolled in
        
        Args:
            db: Database session
            student_id: Student ID
            
        Returns:
            List of courses
            
        Raises:
            HTTPException: If student not found
        """
        student = StudentService.get_student(db, student_id)
        return [enrollment.course for enrollment in student.enrollments]

