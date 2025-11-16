from langchain_core.tools import tool
from sqlalchemy.orm import Session
from typing import List, Union
from src.models.course import Course


@tool
def add_numbers(a: float, b: float) -> float:
    """
    Add two numbers together.

    Args:
        a: First number to add
        b: Second number to add

    Returns:
        The sum of the two numbers (as a float, will be formatted by the LLM in markdown)
    """
    return a + b

# DB tools


@tool
def fetch_all_courses() -> str:
    """
    Fetch all courses from the database.

    Returns:
        A formatted HTML string listing all available courses with their IDs, names, and descriptions.
    """
    from src.db.postgres import get_db
    from src.services.course_service import CourseService
    import html

    try:
        db = next(get_db())
        courses = CourseService.get_all_courses(db)

        if not courses:
            return "<h2>Available Courses</h2><p><strong>No courses are currently available.</strong></p>"

        html_output = "<h2>Available Courses</h2>"
        html_output += "<table><thead><tr><th>ID</th><th>Course Name</th><th>Instructor</th><th>Description</th></tr></thead><tbody>"
        
        for course in courses:
            description = course.description if course.description else "<em>No description</em>"
            # Escape HTML special characters
            description = html.escape(description)
            # Replace newlines with <br> tags
            description = description.replace("\n", "<br>").replace("\r", "")
            course_name = html.escape(str(course.name))
            instructor = html.escape(str(course.instructor))
            html_output += f"<tr><td>{course.id}</td><td><strong>{course_name}</strong></td><td>{instructor}</td><td>{description}</td></tr>"
        
        html_output += "</tbody></table>"
        return html_output

    except Exception as e:
        error_msg = html.escape(str(e))
        return f"<h2>Error</h2><p><strong>Error fetching courses:</strong> <code>{error_msg}</code></p>"


@tool
def enroll_into_course(student_id: Union[int, str], course_id: Union[int, str]) -> str:
    """
    Enroll a student into a course.

    Args:
        student_id: The ID of the student to enroll (can be int or string, will be converted to int)
        course_id: The ID of the course to enroll in (can be int or string, will be converted to int)

    Returns:
        An HTML-formatted confirmation message about the enrollment or an error message if enrollment fails.
    """
    from src.db.postgres import get_db
    from src.services.enrollment_service import EnrollmentService
    from pydantic import BaseModel
    import html

    class EnrollmentData(BaseModel):
        student_id: int
        course_id: int

    try:
        # Convert IDs to int if they are strings or other numeric types
        try:
            if isinstance(student_id, str):
                student_id = int(student_id.strip())
            else:
                student_id = int(student_id)
        except (ValueError, TypeError) as e:
            error_msg = html.escape(f"Invalid student_id: {student_id}. Must be a valid integer.")
            return f"<h2>❌ Enrollment Failed</h2><p><strong>Error:</strong> <code>{error_msg}</code></p>"
        
        try:
            if isinstance(course_id, str):
                course_id = int(course_id.strip())
            else:
                course_id = int(course_id)
        except (ValueError, TypeError) as e:
            error_msg = html.escape(f"Invalid course_id: {course_id}. Must be a valid integer.")
            return f"<h2>❌ Enrollment Failed</h2><p><strong>Error:</strong> <code>{error_msg}</code></p>"
        
        db = next(get_db())
        enrollment_data = EnrollmentData(student_id=student_id, course_id=course_id)
        enrollment = EnrollmentService.create_enrollment(db, enrollment_data)

        html_output = "<h2>✅ Enrollment Successful</h2>"
        html_output += "<ul>"
        html_output += f"<li><strong>Student ID:</strong> <code>{student_id}</code></li>"
        html_output += f"<li><strong>Course ID:</strong> <code>{course_id}</code></li>"
        html_output += f"<li><strong>Enrollment ID:</strong> <code>{enrollment.id}</code></li>"
        html_output += "</ul>"
        html_output += f"<p>Student <code>{student_id}</code> has been successfully enrolled into course <code>{course_id}</code>.</p>"

        return html_output

    except Exception as e:
        error_msg = html.escape(str(e))
        html_output = "<h2>❌ Enrollment Failed</h2>"
        html_output += f"<p><strong>Error:</strong> Failed to enroll student <code>{student_id}</code> into course <code>{course_id}</code>.</p>"
        html_output += f"<p><strong>Details:</strong> <code>{error_msg}</code></p>"
        return html_output


@tool
def unenroll_from_course(student_id: Union[int, str], course_id: Union[int, str]) -> str:
    """
    Unenroll a student from a course.

    Args:
        student_id: The ID of the student to unenroll (can be int or string, will be converted to int)
        course_id: The ID of the course to unenroll from (can be int or string, will be converted to int)

    Returns:
        An HTML-formatted confirmation message about the unenrollment or an error message if unenrollment fails.
    """
    from src.db.postgres import get_db
    from src.services.enrollment_service import EnrollmentService
    import html

    try:
        # Convert IDs to int if they are strings or other numeric types
        try:
            if isinstance(student_id, str):
                student_id = int(student_id.strip())
            else:
                student_id = int(student_id)
        except (ValueError, TypeError) as e:
            error_msg = html.escape(f"Invalid student_id: {student_id}. Must be a valid integer.")
            return f"<h2>❌ Unenrollment Failed</h2><p><strong>Error:</strong> <code>{error_msg}</code></p>"
        
        try:
            if isinstance(course_id, str):
                course_id = int(course_id.strip())
            else:
                course_id = int(course_id)
        except (ValueError, TypeError) as e:
            error_msg = html.escape(f"Invalid course_id: {course_id}. Must be a valid integer.")
            return f"<h2>❌ Unenrollment Failed</h2><p><strong>Error:</strong> <code>{error_msg}</code></p>"
        
        db = next(get_db())
        EnrollmentService.delete_enrollment_by_student_and_course(db, student_id, course_id)

        html_output = "<h2>✅ Unenrollment Successful</h2>"
        html_output += "<ul>"
        html_output += f"<li><strong>Student ID:</strong> <code>{student_id}</code></li>"
        html_output += f"<li><strong>Course ID:</strong> <code>{course_id}</code></li>"
        html_output += "</ul>"
        html_output += f"<p>Student <code>{student_id}</code> has been successfully unenrolled from course <code>{course_id}</code>.</p>"

        return html_output

    except Exception as e:
        error_msg = html.escape(str(e))
        html_output = "<h2>❌ Unenrollment Failed</h2>"
        html_output += f"<p><strong>Error:</strong> Failed to unenroll student <code>{student_id}</code> from course <code>{course_id}</code>.</p>"
        html_output += f"<p><strong>Details:</strong> <code>{error_msg}</code></p>"
        return html_output


@tool
def search_course_information(query: str) -> str:
    """
    Search for course information using semantic search.

    Args:
        query: The search query about courses (e.g., "machine learning courses", "programming classes", "courses about AI")

    Returns:
        Relevant course information in HTML format based on the semantic search query.
    """
    from src.services.rag_service import rag_service
    import html

    try:
        context = rag_service.get_course_context(query, max_results=3)

        print("Context: ", context)

        if "No relevant course information found" in context or "Error retrieving" in context:
            return "<h2>Course Search Results</h2><p><strong>No relevant course information found.</strong></p><p>You might want to use <code>fetch_all_courses</code> to see all available courses.</p>"

        return context

    except Exception as e:
        error_msg = html.escape(str(e))
        return f"<h2>Error</h2><p><strong>Error searching course information:</strong> <code>{error_msg}</code></p><p>Try using <code>fetch_all_courses</code> instead.</p>"