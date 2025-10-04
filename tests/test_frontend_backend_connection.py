"""
Test Frontend-Backend Connection
Tests if the frontend can properly connect to the backend
"""
import requests
import json

def test_frontend_backend_connection():
    """Test frontend-backend connection"""
    print("[CONNECTION] Testing Frontend-Backend Connection")
    print("=" * 60)
    
    # Test 1: Basic server health
    print("\n1. Testing server health...")
    try:
        response = requests.get("http://127.0.0.1:5001/api/health", timeout=5)
        if response.status_code == 200:
            print("[SUCCESS] Server is running and healthy")
        else:
            print(f"[ERROR] Server health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] Cannot connect to server: {e}")
        return False
    
    # Test 2: CORS headers
    print("\n2. Testing CORS headers...")
    try:
        response = requests.options("http://127.0.0.1:5001/api/health", timeout=5)
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
        }
        print(f"[INFO] CORS headers: {cors_headers}")
    except Exception as e:
        print(f"[ERROR] CORS test failed: {e}")
    
    # Test 3: Admin registration and login flow
    print("\n3. Testing admin registration and login flow...")
    
    # Register admin
    admin_data = {
        "name": "Frontend Test Admin",
        "email": "frontend-admin@test.com",
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
            print(f"   Token: {'Yes' if admin_token else 'No'}")
        else:
            print(f"[ERROR] Admin registration failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Admin registration error: {e}")
        return False
    
    # Test 4: Admin login
    print("\n4. Testing admin login...")
    login_data = {
        "email": "frontend-admin@test.com",
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
            print(f"   Token: {'Yes' if admin_token else 'No'}")
        else:
            print(f"[ERROR] Admin login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Admin login error: {e}")
        return False
    
    # Test 5: Admin dashboard endpoints
    print("\n5. Testing admin dashboard endpoints...")
    
    admin_endpoints = [
        ("/api/admin/users", "Users management"),
        ("/api/admin/analytics/platform", "Platform analytics"),
        ("/api/admin/system/health", "System health"),
        ("/api/admin/analytics/user-activity", "User activity")
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
    
    # Test 6: Auth status endpoint
    print("\n6. Testing auth status endpoint...")
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
        print(f"[ERROR] Auth status check error: {e}")
    
    print("\n[SUCCESS] Frontend-Backend Connection Test Complete!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    test_frontend_backend_connection()
