from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from passlib.context import CryptContext
from src.db.postgres import Base

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Student(Base):
    """
    Student model representing a student in the enrollment system.

    Attributes:
        id: Primary key
        name: Student's full name
        email: Student's email address (unique)
        password_hash: Hashed password for authentication
        enrollments: Relationship to Enrollment model
    """
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)

    # Relationship to enrollments (one student can have many enrollments)
    enrollments = relationship("Enrollment", back_populates="student", cascade="all, delete-orphan")

    def set_password(self, password: str):
        """Hash and set the password"""
        self.password_hash = pwd_context.hash(password)

    def verify_password(self, password: str) -> bool:
        """Verify a password against the stored hash"""
        return pwd_context.verify(password, self.password_hash)

