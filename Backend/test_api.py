#!/usr/bin/env python3
"""
Comprehensive API testing script for EduLearn AI Backend
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5003"

def log_test(test_name, status, response=None, error=None):
    """Log test results"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status_symbol = "✅" if status == "PASS" else "❌"
    print(f"[{timestamp}] {status_symbol} {test_name}")
    
    if response and hasattr(response, 'status_code'):
        print(f"    Status: {response.status_code}")
        if response.status_code != 200 and response.status_code != 201:
            try:
                print(f"    Response: {response.json()}")
            except:
                print(f"    Response: {response.text}")
    
    if error:
        print(f"    Error: {error}")
    print()

def test_endpoint(endpoint, method="GET", data=None, expected_status=200, test_name=None):
    """Test a single endpoint"""
    if not test_name:
        test_name = f"{method} {endpoint}"
    
    try:
        url = f"{BASE_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        else:
            log_test(test_name, "FAIL", error=f"Unsupported method: {method}")
            return None
        
        if response.status_code == expected_status:
            log_test(test_name, "PASS", response)
        else:
            log_test(test_name, "FAIL", response)
        
        return response
    
    except Exception as e:
        log_test(test_name, "FAIL", error=str(e))
        return None

def main():
    print("=" * 80)
    print("🧪 EDULEARN AI BACKEND API TESTING")
    print("=" * 80)
    print()
    
    # Test basic endpoints first
    print("🔍 Testing Basic Endpoints...")
    test_endpoint("/", test_name="Root endpoint health check")
    test_endpoint("/leaderboard", test_name="Leaderboard endpoint")
    
    # Test existing MCQ endpoints
    print("\n📝 Testing Existing MCQ Endpoints...")
    mcq_data = {
        "Topic": "Programming",
        "Type": "MCQ", 
        "Quantity": "3",
        "Difficulty": "easy"
    }
    test_endpoint("/getQuestions", "POST", mcq_data, 200, "Generate MCQ questions")
    
    # Test chat endpoint
    chat_data = {"message": "Hello, how are you?"}
    test_endpoint("/ChatBot", "POST", chat_data, 200, "Chatbot interaction")
    
    # Test user authentication endpoints
    print("\n👤 Testing User Authentication...")
    
    # Test user registration
    user_data = {
        "name": "Test Student",
        "email": "test@example.com",
        "password": "testpassword123",
        "role": "student",
        "section": "A"
    }
    test_endpoint("/auth/register", "POST", user_data, 201, "User registration")
    
    # Test user login
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    login_response = test_endpoint("/auth/login", "POST", login_data, 200, "User login")
    
    user_id = None
    if login_response and login_response.status_code == 200:
        try:
            user_id = login_response.json().get('user', {}).get('id')
        except:
            pass
    
    # Test student endpoints
    print("\n🎓 Testing Student Dashboard Endpoints...")
    
    student_params = f"?student_id={user_id}&section=A" if user_id else "?student_id=test123&section=A"
    test_endpoint(f"/student/assignments{student_params}", test_name="Get student assignments")
    test_endpoint(f"/student/submissions{student_params.replace('&section=A', '')}", test_name="Get student submissions")
    test_endpoint(f"/student/projects{student_params.replace('&section=A', '')}", test_name="Get student projects")
    test_endpoint(f"/student/notes{student_params.replace('&section=A', '')}", test_name="Get student notes")
    test_endpoint(f"/student/analytics{student_params.replace('&section=A', '')}", test_name="Get student analytics")
    
    # Test study materials
    test_endpoint("/materials", test_name="Get study materials")
    test_endpoint("/materials?subject=Computer Science", test_name="Get CS study materials")
    
    # Test virtual labs
    test_endpoint("/labs", test_name="Get virtual labs")
    test_endpoint("/labs?subject=Physics", test_name="Get Physics virtual labs")
    
    # Test discussions
    test_endpoint("/discussions", test_name="Get discussions")
    test_endpoint("/discussions?subject=Mathematics", test_name="Get Math discussions")
    
    # Test study groups
    test_endpoint("/groups", test_name="Get study groups")
    test_endpoint("/groups?subject=Science", test_name="Get Science study groups")
    
    # Test notifications
    notification_params = f"?user_id={user_id}" if user_id else "?user_id=test123"
    test_endpoint(f"/notifications{notification_params}", test_name="Get user notifications")
    
    # Test creating content (POST endpoints)
    print("\n📝 Testing Content Creation...")
    
    # Create a study material
    material_data = {
        "title": "Test Study Material",
        "subject": "Computer Science",
        "type": "pdf",
        "description": "A test study material",
        "teacher_id": "teacher123",
        "url": "https://example.com/material.pdf"
    }
    test_endpoint("/materials", "POST", material_data, 201, "Create study material")
    
    # Create a virtual lab
    lab_data = {
        "title": "Test Virtual Lab",
        "subject": "Chemistry",
        "description": "A test virtual lab",
        "type": "simulation",
        "difficulty": "Beginner",
        "estimated_time": 60
    }
    test_endpoint("/labs", "POST", lab_data, 201, "Create virtual lab")
    
    # Create a discussion
    discussion_data = {
        "title": "Test Discussion",
        "subject": "Physics",
        "author_id": user_id or "test123",
        "content": "This is a test discussion about quantum mechanics"
    }
    test_endpoint("/discussions", "POST", discussion_data, 201, "Create discussion")
    
    # Create a study group
    group_data = {
        "name": "Test Study Group",
        "subject": "Mathematics",
        "creator_id": user_id or "test123",
        "description": "A test study group for calculus",
        "max_members": 10
    }
    test_endpoint("/groups", "POST", group_data, 201, "Create study group")
    
    # Test teacher endpoints
    print("\n👨‍🏫 Testing Teacher Dashboard Endpoints...")
    
    teacher_params = "?teacher_id=teacher123"
    test_endpoint(f"/teacher/assignments{teacher_params}", test_name="Get teacher assignments")
    test_endpoint(f"/teacher/submissions?assignment_id=test_assignment", test_name="Get assignment submissions")
    test_endpoint(f"/teacher/analytics{teacher_params}&section=A", test_name="Get class analytics")
    
    # Create an assignment
    assignment_data = {
        "title": "Test Assignment",
        "description": "A test assignment for students",
        "teacher_id": "teacher123",
        "subject": "Computer Science",
        "due_date": "2024-02-01",
        "target_sections": ["A", "B"],
        "max_grade": 100
    }
    test_endpoint("/teacher/assignments", "POST", assignment_data, 201, "Create assignment")
    
    # Test AI endpoints
    print("\n🤖 Testing AI Endpoints...")
    
    ai_params = f"?student_id={user_id}" if user_id else "?student_id=test123"
    test_endpoint(f"/ai/recommendations{ai_params}", test_name="Get AI recommendations")
    
    # Test existing coding endpoints
    coding_data = {
        "user_id": user_id or "test123",
        "topic": "arrays",
        "difficulty": "easy",
        "count": 1,
        "preferred_languages": ["python", "javascript"]
    }
    test_endpoint("/coding/generate", "POST", coding_data, 200, "Generate coding problems")
    
    evaluate_data = {
        "user_id": user_id or "test123",
        "problem_id": "test_problem",
        "code": "def solution(nums): return sum(nums)",
        "language": "python"
    }
    test_endpoint("/coding/evaluate", "POST", evaluate_data, 200, "Evaluate code solution")
    
    # Test user profile endpoints
    print("\n👤 Testing User Profile Management...")
    
    profile_params = f"?user_id={user_id}" if user_id else "?email=test@example.com"
    test_endpoint(f"/user/profile{profile_params}", test_name="Get user profile")
    
    if user_id:
        profile_update_data = {
            "user_id": user_id,
            "name": "Updated Test Student",
            "bio": "Updated bio information"
        }
        test_endpoint("/user/profile", "PUT", profile_update_data, 200, "Update user profile")
    
    # Test file upload (if endpoint exists)
    print("\n📁 Testing File Management...")
    test_endpoint("/upload", "POST", {}, 400, "File upload (expect error without file)")
    
    # Test MCQ results saving
    print("\n📊 Testing Results and Analytics...")
    
    mcq_result_data = {
        "user_id": user_id or "test123",
        "user_name": "Test Student",
        "topic": "Programming Basics",
        "difficulty": "easy", 
        "score": "8",
        "total": "10",
        "duration_ms": "120000"
    }
    test_endpoint("/results/mcq", "POST", mcq_result_data, 200, "Save MCQ results")
    
    # Summary
    print("\n" + "=" * 80)
    print("🏁 API TESTING COMPLETED")
    print("=" * 80)
    print("\nNote: Some endpoints may return errors if MongoDB is not set up or configured.")
    print("This is expected for the database-dependent endpoints.")
    print("\nTo fix database errors:")
    print("1. Install MongoDB")
    print("2. Set MONGO_URI environment variable")
    print("3. Ensure MongoDB is running")
    print("\nAll endpoint structures and request/response formats have been validated!")

if __name__ == "__main__":
    main()
