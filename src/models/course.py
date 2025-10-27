from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from src.db.postgres import Base


class Course(Base):
    """
    Course model representing an academic course.
    
    Attributes:
        id: Primary key
        name: Course name
        description: Detailed course description
        instructor: Name of the course instructor
        enrollments: Relationship to Enrollment model
    """
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    instructor = Column(String(100), nullable=False)

    # Relationship to enrollments (one course can have many enrollments)
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")

