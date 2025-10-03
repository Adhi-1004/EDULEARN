"""
Test script to verify backend API endpoints for teacher and admin dashboards
"""

import requests
import json
import time

# Base URL for the backend
BASE_URL = "http://localhost:5001"

def register_test_users():
    """Register test users with different roles"""
    print("Registering test users...")
    
    users = [
        {
            "name": "Test Teacher",
            "email": "teacher@test.com",
            "password": "testpassword",
            "role": "teacher"
        },
        {
            "name": "Test Admin",
            "email": "admin@test.com",
            "password": "testpassword",
            "role": "admin"
        },
        {
            "name": "Test Student 1",
            "email": "student1@test.com",
            "password": "testpassword",
            "role": "student"
        },
        {
            "name": "Test Student 2",
            "email": "student2@test.com",
            "password": "testpassword",
            "role": "student"
        }
    ]
    
    tokens = {}
    
    for user_data in users:
        try:
            response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
            if response.status_code == 200:
                print(f"✓ {user_data['role'].title()} registration successful")
                tokens[user_data['role']] = response.json().get("access_token")
            else:
                print(f"✗ {user_data['role'].title()} registration failed: {response.text}")
        except Exception as e:
            print(f"✗ {user_data['role'].title()} registration error: {e}")
    
    return tokens

def test_teacher_endpoints(teacher_token):
    """Test teacher dashboard endpoints"""
    print("\nTesting Teacher Dashboard Endpoints...")
    
    headers = {"Authorization": f"Bearer {teacher_token}"}
    
    # Test 1: Get students
    print("1. Testing get students...")
    try:
        response = requests.get(f"{BASE_URL}/api/teacher/students", headers=headers)
        if response.status_code == 200:
            students = response.json()
            print(f"✓ Get students successful - Found {len(students)} students")
        else:
            print(f"✗ Get students failed: {response.text}")
    except Exception as e:
        print(f"✗ Get students error: {e}")
    
    # Test 2: Create batch
    print("2. Testing create batch...")
    batch_data = {
        "name": "Test Batch",
        "description": "A test batch for verification"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/teacher/batches", headers=headers, json=batch_data)
        if response.status_code == 200:
            batch = response.json()
            batch_id = batch.get("id")
            print(f"✓ Create batch successful - Batch ID: {batch_id}")
        else:
            print(f"✗ Create batch failed: {response.text}")
            batch_id = None
    except Exception as e:
        print(f"✗ Create batch error: {e}")
        batch_id = None
    
    # Test 3: Get batches
    print("3. Testing get batches...")
    try:
        response = requests.get(f"{BASE_URL}/api/teacher/batches", headers=headers)
        if response.status_code == 200:
            batches = response.json()
            print(f"✓ Get batches successful - Found {len(batches)} batches")
        else:
            print(f"✗ Get batches failed: {response.text}")
    except Exception as e:
        print(f"✗ Get batches error: {e}")
    
    # Test 4: Create assessment
    print("4. Testing create assessment...")
    assessment_data = {
        "title": "Test Assessment",
        "topic": "Mathematics",
        "difficulty": "medium",
        "question_count": 10,
        "description": "A test assessment"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/teacher/assessments", headers=headers, json=assessment_data)
        if response.status_code == 200:
            assessment = response.json()
            print(f"✓ Create assessment successful - Assessment ID: {assessment.get('id')}")
        else:
            print(f"✗ Create assessment failed: {response.text}")
    except Exception as e:
        print(f"✗ Create assessment error: {e}")
    
    # Test 5: Get assessments
    print("5. Testing get assessments...")
    try:
        response = requests.get(f"{BASE_URL}/api/teacher/assessments", headers=headers)
        if response.status_code == 200:
            assessments = response.json()
            print(f"✓ Get assessments successful - Found {len(assessments)} assessments")
        else:
            print(f"✗ Get assessments failed: {response.text}")
    except Exception as e:
        print(f"✗ Get assessments error: {e}")
    
    # Test 6: Get class analytics
    print("6. Testing get class analytics...")
    try:
        response = requests.get(f"{BASE_URL}/api/teacher/analytics/class", headers=headers)
        if response.status_code == 200:
            analytics = response.json()
            print(f"✓ Get class analytics successful")
        else:
            print(f"✗ Get class analytics failed: {response.text}")
    except Exception as e:
        print(f"✗ Get class analytics error: {e}")
    
    return batch_id

def test_admin_endpoints(admin_token):
    """Test admin dashboard endpoints"""
    print("\nTesting Admin Dashboard Endpoints...")
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Test 1: Get users
    print("1. Testing get users...")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/users", headers=headers)
        if response.status_code == 200:
            users_data = response.json()
            print(f"✓ Get users successful - Total users: {users_data.get('total', 0)}")
        else:
            print(f"✗ Get users failed: {response.text}")
    except Exception as e:
        print(f"✗ Get users error: {e}")
    
    # Test 2: Get platform stats
    print("2. Testing get platform stats...")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/analytics/platform", headers=headers)
        if response.status_code == 200:
            stats = response.json()
            print(f"✓ Get platform stats successful")
        else:
            print(f"✗ Get platform stats failed: {response.text}")
    except Exception as e:
        print(f"✗ Get platform stats error: {e}")
    
    # Test 3: Get user activity
    print("3. Testing get user activity...")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/analytics/users", headers=headers)
        if response.status_code == 200:
            activities = response.json()
            print(f"✓ Get user activity successful - Found {len(activities)} activities")
        else:
            print(f"✗ Get user activity failed: {response.text}")
    except Exception as e:
        print(f"✗ Get user activity error: {e}")
    
    # Test 4: Get content stats
    print("4. Testing get content stats...")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/analytics/content", headers=headers)
        if response.status_code == 200:
            content_stats = response.json()
            print(f"✓ Get content stats successful")
        else:
            print(f"✗ Get content stats failed: {response.text}")
    except Exception as e:
        print(f"✗ Get content stats error: {e}")
    
    # Test 5: System health check
    print("5. Testing system health check...")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/system/health", headers=headers)
        if response.status_code == 200:
            health = response.json()
            print(f"✓ System health check successful - Status: {health.get('status')}")
        else:
            print(f"✗ System health check failed: {response.text}")
    except Exception as e:
        print(f"✗ System health check error: {e}")

def test_unauthorized_access(tokens):
    """Test that users cannot access endpoints they're not authorized for"""
    print("\nTesting Unauthorized Access Prevention...")
    
    # Student trying to access teacher endpoints
    student_headers = {"Authorization": f"Bearer {tokens.get('student')}"}
    
    print("1. Testing student access to teacher endpoints...")
    try:
        response = requests.get(f"{BASE_URL}/api/teacher/students", headers=student_headers)
        if response.status_code == 403:
            print("✓ Student correctly denied access to teacher endpoints")
        else:
            print(f"✗ Student should be denied access but got: {response.status_code}")
    except Exception as e:
        print(f"✗ Student access test error: {e}")
    
    # Student trying to access admin endpoints
    print("2. Testing student access to admin endpoints...")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/users", headers=student_headers)
        if response.status_code == 403:
            print("✓ Student correctly denied access to admin endpoints")
        else:
            print(f"✗ Student should be denied access but got: {response.status_code}")
    except Exception as e:
        print(f"✗ Student access test error: {e}")
    
    # Teacher trying to access admin endpoints
    teacher_headers = {"Authorization": f"Bearer {tokens.get('teacher')}"}
    
    print("3. Testing teacher access to admin endpoints...")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/users", headers=teacher_headers)
        if response.status_code == 403:
            print("✓ Teacher correctly denied access to admin endpoints")
        else:
            print(f"✗ Teacher should be denied access but got: {response.status_code}")
    except Exception as e:
        print(f"✗ Teacher access test error: {e}")

def main():
    """Main test function"""
    print("Backend API Endpoints Testing")
    print("=" * 40)
    
    # Register test users
    tokens = register_test_users()
    
    if not tokens:
        print("Failed to register test users. Exiting...")
        return
    
    # Test teacher endpoints
    if tokens.get("teacher"):
        batch_id = test_teacher_endpoints(tokens["teacher"])
    
    # Test admin endpoints
    if tokens.get("admin"):
        test_admin_endpoints(tokens["admin"])
    
    # Test unauthorized access prevention
    test_unauthorized_access(tokens)
    
    print("\n" + "=" * 40)
    print("Backend API Testing Complete!")

if __name__ == "__main__":
    main()