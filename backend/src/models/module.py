from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from src.db.postgres import Base


class Module(Base):
    """
    Module model representing a course module/lesson.
    
    Attributes:
        id: Primary key
        course_id: Foreign key to Course
        title: Module title
        description: Module description
        content: Module content/material (optional)
        order: Sequence order within the course
        course: Relationship to Course model
    """
    __tablename__ = "modules"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    order = Column(Integer, nullable=False, default=0)

    # Relationship to course (many modules belong to one course)
    course = relationship("Course", back_populates="modules")
