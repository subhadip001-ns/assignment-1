#!/usr/bin/env python3
"""
Simple script to test the Student Course Enrollment Portal API
Run this after starting the API server with: python main.py
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def print_response(response, title):
    """Pretty print API response"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")
    print()


def test_api():
    """Test all API endpoints"""
    
    print("🚀 Testing Student Course Enrollment Portal API")
    print(f"Base URL: {BASE_URL}\n")
    
    # Test health check
    response = requests.get(f"{BASE_URL}/health")
    print_response(response, "Health Check")
    
    # 1. Create students
    print("📝 Creating Students...")
    students = [
        {"name": "Alice Johnson", "email": "alice@example.com"},
        {"name": "Bob Smith", "email": "bob@example.com"},
        {"name": "Charlie Brown", "email": "charlie@example.com"}
    ]
    
    student_ids = []
    for student in students:
        response = requests.post(f"{BASE_URL}/students/", json=student)
        print_response(response, f"Create Student: {student['name']}")
        if response.status_code == 201:
            student_ids.append(response.json()["id"])
    
    # 2. Get all students
    response = requests.get(f"{BASE_URL}/students/")
    print_response(response, "Get All Students")
    
    # 3. Create courses
    print("📚 Creating Courses...")
    courses = [
        {
            "name": "Introduction to Computer Science",
            "description": "Learn the fundamentals of programming and computer science",
            "instructor": "Dr. Sarah Williams"
        },
        {
            "name": "Data Structures and Algorithms",
            "description": "Advanced programming concepts and algorithmic thinking",
            "instructor": "Prof. Michael Chen"
        },
        {
            "name": "Web Development",
            "description": "Build modern web applications with HTML, CSS, and JavaScript",
            "instructor": "Dr. Emily Davis"
        }
    ]
    
    course_ids = []
    for course in courses:
        response = requests.post(f"{BASE_URL}/courses/", json=course)
        print_response(response, f"Create Course: {course['name']}")
        if response.status_code == 201:
            course_ids.append(response.json()["id"])
    
    # 4. Get all courses
    response = requests.get(f"{BASE_URL}/courses/")
    print_response(response, "Get All Courses")
    
    # 5. Create enrollments
    print("🎓 Creating Enrollments...")
    if student_ids and course_ids:
        enrollments = [
            {"student_id": student_ids[0], "course_id": course_ids[0]},
            {"student_id": student_ids[0], "course_id": course_ids[1]},
            {"student_id": student_ids[1], "course_id": course_ids[0]},
            {"student_id": student_ids[1], "course_id": course_ids[2]},
            {"student_id": student_ids[2], "course_id": course_ids[1]},
        ]
        
        for enrollment in enrollments:
            response = requests.post(f"{BASE_URL}/enrollments/", json=enrollment)
            print_response(response, f"Enroll Student {enrollment['student_id']} in Course {enrollment['course_id']}")
    
    # 6. Get student's courses
    if student_ids:
        response = requests.get(f"{BASE_URL}/students/{student_ids[0]}/courses")
        print_response(response, f"Get Courses for Student {student_ids[0]}")
    
    # 7. Get course's students
    if course_ids:
        response = requests.get(f"{BASE_URL}/courses/{course_ids[0]}/students")
        print_response(response, f"Get Students in Course {course_ids[0]}")
    
    # 8. Get all enrollments
    response = requests.get(f"{BASE_URL}/enrollments/")
    print_response(response, "Get All Enrollments")
    
    # 9. Update a student
    if student_ids:
        update_data = {"name": "Alice Johnson-Smith"}
        response = requests.put(f"{BASE_URL}/students/{student_ids[0]}", json=update_data)
        print_response(response, f"Update Student {student_ids[0]}")
    
    # 10. Update a course
    if course_ids:
        update_data = {"instructor": "Dr. Sarah Williams, PhD"}
        response = requests.put(f"{BASE_URL}/courses/{course_ids[0]}", json=update_data)
        print_response(response, f"Update Course {course_ids[0]}")
    
    print("✅ API Testing Complete!")
    print("\n💡 For interactive API documentation, visit:")
    print(f"   Swagger UI: {BASE_URL}/docs")
    print(f"   ReDoc: {BASE_URL}/redoc\n")


if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the API server.")
        print("Make sure the server is running with: python main.py")
    except Exception as e:
        print(f"❌ Error: {e}")

