from langchain_core.tools import tool
from sqlalchemy.orm import Session
from typing import List
from src.models.course import Course


@tool
def add_numbers(a: float, b: float) -> float:
    """
    Add two numbers together.

    Args:
        a: First number to add
        b: Second number to add

    Returns:
        The sum of the two numbers
    """
    return a + b

# DB tools


@tool
def fetch_all_courses() -> str:
    """
    Fetch all courses from the database.

    Returns:
        A formatted string listing all available courses with their IDs, names, and descriptions.
    """
    from src.db.postgres import get_db
    from src.services.course_service import CourseService

    try:
        db = next(get_db())
        courses = CourseService.get_all_courses(db)

        if not courses:
            return "No courses are currently available."

        course_list = []
        for course in courses:
            course_info = f"ID: {course.id}, Name: {course.name}, Instructor: {course.instructor}"
            if course.description:
                course_info += f", Description: {course.description}"
            course_list.append(course_info)

        return "Available courses:\n" + "\n".join(course_list)

    except Exception as e:
        return f"Error fetching courses: {str(e)}"


@tool
def enroll_into_course(student_id: int, course_id: int) -> str:
    """
    Enroll a student into a course.

    Args:
        student_id: The ID of the student to enroll
        course_id: The ID of the course to enroll in

    Returns:
        A confirmation message about the enrollment or an error message if enrollment fails.
    """
    from src.db.postgres import get_db
    from src.services.enrollment_service import EnrollmentService
    from pydantic import BaseModel

    class EnrollmentData(BaseModel):
        student_id: int
        course_id: int

    try:
        db = next(get_db())
        enrollment_data = EnrollmentData(student_id=student_id, course_id=course_id)
        enrollment = EnrollmentService.create_enrollment(db, enrollment_data)

        return f"Successfully enrolled student {student_id} into course {course_id}. Enrollment ID: {enrollment.id}"

    except Exception as e:
        return f"Failed to enroll student {student_id} into course {course_id}: {str(e)}"


@tool
def search_course_information(query: str) -> str:
    """
    Search for course information using semantic search.

    Args:
        query: The search query about courses (e.g., "machine learning courses", "programming classes", "courses about AI")

    Returns:
        Relevant course information based on the semantic search query.
    """
    from src.services.rag_service import rag_service

    try:
        context = rag_service.get_course_context(query, max_results=3)

        print("Context: ", context)

        if "No relevant course information found" in context or "Error retrieving" in context:
            return "I couldn't find specific course information matching your query. You might want to use 'fetch_all_courses' to see all available courses."

        return context

    except Exception as e:
        return f"Error searching course information: {str(e)}. Try using 'fetch_all_courses' instead."