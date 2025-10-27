#!/usr/bin/env python3
"""
Comprehensive test suite for the Student Course Enrollment Portal API
Run with: pytest test_api.py -v
Make sure the API server is running: python main.py
"""

import pytest
import requests
from typing import Dict, List
import time
import random

BASE_URL = "http://localhost:8000"


def generate_unique_email(prefix: str = "test") -> str:
    """Generate a unique email address for testing"""
    timestamp = int(time.time() * 1000)
    random_num = random.randint(1000, 9999)
    return f"{prefix}.{timestamp}.{random_num}@example.com"


@pytest.fixture(scope="module")
def api_client():
    """Fixture to verify API is running before tests"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        assert response.status_code == 200, "API health check failed"
        return BASE_URL
    except requests.exceptions.ConnectionError:
        pytest.skip("API server is not running. Start it with: python main.py")


@pytest.fixture
def sample_student_data() -> Dict:
    """Fixture providing sample student data with unique email"""
    return {
        "name": "Alice Johnson",
        "email": generate_unique_email("alice")
    }


@pytest.fixture
def sample_course_data() -> Dict:
    """Fixture providing sample course data"""
    return {
        "name": "Introduction to Testing",
        "description": "Learn testing best practices",
        "instructor": "Dr. Test Master"
    }


class TestHealthCheck:
    """Test health check endpoint"""
    
    def test_health_check(self, api_client):
        """Test health check endpoint returns 200"""
        response = requests.get(f"{api_client}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestStudentEndpoints:
    """Test student CRUD operations"""
    
    def test_create_student_success(self, api_client, sample_student_data):
        """Test successful student creation"""
        response = requests.post(f"{api_client}/students/", json=sample_student_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_student_data["name"]
        assert data["email"] == sample_student_data["email"]
        assert "id" in data
    
    def test_create_student_duplicate_email(self, api_client):
        """Test creating student with duplicate email fails"""
        unique_email = generate_unique_email("duplicate")
        student_data = {
            "name": "Bob Duplicate",
            "email": unique_email
        }
        # Create first student
        response1 = requests.post(f"{api_client}/students/", json=student_data)
        assert response1.status_code == 201
        
        # Try to create duplicate
        response2 = requests.post(f"{api_client}/students/", json=student_data)
        assert response2.status_code == 400
        assert "already exists" in response2.json()["detail"].lower()
    
    def test_create_student_invalid_data(self, api_client):
        """Test creating student with invalid data"""
        invalid_data = {"name": "No Email"}
        response = requests.post(f"{api_client}/students/", json=invalid_data)
        assert response.status_code == 422
    
    def test_get_all_students(self, api_client):
        """Test getting all students"""
        response = requests.get(f"{api_client}/students/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_student_by_id(self, api_client, sample_student_data):
        """Test getting a specific student by ID"""
        # Create a student first
        create_response = requests.post(f"{api_client}/students/", json=sample_student_data)
        student_id = create_response.json()["id"]
        
        # Get the student
        response = requests.get(f"{api_client}/students/{student_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == student_id
    
    def test_get_student_not_found(self, api_client):
        """Test getting non-existent student returns 404"""
        response = requests.get(f"{api_client}/students/999999")
        assert response.status_code == 404
    
    def test_update_student(self, api_client, sample_student_data):
        """Test updating student information"""
        # Create a student
        create_response = requests.post(f"{api_client}/students/", json=sample_student_data)
        student_id = create_response.json()["id"]
        
        # Update the student
        update_data = {"name": "Alice Johnson-Smith"}
        response = requests.put(f"{api_client}/students/{student_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
    
    def test_delete_student(self, api_client, sample_student_data):
        """Test deleting a student"""
        # Create a student
        create_response = requests.post(f"{api_client}/students/", json=sample_student_data)
        student_id = create_response.json()["id"]
        
        # Delete the student
        response = requests.delete(f"{api_client}/students/{student_id}")
        assert response.status_code == 204
        
        # Verify deletion
        get_response = requests.get(f"{api_client}/students/{student_id}")
        assert get_response.status_code == 404


class TestCourseEndpoints:
    """Test course CRUD operations"""
    
    def test_create_course_success(self, api_client, sample_course_data):
        """Test successful course creation"""
        response = requests.post(f"{api_client}/courses/", json=sample_course_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_course_data["name"]
        assert "id" in data
    
    def test_create_course_invalid_data(self, api_client):
        """Test creating course with missing required fields"""
        invalid_data = {"name": "Incomplete Course"}
        response = requests.post(f"{api_client}/courses/", json=invalid_data)
        assert response.status_code == 422
    
    def test_get_all_courses(self, api_client):
        """Test getting all courses"""
        response = requests.get(f"{api_client}/courses/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_course_by_id(self, api_client, sample_course_data):
        """Test getting a specific course by ID"""
        # Create a course
        create_response = requests.post(f"{api_client}/courses/", json=sample_course_data)
        course_id = create_response.json()["id"]
        
        # Get the course
        response = requests.get(f"{api_client}/courses/{course_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == course_id
    
    def test_get_course_not_found(self, api_client):
        """Test getting non-existent course returns 404"""
        response = requests.get(f"{api_client}/courses/999999")
        assert response.status_code == 404
    
    def test_update_course(self, api_client, sample_course_data):
        """Test updating course information"""
        # Create a course
        create_response = requests.post(f"{api_client}/courses/", json=sample_course_data)
        course_id = create_response.json()["id"]
        
        # Update the course
        update_data = {"instructor": "Dr. Test Master, PhD"}
        response = requests.put(f"{api_client}/courses/{course_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["instructor"] == update_data["instructor"]
    
    def test_delete_course(self, api_client, sample_course_data):
        """Test deleting a course"""
        # Create a course
        create_response = requests.post(f"{api_client}/courses/", json=sample_course_data)
        course_id = create_response.json()["id"]
        
        # Delete the course
        response = requests.delete(f"{api_client}/courses/{course_id}")
        assert response.status_code == 204
        
        # Verify deletion
        get_response = requests.get(f"{api_client}/courses/{course_id}")
        assert get_response.status_code == 404


class TestEnrollmentEndpoints:
    """Test enrollment operations including edge cases"""
    
    @pytest.fixture
    def setup_student_and_course(self, api_client):
        """Create a student and course for enrollment tests"""
        student_data = {
            "name": "Test Student",
            "email": generate_unique_email("enrollment.test")
        }
        course_data = {
            "name": f"Test Course {int(time.time() * 1000)}",
            "description": "For enrollment testing",
            "instructor": "Test Instructor"
        }
        
        student_response = requests.post(f"{api_client}/students/", json=student_data)
        course_response = requests.post(f"{api_client}/courses/", json=course_data)
        
        # Check if creation was successful
        assert student_response.status_code == 201, f"Failed to create student: {student_response.text}"
        assert course_response.status_code == 201, f"Failed to create course: {course_response.text}"
        
        return {
            "student_id": student_response.json()["id"],
            "course_id": course_response.json()["id"]
        }
    
    def test_create_enrollment_success(self, api_client, setup_student_and_course):
        """Test successful enrollment creation"""
        enrollment_data = {
            "student_id": setup_student_and_course["student_id"],
            "course_id": setup_student_and_course["course_id"]
        }
        response = requests.post(f"{api_client}/enrollments/", json=enrollment_data)
        assert response.status_code == 201
        data = response.json()
        assert data["student_id"] == enrollment_data["student_id"]
        assert data["course_id"] == enrollment_data["course_id"]
    
    def test_create_enrollment_duplicate(self, api_client, setup_student_and_course):
        """Test that duplicate enrollment is rejected with 409"""
        enrollment_data = {
            "student_id": setup_student_and_course["student_id"],
            "course_id": setup_student_and_course["course_id"]
        }
        
        # Create first enrollment
        response1 = requests.post(f"{api_client}/enrollments/", json=enrollment_data)
        assert response1.status_code == 201
        
        # Try to create duplicate
        response2 = requests.post(f"{api_client}/enrollments/", json=enrollment_data)
        assert response2.status_code == 409
        assert "already enrolled" in response2.json()["detail"].lower()
    
    def test_create_enrollment_invalid_student_id(self, api_client, setup_student_and_course):
        """Test enrollment with negative student ID fails with 422"""
        enrollment_data = {
            "student_id": -1,
            "course_id": setup_student_and_course["course_id"]
        }
        response = requests.post(f"{api_client}/enrollments/", json=enrollment_data)
        assert response.status_code == 422
        detail = response.json()["detail"]
        # Handle both string and list format for detail
        detail_str = detail if isinstance(detail, str) else str(detail)
        # Pydantic validation says "greater than 0" not "positive integer"
        assert "greater than 0" in detail_str.lower()
    
    def test_create_enrollment_invalid_course_id(self, api_client, setup_student_and_course):
        """Test enrollment with zero course ID fails with 422"""
        enrollment_data = {
            "student_id": setup_student_and_course["student_id"],
            "course_id": 0
        }
        response = requests.post(f"{api_client}/enrollments/", json=enrollment_data)
        assert response.status_code == 422
        detail = response.json()["detail"]
        # Handle both string and list format for detail
        detail_str = detail if isinstance(detail, str) else str(detail)
        # Pydantic validation says "greater than 0" not "positive integer"
        assert "greater than 0" in detail_str.lower()
    
    def test_create_enrollment_nonexistent_student(self, api_client, setup_student_and_course):
        """Test enrollment with non-existent student fails with 404"""
        enrollment_data = {
            "student_id": 999999,
            "course_id": setup_student_and_course["course_id"]
        }
        response = requests.post(f"{api_client}/enrollments/", json=enrollment_data)
        assert response.status_code == 404
        assert "student" in response.json()["detail"].lower()
    
    def test_create_enrollment_nonexistent_course(self, api_client, setup_student_and_course):
        """Test enrollment with non-existent course fails with 404"""
        enrollment_data = {
            "student_id": setup_student_and_course["student_id"],
            "course_id": 999999
        }
        response = requests.post(f"{api_client}/enrollments/", json=enrollment_data)
        assert response.status_code == 404
        assert "course" in response.json()["detail"].lower()
    
    def test_get_all_enrollments(self, api_client):
        """Test getting all enrollments"""
        response = requests.get(f"{api_client}/enrollments/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_enrollments_with_pagination(self, api_client):
        """Test pagination parameters"""
        response = requests.get(f"{api_client}/enrollments/?skip=0&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10
    
    def test_get_enrollments_invalid_pagination_negative_skip(self, api_client):
        """Test that negative skip parameter fails with 422"""
        response = requests.get(f"{api_client}/enrollments/?skip=-1&limit=10")
        assert response.status_code == 422
        detail = response.json()["detail"]
        detail_str = detail if isinstance(detail, str) else str(detail)
        assert "skip" in detail_str.lower()
    
    def test_get_enrollments_invalid_pagination_zero_limit(self, api_client):
        """Test that zero limit parameter fails with 422"""
        response = requests.get(f"{api_client}/enrollments/?skip=0&limit=0")
        assert response.status_code == 422
        detail = response.json()["detail"]
        detail_str = detail if isinstance(detail, str) else str(detail)
        assert "limit" in detail_str.lower()
    
    def test_get_enrollments_invalid_pagination_exceeds_max(self, api_client):
        """Test that limit exceeding 1000 fails with 422"""
        response = requests.get(f"{api_client}/enrollments/?skip=0&limit=1001")
        assert response.status_code == 422
        detail = response.json()["detail"]
        detail_str = detail if isinstance(detail, str) else str(detail)
        assert "1000" in detail_str
    
    def test_get_enrollment_by_id(self, api_client, setup_student_and_course):
        """Test getting a specific enrollment by ID"""
        # Create enrollment
        enrollment_data = {
            "student_id": setup_student_and_course["student_id"],
            "course_id": setup_student_and_course["course_id"]
        }
        create_response = requests.post(f"{api_client}/enrollments/", json=enrollment_data)
        enrollment_id = create_response.json()["id"]
        
        # Get the enrollment
        response = requests.get(f"{api_client}/enrollments/{enrollment_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == enrollment_id
    
    def test_get_enrollment_invalid_id(self, api_client):
        """Test getting enrollment with invalid ID fails with 422"""
        response = requests.get(f"{api_client}/enrollments/-1")
        assert response.status_code == 422
        detail = response.json()["detail"]
        detail_str = detail if isinstance(detail, str) else str(detail)
        assert "positive integer" in detail_str.lower()
    
    def test_get_enrollment_not_found(self, api_client):
        """Test getting non-existent enrollment returns 404"""
        response = requests.get(f"{api_client}/enrollments/999999")
        assert response.status_code == 404
    
    def test_delete_enrollment_success(self, api_client, setup_student_and_course):
        """Test successful enrollment deletion"""
        # Create enrollment
        enrollment_data = {
            "student_id": setup_student_and_course["student_id"],
            "course_id": setup_student_and_course["course_id"]
        }
        create_response = requests.post(f"{api_client}/enrollments/", json=enrollment_data)
        enrollment_id = create_response.json()["id"]
        
        # Delete the enrollment
        response = requests.delete(f"{api_client}/enrollments/{enrollment_id}")
        assert response.status_code == 204
        
        # Verify deletion
        get_response = requests.get(f"{api_client}/enrollments/{enrollment_id}")
        assert get_response.status_code == 404
    
    def test_delete_enrollment_invalid_id(self, api_client):
        """Test deleting enrollment with invalid ID fails with 422"""
        response = requests.delete(f"{api_client}/enrollments/0")
        assert response.status_code == 422
        detail = response.json()["detail"]
        detail_str = detail if isinstance(detail, str) else str(detail)
        assert "positive integer" in detail_str.lower()
    
    def test_delete_enrollment_not_found(self, api_client):
        """Test deleting non-existent enrollment fails with 404"""
        response = requests.delete(f"{api_client}/enrollments/999999")
        assert response.status_code == 404
    
    def test_get_student_courses(self, api_client, setup_student_and_course):
        """Test getting all courses for a student"""
        # Create enrollment
        enrollment_data = {
            "student_id": setup_student_and_course["student_id"],
            "course_id": setup_student_and_course["course_id"]
        }
        requests.post(f"{api_client}/enrollments/", json=enrollment_data)
        
        # Get student's courses
        response = requests.get(
            f"{api_client}/students/{setup_student_and_course['student_id']}/courses"
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert any(course["id"] == setup_student_and_course["course_id"] for course in data)
    
    def test_get_course_students(self, api_client, setup_student_and_course):
        """Test getting all students in a course"""
        # Create enrollment
        enrollment_data = {
            "student_id": setup_student_and_course["student_id"],
            "course_id": setup_student_and_course["course_id"]
        }
        requests.post(f"{api_client}/enrollments/", json=enrollment_data)
        
        # Get course's students
        response = requests.get(
            f"{api_client}/courses/{setup_student_and_course['course_id']}/students"
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert any(student["id"] == setup_student_and_course["student_id"] for student in data)


class TestIntegrationScenarios:
    """Test complete workflows and integration scenarios"""
    
    def test_complete_enrollment_workflow(self, api_client):
        """Test complete workflow: create student, course, enroll, verify, unenroll"""
        # Create student
        student_data = {
            "name": "Integration Test Student",
            "email": generate_unique_email("integration.test")
        }
        student_response = requests.post(f"{api_client}/students/", json=student_data)
        assert student_response.status_code == 201
        student_id = student_response.json()["id"]
        
        # Create course
        course_data = {
            "name": f"Integration Test Course {int(time.time() * 1000)}",
            "description": "Full workflow test",
            "instructor": "Test Instructor"
        }
        course_response = requests.post(f"{api_client}/courses/", json=course_data)
        assert course_response.status_code == 201
        course_id = course_response.json()["id"]
        
        # Enroll student in course
        enrollment_data = {"student_id": student_id, "course_id": course_id}
        enrollment_response = requests.post(f"{api_client}/enrollments/", json=enrollment_data)
        assert enrollment_response.status_code == 201
        enrollment_id = enrollment_response.json()["id"]
        
        # Verify enrollment exists
        verify_response = requests.get(f"{api_client}/enrollments/{enrollment_id}")
        assert verify_response.status_code == 200
        
        # Verify student has the course
        student_courses = requests.get(f"{api_client}/students/{student_id}/courses")
        assert student_courses.status_code == 200
        assert any(c["id"] == course_id for c in student_courses.json())
        
        # Unenroll student
        delete_response = requests.delete(f"{api_client}/enrollments/{enrollment_id}")
        assert delete_response.status_code == 204
        
        # Verify enrollment no longer exists
        final_check = requests.get(f"{api_client}/enrollments/{enrollment_id}")
        assert final_check.status_code == 404
        
        # Cleanup
        requests.delete(f"{api_client}/students/{student_id}")
        requests.delete(f"{api_client}/courses/{course_id}")
    
    def test_cascade_delete_student_removes_enrollments(self, api_client):
        """Test that deleting a student also removes their enrollments"""
        # Create student and course
        student_data = {
            "name": "Cascade Test Student",
            "email": generate_unique_email("cascade.student")
        }
        student_response = requests.post(f"{api_client}/students/", json=student_data)
        student_id = student_response.json()["id"]
        
        course_data = {
            "name": f"Cascade Test Course {int(time.time() * 1000)}",
            "description": "Cascade delete test",
            "instructor": "Test Instructor"
        }
        course_response = requests.post(f"{api_client}/courses/", json=course_data)
        course_id = course_response.json()["id"]
        
        # Enroll student
        enrollment_data = {"student_id": student_id, "course_id": course_id}
        enrollment_response = requests.post(f"{api_client}/enrollments/", json=enrollment_data)
        enrollment_id = enrollment_response.json()["id"]
        
        # Delete student
        delete_response = requests.delete(f"{api_client}/students/{student_id}")
        assert delete_response.status_code == 204
        
        # Verify enrollment is also deleted (cascade)
        enrollment_check = requests.get(f"{api_client}/enrollments/{enrollment_id}")
        assert enrollment_check.status_code == 404
        
        # Cleanup
        requests.delete(f"{api_client}/courses/{course_id}")


if __name__ == "__main__":
    print("Run tests with: pytest test_api.py -v")
    print("For detailed output: pytest test_api.py -v -s")
    print("To run specific test class: pytest test_api.py::TestEnrollmentEndpoints -v")
