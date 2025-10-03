"""
Test script to verify role-based access control implementation
"""

import requests
import json

# Base URL for the backend
BASE_URL = "http://localhost:5001"

def test_role_based_access():
    """Test role-based access control"""
    
    print("Testing role-based access control implementation...")
    
    # Initialize tokens
    student_token = None
    teacher_token = None
    admin_token = None
    
    # Test 1: Register users with different roles
    print("\n1. Testing user registration with roles...")
    
    # Register a student
    student_data = {
        "name": "Test Student",
        "email": "student@test.com",
        "password": "testpassword",
        "role": "student"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=student_data)
        if response.status_code == 200:
            print("✓ Student registration successful")
            student_token = response.json().get("access_token")
        else:
            print(f"✗ Student registration failed: {response.text}")
    except Exception as e:
        print(f"✗ Student registration error: {e}")
    
    # Register a teacher
    teacher_data = {
        "name": "Test Teacher",
        "email": "teacher@test.com",
        "password": "testpassword",
        "role": "teacher"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=teacher_data)
        if response.status_code == 200:
            print("✓ Teacher registration successful")
            teacher_token = response.json().get("access_token")
        else:
            print(f"✗ Teacher registration failed: {response.text}")
    except Exception as e:
        print(f"✗ Teacher registration error: {e}")
    
    # Register an admin
    admin_data = {
        "name": "Test Admin",
        "email": "admin@test.com",
        "password": "testpassword",
        "role": "admin"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=admin_data)
        if response.status_code == 200:
            print("✓ Admin registration successful")
            admin_token = response.json().get("access_token")
        else:
            print(f"✗ Admin registration failed: {response.text}")
    except Exception as e:
        print(f"✗ Admin registration error: {e}")
    
    # Test 2: Login users with different roles
    print("\n2. Testing user login...")
    
    # Login as student
    login_data = {
        "email": "student@test.com",
        "password": "testpassword"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            print("✓ Student login successful")
            student_response = response.json()
            print(f"  Role: {student_response.get('user', {}).get('role', 'N/A')}")
        else:
            print(f"✗ Student login failed: {response.text}")
    except Exception as e:
        print(f"✗ Student login error: {e}")
    
    # Login as teacher
    login_data = {
        "email": "teacher@test.com",
        "password": "testpassword"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            print("✓ Teacher login successful")
            teacher_response = response.json()
            print(f"  Role: {teacher_response.get('user', {}).get('role', 'N/A')}")
        else:
            print(f"✗ Teacher login failed: {response.text}")
    except Exception as e:
        print(f"✗ Teacher login error: {e}")
    
    # Login as admin
    login_data = {
        "email": "admin@test.com",
        "password": "testpassword"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            print("✓ Admin login successful")
            admin_response = response.json()
            print(f"  Role: {admin_response.get('user', {}).get('role', 'N/A')}")
        else:
            print(f"✗ Admin login failed: {response.text}")
    except Exception as e:
        print(f"✗ Admin login error: {e}")
    
    # Test 3: Check authentication status
    print("\n3. Testing authentication status...")
    
    headers = {"Authorization": f"Bearer {student_token}"}
    try:
        response = requests.get(f"{BASE_URL}/auth/status", headers=headers)
        if response.status_code == 200:
            status_data = response.json()
            if status_data.get("isAuthenticated"):
                user_role = status_data.get("user", {}).get("role", "N/A")
                print(f"✓ Student authentication status check successful (Role: {user_role})")
            else:
                print("✗ Student not authenticated")
        else:
            print(f"✗ Student authentication status check failed: {response.text}")
    except Exception as e:
        print(f"✗ Student authentication status check error: {e}")
    
    print("\nRole-based access control testing completed!")

if __name__ == "__main__":
    test_role_based_access()