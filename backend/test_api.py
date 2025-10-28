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

# Test authentication data
ADMIN_EMAIL = "admin@admin.com"
ADMIN_PASSWORD = "admin"


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


if __name__ == "__main__":
    print("Run tests with: pytest test_api.py -v")
    print("For detailed output: pytest test_api.py -v -s")
    print("To run specific test class:")
    print("  pytest test_api.py::TestHealthCheck -v")
    print("  pytest test_api.py::TestStudentEndpoints -v")
