from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from src.db.postgres import Base


class Enrollment(Base):
    """
    Enrollment model representing the many-to-many relationship 
    between students and courses.
    
    Attributes:
        id: Primary key
        student_id: Foreign key to Student
        course_id: Foreign key to Course
        student: Relationship to Student model
        course: Relationship to Course model
    """
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)

    # Relationships
    student = relationship("Student", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")

    # Unique constraint to prevent duplicate enrollments
    __table_args__ = (
        UniqueConstraint('student_id', 'course_id', name='unique_student_course_enrollment'),
    )

