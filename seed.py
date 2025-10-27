"""
Database seeding script to populate the database with sample data.

This script creates sample students and courses for testing and development.
"""

from sqlalchemy.orm import Session
from sqlalchemy import text
from src.db.postgres import SessionLocal, init_db
from src.models.student import Student
from src.models.course import Course
from src.models.enrollment import Enrollment


def clear_database(db: Session):
    """
    Clear all existing data from the database.
    WARNING: This will delete all data!
    """
    print("Clearing existing data...")
    
    # TRUNCATE is faster and automatically resets sequences with RESTART IDENTITY
    db.execute(text("TRUNCATE TABLE enrollments, students, courses RESTART IDENTITY CASCADE"))
    db.commit()
    
    print("Database cleared.")


def seed_students(db: Session):
    """Create sample students."""
    print("\nSeeding students...")
    
    students_data = [
        {"name": "Alice Johnson", "email": "alice.johnson@university.edu"},
        {"name": "Bob Smith", "email": "bob.smith@university.edu"},
        {"name": "Charlie Davis", "email": "charlie.davis@university.edu"},
        {"name": "Diana Martinez", "email": "diana.martinez@university.edu"},
        {"name": "Ethan Brown", "email": "ethan.brown@university.edu"},
        {"name": "Fiona Wilson", "email": "fiona.wilson@university.edu"},
        {"name": "George Taylor", "email": "george.taylor@university.edu"},
        {"name": "Hannah Lee", "email": "hannah.lee@university.edu"},
        {"name": "Isaac Anderson", "email": "isaac.anderson@university.edu"},
        {"name": "Julia Thomas", "email": "julia.thomas@university.edu"},
    ]
    
    students = []
    for student_data in students_data:
        student = Student(**student_data)
        db.add(student)
        students.append(student)
    
    db.commit()
    print(f"Created {len(students)} students")
    return students


def seed_courses(db: Session):
    """Create sample courses."""
    print("\nSeeding courses...")
    
    courses_data = [
        {
            "name": "Introduction to Computer Science",
            "description": "Fundamental concepts of programming, algorithms, and data structures. Perfect for beginners.",
            "instructor": "Dr. Sarah Williams"
        },
        {
            "name": "Web Development Fundamentals",
            "description": "Learn HTML, CSS, JavaScript, and modern web development practices. Build real-world projects.",
            "instructor": "Prof. Michael Chen"
        },
        {
            "name": "Data Structures and Algorithms",
            "description": "Advanced study of data structures, algorithm design, and complexity analysis.",
            "instructor": "Dr. Robert Garcia"
        },
        {
            "name": "Database Management Systems",
            "description": "Relational databases, SQL, normalization, and database design principles.",
            "instructor": "Prof. Emily Rodriguez"
        },
        {
            "name": "Machine Learning Basics",
            "description": "Introduction to machine learning algorithms, neural networks, and practical applications.",
            "instructor": "Dr. James Peterson"
        },
        {
            "name": "Mobile App Development",
            "description": "Building native and cross-platform mobile applications for iOS and Android.",
            "instructor": "Prof. Lisa Kim"
        },
        {
            "name": "Cloud Computing",
            "description": "Cloud architecture, AWS, Azure, containerization, and microservices.",
            "instructor": "Dr. David Anderson"
        },
        {
            "name": "Cybersecurity Fundamentals",
            "description": "Network security, cryptography, ethical hacking, and security best practices.",
            "instructor": "Prof. Amanda White"
        },
        {
            "name": "Software Engineering Principles",
            "description": "Software development lifecycle, design patterns, testing, and project management.",
            "instructor": "Dr. Christopher Hall"
        },
        {
            "name": "Artificial Intelligence",
            "description": "AI concepts, problem-solving techniques, and intelligent agent design.",
            "instructor": "Prof. Jennifer Martinez"
        },
    ]
    
    courses = []
    for course_data in courses_data:
        course = Course(**course_data)
        db.add(course)
        courses.append(course)
    
    db.commit()
    print(f"Created {len(courses)} courses")
    return courses


def seed_database(clear_first: bool = True):
    """
    Main function to seed the database with sample data.
    
    Args:
        clear_first: If True, clears existing data before seeding
    """
    print("Starting database seeding process...")
    
    # Initialize database tables
    init_db()
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Clear existing data if requested
        if clear_first:
            clear_database(db)
        
        # Seed data
        students = seed_students(db)
        courses = seed_courses(db)
        
        print("\n" + "="*50)
        print("Database seeding completed successfully!")
        print("="*50)
        print(f"Summary:")
        print(f"   - Students: {len(students)}")
        print(f"   - Courses: {len(courses)}")
        print("="*50)
        
    except Exception as e:
        print(f"\nError during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database(clear_first=True)

