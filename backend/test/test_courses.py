#!/usr/bin/env python3
"""
Course tests for the Student Course Enrollment Portal API
Run with: pytest test/test_courses.py -v
"""

import pytest
import requests
from typing import Dict

BASE_URL = "http://localhost:8000"


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
def sample_course_data() -> Dict:
    """Fixture providing sample course data"""
    import time
    return {
        "name": f"Introduction to Testing {int(time.time() * 1000)}",
        "description": "Learn testing best practices",
        "instructor": "Dr. Test Master"
    }


class TestCourseEndpoints:
    """Test course CRUD operations"""

    def test_create_course_success(self, api_client, sample_course_data):
        """Test successful course creation"""
        response = requests.post(f"{api_client}/courses/", json=sample_course_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_course_data["name"]
        assert data["description"] == sample_course_data["description"]
        assert data["instructor"] == sample_course_data["instructor"]
        assert "id" in data

    def test_create_course_invalid_data(self, api_client):
        """Test creating course with missing required fields"""
        invalid_data = {"name": "Incomplete Course"}
        response = requests.post(f"{api_client}/courses/", json=invalid_data)
        assert response.status_code == 422

    def test_create_course_minimal_data(self, api_client):
        """Test creating course with only required fields"""
        import time
        minimal_data = {
            "name": f"Minimal Course {int(time.time() * 1000)}",
            "instructor": "Test Instructor"
        }
        response = requests.post(f"{api_client}/courses/", json=minimal_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == minimal_data["name"]
        assert data["instructor"] == minimal_data["instructor"]
        assert data["description"] is None  # Optional field

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
        assert data["name"] == sample_course_data["name"]

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
        assert data["name"] == sample_course_data["name"]  # Name unchanged

    def test_update_course_partial(self, api_client, sample_course_data):
        """Test partial update of course information"""
        # Create a course
        create_response = requests.post(f"{api_client}/courses/", json=sample_course_data)
        course_id = create_response.json()["id"]

        # Update only description
        update_data = {"description": "Updated course description"}
        response = requests.put(f"{api_client}/courses/{course_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == update_data["description"]
        assert data["name"] == sample_course_data["name"]  # Other fields unchanged

    def test_update_course_not_found(self, api_client):
        """Test updating non-existent course returns 404"""
        update_data = {"name": "Non-existent Course"}
        response = requests.put(f"{api_client}/courses/999999", json=update_data)
        assert response.status_code == 404

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

    def test_delete_course_not_found(self, api_client):
        """Test deleting non-existent course returns 404"""
        response = requests.delete(f"{api_client}/courses/999999")
        assert response.status_code == 404

    def test_get_course_students(self, api_client, sample_course_data):
        """Test getting all students in a course"""
        # Create course
        course_response = requests.post(f"{api_client}/courses/", json=sample_course_data)
        course_id = course_response.json()["id"]

        # Create student via auth
        import time
        import random
        student_email = f"enrollment.test.{int(time.time() * 1000)}.{random.randint(1000, 9999)}@example.com"
        login_data = {
            "email": student_email,
            "password": "testpass123",
            "role": "student"
        }
        login_response = requests.post(f"{api_client}/auth/login", json=login_data)
        student_id = login_response.json()["user"]["id"]

        # Enroll student in course
        enrollment_data = {"student_id": student_id, "course_id": course_id}
        enrollment_response = requests.post(f"{api_client}/enrollments/", json=enrollment_data)
        assert enrollment_response.status_code == 201

        # Get course's students
        response = requests.get(f"{api_client}/courses/{course_id}/students")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert any(student["id"] == student_id for student in data)

    def test_get_course_students_empty(self, api_client, sample_course_data):
        """Test getting students for course with no enrollments"""
        # Create course
        course_response = requests.post(f"{api_client}/courses/", json=sample_course_data)
        course_id = course_response.json()["id"]

        # Get course's students (should be empty)
        response = requests.get(f"{api_client}/courses/{course_id}/students")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0


if __name__ == "__main__":
    print("Run course tests with: pytest test/test_courses.py -v")
    print("For detailed output: pytest test/test_courses.py -v -s")
