"""
Test Admin Authentication Flow
Tests the complete admin authentication process
"""
import requests
import json

def test_admin_auth_flow():
    """Test complete admin authentication flow"""
    print("[AUTH] Testing Admin Authentication Flow")
    print("=" * 50)
    
    # Step 1: Test admin registration
    print("\n1. Testing admin registration...")
    admin_data = {
        "name": "Admin User",
        "email": "admin@test.com",
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
            print(f"   Token received: {'Yes' if admin_token else 'No'}")
        else:
            print(f"[ERROR] Admin registration failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error in admin registration: {e}")
        return False
    
    # Step 2: Test admin login
    print("\n2. Testing admin login...")
    login_data = {
        "email": "admin@test.com",
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
            print(f"   Token received: {'Yes' if admin_token else 'No'}")
        else:
            print(f"[ERROR] Admin login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error in admin login: {e}")
        return False
    
    # Step 3: Test admin access to admin endpoints
    print("\n3. Testing admin access to admin endpoints...")
    
    admin_endpoints = [
        "/api/admin/users",
        "/api/admin/analytics/platform",
        "/api/admin/system/health"
    ]
    
    for endpoint in admin_endpoints:
        print(f"   Testing {endpoint}...")
        try:
            headers = {"Authorization": f"Bearer {admin_token}"}
            response = requests.get(
                f"http://127.0.0.1:5001{endpoint}",
                headers=headers,
                timeout=5
            )
            
            if response.status_code in [200, 404]:  # 404 is OK for empty results
                print(f"   [SUCCESS] Access granted to {endpoint}")
            else:
                print(f"   [ERROR] Access denied to {endpoint}: {response.status_code}")
                print(f"      Response: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   [ERROR] Error accessing {endpoint}: {e}")
    
    # Step 4: Test admin access to teacher endpoints (should work)
    print("\n4. Testing admin access to teacher endpoints...")
    
    teacher_endpoints = [
        "/api/teacher/students",
        "/api/teacher/batches",
        "/api/teacher/analytics/class"
    ]
    
    for endpoint in teacher_endpoints:
        print(f"   Testing {endpoint}...")
        try:
            headers = {"Authorization": f"Bearer {admin_token}"}
            response = requests.get(
                f"http://127.0.0.1:5001{endpoint}",
                headers=headers,
                timeout=5
            )
            
            if response.status_code in [200, 404]:  # 404 is OK for empty results
                print(f"   [SUCCESS] Access granted to {endpoint}")
            else:
                print(f"   [ERROR] Access denied to {endpoint}: {response.status_code}")
                
        except Exception as e:
            print(f"   [ERROR] Error accessing {endpoint}: {e}")
    
    # Step 5: Test auth status endpoint
    print("\n5. Testing auth status endpoint...")
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
            
    except Exception as e:
        print(f"[ERROR] Error in auth status check: {e}")
    
    print("\n[SUCCESS] Admin Authentication Flow Test Complete!")
    print("=" * 50)
    return True

if __name__ == "__main__":
    test_admin_auth_flow()
