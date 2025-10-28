#!/usr/bin/env python3
"""
Student tests for the Student Course Enrollment Portal API
Run with: pytest test/test_students.py -v
"""

import pytest
import requests
from typing import Dict

BASE_URL = "http://localhost:8000"


def generate_unique_email(prefix: str = "test") -> str:
    """Generate a unique email address for testing"""
    import time
    import random
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


class TestStudentEndpoints:
    """Test student CRUD operations (excluding creation which is handled by auth)"""

    def test_get_all_students(self, api_client):
        """Test getting all students"""
        response = requests.get(f"{api_client}/students/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_student_by_id(self, api_client):
        """Test getting a specific student by ID"""
        # First create a student via auth
        unique_email = generate_unique_email("test.get")
        login_data = {
            "email": unique_email,
            "password": "testpass123",
            "role": "student"
        }
        login_response = requests.post(f"{api_client}/auth/login", json=login_data)
        assert login_response.status_code == 200
        student_id = login_response.json()["user"]["id"]

        # Get the student
        response = requests.get(f"{api_client}/students/{student_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == student_id
        assert data["email"] == unique_email

    def test_get_student_not_found(self, api_client):
        """Test getting non-existent student returns 404"""
        response = requests.get(f"{api_client}/students/999999")
        assert response.status_code == 404

    def test_update_student(self, api_client):
        """Test updating student information"""
        # First create a student via auth
        unique_email = generate_unique_email("test.update")
        login_data = {
            "email": unique_email,
            "password": "testpass123",
            "role": "student"
        }
        login_response = requests.post(f"{api_client}/auth/login", json=login_data)
        assert login_response.status_code == 200
        student_id = login_response.json()["user"]["id"]

        # Update the student
        update_data = {"name": "Alice Johnson-Smith"}
        response = requests.put(f"{api_client}/students/{student_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["email"] == unique_email  # Email should remain unchanged

    def test_update_student_email_conflict(self, api_client):
        """Test updating student email to existing email fails"""
        # Create first student
        email1 = generate_unique_email("conflict1")
        login_data1 = {
            "email": email1,
            "password": "testpass123",
            "role": "student"
        }
        login_response1 = requests.post(f"{api_client}/auth/login", json=login_data1)
        assert login_response1.status_code == 200
        student_id1 = login_response1.json()["user"]["id"]

        # Create second student
        email2 = generate_unique_email("conflict2")
        login_data2 = {
            "email": email2,
            "password": "testpass123",
            "role": "student"
        }
        login_response2 = requests.post(f"{api_client}/auth/login", json=login_data2)
        assert login_response2.status_code == 200
        student_id2 = login_response2.json()["user"]["id"]

        # Try to update second student to first student's email
        update_data = {"email": email1}
        response = requests.put(f"{api_client}/students/{student_id2}", json=update_data)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()

    def test_delete_student(self, api_client):
        """Test deleting a student"""
        # First create a student via auth
        unique_email = generate_unique_email("test.delete")
        login_data = {
            "email": unique_email,
            "password": "testpass123",
            "role": "student"
        }
        login_response = requests.post(f"{api_client}/auth/login", json=login_data)
        assert login_response.status_code == 200
        student_id = login_response.json()["user"]["id"]

        # Delete the student
        response = requests.delete(f"{api_client}/students/{student_id}")
        assert response.status_code == 204

        # Verify deletion
        get_response = requests.get(f"{api_client}/students/{student_id}")
        assert get_response.status_code == 404

    def test_get_student_courses(self, api_client):
        """Test getting all courses a student is enrolled in"""
        # Create student via auth
        student_email = generate_unique_email("courses.student")
        login_data = {
            "email": student_email,
            "password": "testpass123",
            "role": "student"
        }
        login_response = requests.post(f"{api_client}/auth/login", json=login_data)
        assert login_response.status_code == 200
        student_id = login_response.json()["user"]["id"]

        # Create a course
        course_data = {
            "name": f"Test Course {int(__import__('time').time() * 1000)}",
            "description": "Test course for enrollment",
            "instructor": "Test Instructor"
        }
        course_response = requests.post(f"{api_client}/courses/", json=course_data)
        assert course_response.status_code == 201
        course_id = course_response.json()["id"]

        # Enroll student in course
        enrollment_data = {"student_id": student_id, "course_id": course_id}
        enrollment_response = requests.post(f"{api_client}/enrollments/", json=enrollment_data)
        assert enrollment_response.status_code == 201

        # Get student's courses
        response = requests.get(f"{api_client}/students/{student_id}/courses")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert any(course["id"] == course_id for course in data)

    def test_get_student_courses_empty(self, api_client):
        """Test getting courses for student with no enrollments"""
        # Create student via auth
        student_email = generate_unique_email("empty.courses")
        login_data = {
            "email": student_email,
            "password": "testpass123",
            "role": "student"
        }
        login_response = requests.post(f"{api_client}/auth/login", json=login_data)
        assert login_response.status_code == 200
        student_id = login_response.json()["user"]["id"]

        # Get student's courses (should be empty)
        response = requests.get(f"{api_client}/students/{student_id}/courses")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0


if __name__ == "__main__":
    print("Run student tests with: pytest test/test_students.py -v")
    print("For detailed output: pytest test/test_students.py -v -s")
