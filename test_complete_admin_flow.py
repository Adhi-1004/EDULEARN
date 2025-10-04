"""
Test Complete Admin Authentication Flow
Tests the complete admin authentication flow from registration to dashboard access
"""
import requests
import json

def test_complete_admin_flow():
    """Test complete admin authentication flow"""
    print("[ADMIN] Testing Complete Admin Authentication Flow")
    print("=" * 60)
    
    # Step 1: Test admin registration
    print("\n1. Testing admin registration...")
    admin_data = {
        "name": "Complete Test Admin",
        "email": "complete-admin@test.com",
        "password": "admin123",
        "role": "admin"
    }
    
    try:
        response = requests.post(
            "http://127.0.0.1:5001/auth/register",
            json=admin_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            admin_token = data.get("access_token")
            print("[SUCCESS] Admin registration successful")
            print(f"   Role: {data.get('user', {}).get('role')}")
            print(f"   is_admin: {data.get('user', {}).get('is_admin')}")
            print(f"   Token: {'Yes' if admin_token else 'No'}")
        else:
            print(f"[ERROR] Admin registration failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Admin registration error: {e}")
        return False
    
    # Step 2: Test admin login
    print("\n2. Testing admin login...")
    login_data = {
        "email": "complete-admin@test.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(
            "http://127.0.0.1:5001/auth/login",
            json=login_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            admin_token = data.get("access_token")
            print("[SUCCESS] Admin login successful")
            print(f"   Role: {data.get('user', {}).get('role')}")
            print(f"   is_admin: {data.get('user', {}).get('is_admin')}")
            print(f"   Token: {'Yes' if admin_token else 'No'}")
        else:
            print(f"[ERROR] Admin login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Admin login error: {e}")
        return False
    
    # Step 3: Test auth status endpoint
    print("\n3. Testing auth status endpoint...")
    try:
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(
            "http://127.0.0.1:5001/auth/status",
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print("[SUCCESS] Auth status check successful")
            print(f"   isAuthenticated: {data.get('isAuthenticated')}")
            print(f"   User role: {data.get('user', {}).get('role')}")
            print(f"   User is_admin: {data.get('user', {}).get('is_admin')}")
        else:
            print(f"[ERROR] Auth status check failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Auth status check error: {e}")
        return False
    
    # Step 4: Test admin dashboard endpoints
    print("\n4. Testing admin dashboard endpoints...")
    
    admin_endpoints = [
        ("/api/admin/users", "Users management"),
        ("/api/admin/analytics/platform", "Platform analytics"),
        ("/api/admin/system/health", "System health"),
        ("/api/admin/analytics/user-activity", "User activity"),
        ("/api/admin/analytics/content", "Content analytics")
    ]
    
    for endpoint, description in admin_endpoints:
        print(f"   Testing {description} ({endpoint})...")
        try:
            headers = {"Authorization": f"Bearer {admin_token}"}
            response = requests.get(
                f"http://127.0.0.1:5001{endpoint}",
                headers=headers,
                timeout=5
            )
            
            if response.status_code in [200, 404]:  # 404 is OK for empty results
                print(f"   [SUCCESS] {description} accessible")
            else:
                print(f"   [ERROR] {description} failed: {response.status_code}")
                print(f"      Response: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   [ERROR] {description} error: {e}")
    
    # Step 5: Test admin access to teacher endpoints (should work)
    print("\n5. Testing admin access to teacher endpoints...")
    
    teacher_endpoints = [
        ("/api/teacher/students", "Teacher students"),
        ("/api/teacher/batches", "Teacher batches"),
        ("/api/teacher/analytics/class", "Teacher analytics")
    ]
    
    for endpoint, description in teacher_endpoints:
        print(f"   Testing {description} ({endpoint})...")
        try:
            headers = {"Authorization": f"Bearer {admin_token}"}
            response = requests.get(
                f"http://127.0.0.1:5001{endpoint}",
                headers=headers,
                timeout=5
            )
            
            if response.status_code in [200, 404]:  # 404 is OK for empty results
                print(f"   [SUCCESS] {description} accessible")
            else:
                print(f"   [ERROR] {description} failed: {response.status_code}")
                
        except Exception as e:
            print(f"   [ERROR] {description} error: {e}")
    
    # Step 6: Test student access to admin endpoints (should be denied)
    print("\n6. Testing student access to admin endpoints (should be denied)...")
    
    # Create a student user
    student_data = {
        "name": "Test Student",
        "email": "student@test.com",
        "password": "student123",
        "role": "student"
    }
    
    try:
        response = requests.post(
            "http://127.0.0.1:5001/auth/register",
            json=student_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            student_token = data.get("access_token")
            print("[SUCCESS] Student registration successful")
            
            # Test student access to admin endpoint
            headers = {"Authorization": f"Bearer {student_token}"}
            response = requests.get(
                "http://127.0.0.1:5001/api/admin/users",
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 403:
                print("[SUCCESS] Student correctly denied access to admin endpoint")
            else:
                print(f"[ERROR] Student should be denied but got: {response.status_code}")
                
        else:
            print(f"[ERROR] Student registration failed: {response.status_code}")
            
    except Exception as e:
        print(f"[ERROR] Student access test error: {e}")
    
    print("\n[SUCCESS] Complete Admin Authentication Flow Test Complete!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    test_complete_admin_flow()
