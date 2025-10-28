from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from src.db.postgres import Base


class Student(Base):
    """
    Student model representing a student in the enrollment system.
    
    Attributes:
        id: Primary key
        name: Student's full name
        email: Student's email address (unique)
        enrollments: Relationship to Enrollment model
    """
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)

    # Relationship to enrollments (one student can have many enrollments)
    enrollments = relationship("Enrollment", back_populates="student", cascade="all, delete-orphan")

