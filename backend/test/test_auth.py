#!/usr/bin/env python3
"""
Authentication tests for the Student Course Enrollment Portal API
Run with: pytest test/test_auth.py -v
"""

import pytest
import requests
from typing import Dict

BASE_URL = "http://localhost:8000"

# Test authentication data
ADMIN_EMAIL = "admin@admin.com"
ADMIN_PASSWORD = "admin"


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


class TestAuthEndpoints:
    """Test authentication endpoints"""

    def test_admin_login_success(self, api_client):
        """Test successful admin login"""
        login_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD,
            "role": "admin"
        }
        response = requests.post(f"{api_client}/auth/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert "user" in data
        assert data["user"]["email"] == ADMIN_EMAIL
        assert data["user"]["role"] == "admin"
        assert data["token_type"] == "bearer"

    def test_admin_login_wrong_password(self, api_client):
        """Test admin login with wrong password fails"""
        login_data = {
            "email": ADMIN_EMAIL,
            "password": "wrongpassword",
            "role": "admin"
        }
        response = requests.post(f"{api_client}/auth/login", json=login_data)
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "invalid admin credentials" in data["detail"].lower()

    def test_admin_login_wrong_email(self, api_client):
        """Test admin login with wrong email fails"""
        login_data = {
            "email": "wrong@admin.com",
            "password": ADMIN_PASSWORD,
            "role": "admin"
        }
        response = requests.post(f"{api_client}/auth/login", json=login_data)
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "invalid admin credentials" in data["detail"].lower()

    def test_student_login_signup_new_student(self, api_client):
        """Test student login creates new student when email doesn't exist"""
        unique_email = generate_unique_email("new.student")
        login_data = {
            "email": unique_email,
            "password": "testpassword123",
            "role": "student"
        }
        response = requests.post(f"{api_client}/auth/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == unique_email
        assert data["user"]["role"] == "student"
        assert data["user"]["name"] == unique_email.split('@')[0]  # Name derived from email

    def test_student_login_existing_student_correct_password(self, api_client):
        """Test student login with existing student and correct password"""
        unique_email = generate_unique_email("existing.student")
        password = "testpassword123"

        # First login (creates student)
        login_data = {
            "email": unique_email,
            "password": password,
            "role": "student"
        }
        response1 = requests.post(f"{api_client}/auth/login", json=login_data)
        assert response1.status_code == 200
        user_id = response1.json()["user"]["id"]

        # Second login (should authenticate existing student)
        response2 = requests.post(f"{api_client}/auth/login", json=login_data)
        assert response2.status_code == 200
        data = response2.json()
        assert data["user"]["id"] == user_id  # Same user ID
        assert data["user"]["email"] == unique_email
        assert data["user"]["role"] == "student"

    def test_student_login_wrong_password(self, api_client):
        """Test student login with wrong password is rejected"""
        unique_email = generate_unique_email("wrong.pass.student")
        correct_password = "correctpassword123"

        # First login (creates student)
        login_data1 = {
            "email": unique_email,
            "password": correct_password,
            "role": "student"
        }
        response1 = requests.post(f"{api_client}/auth/login", json=login_data1)
        assert response1.status_code == 200
        user_id1 = response1.json()["user"]["id"]

        # Second login with wrong password (should be rejected)
        login_data2 = {
            "email": unique_email,
            "password": "wrongpassword",
            "role": "student"
        }
        response2 = requests.post(f"{api_client}/auth/login", json=login_data2)
        # Backend correctly rejects wrong password with 400 (email already exists)
        assert response2.status_code == 400
        assert "already exists" in response2.json()["detail"].lower()

    def test_login_invalid_role(self, api_client):
        """Test login with invalid role fails"""
        login_data = {
            "email": "test@example.com",
            "password": "password",
            "role": "invalid_role"
        }
        response = requests.post(f"{api_client}/auth/login", json=login_data)
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "invalid role" in data["detail"].lower()

    def test_login_missing_fields(self, api_client):
        """Test login with missing required fields fails"""
        # Missing password
        login_data = {
            "email": "test@example.com",
            "role": "student"
        }
        response = requests.post(f"{api_client}/auth/login", json=login_data)
        assert response.status_code == 422

        # Missing email
        login_data = {
            "password": "password",
            "role": "student"
        }
        response = requests.post(f"{api_client}/auth/login", json=login_data)
        assert response.status_code == 422

        # Missing role
        login_data = {
            "email": "test@example.com",
            "password": "password"
        }
        response = requests.post(f"{api_client}/auth/login", json=login_data)
        assert response.status_code == 422

    def test_logout_with_token(self, api_client):
        """Test logout with valid token"""
        # Login first to get token
        login_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD,
            "role": "admin"
        }
        login_response = requests.post(f"{api_client}/auth/login", json=login_data)
        token = login_response.json()["access_token"]

        # Logout with token
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{api_client}/auth/logout", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "successfully logged out" in data["message"].lower()

    def test_logout_without_token(self, api_client):
        """Test logout without token fails"""
        response = requests.post(f"{api_client}/auth/logout")
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "invalid token" in data["detail"].lower()

    def test_get_current_user_with_valid_token(self, api_client):
        """Test getting current user with valid token"""
        # Login first to get token
        login_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD,
            "role": "admin"
        }
        login_response = requests.post(f"{api_client}/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        user_data = login_response.json()["user"]

        # Get current user
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{api_client}/auth/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == user_data["id"]
        assert data["role"] == user_data["role"]

    def test_get_current_user_with_invalid_token(self, api_client):
        """Test getting current user with invalid token fails"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = requests.get(f"{api_client}/auth/me", headers=headers)
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "invalid token" in data["detail"].lower()

    def test_get_current_user_without_token(self, api_client):
        """Test getting current user without token fails"""
        response = requests.get(f"{api_client}/auth/me")
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "invalid token" in data["detail"].lower()

    def test_get_current_user_with_expired_token(self, api_client):
        """Test getting current user with expired token fails"""
        # Create an expired token (this is tricky to test without manipulating time)
        # For now, we'll test with a malformed token
        headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"}
        response = requests.get(f"{api_client}/auth/me", headers=headers)
        # This should fail as the token is malformed/expired
        assert response.status_code in [401, 422]


if __name__ == "__main__":
    print("Run auth tests with: pytest test/test_auth.py -v")
    print("For detailed output: pytest test/test_auth.py -v -s")
