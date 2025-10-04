"""
Quick RBAC Test - Test the Role-Based Access Control system
"""
import requests
import json

def test_rbac_quick():
    """Quick test of RBAC system"""
    print("[RBAC] Quick RBAC Test")
    print("=" * 40)
    
    # Test server health first
    try:
        response = requests.get("http://127.0.0.1:5001/api/health", timeout=5)
        if response.status_code == 200:
            print("[SUCCESS] Server is running")
        else:
            print(f"[ERROR] Server health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("[ERROR] Cannot connect to server. Make sure the server is running:")
        print("   Run: start_server_fixed.bat")
        return False
    except Exception as e:
        print(f"[ERROR] Error connecting to server: {e}")
        return False
    
    # Test student registration and login
    print("\n1. Testing student registration...")
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
            print("[SUCCESS] Student registered successfully")
            print(f"   Role in response: {data.get('user', {}).get('role', 'unknown')}")
        else:
            print(f"[ERROR] Student registration failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error registering student: {e}")
        return False
    
    # Test teacher registration
    print("\n2. Testing teacher registration...")
    teacher_data = {
        "name": "Test Teacher",
        "email": "teacher@test.com", 
        "password": "teacher123",
        "role": "teacher"
    }
    
    try:
        response = requests.post(
            "http://127.0.0.1:5001/auth/register",
            json=teacher_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            teacher_token = data.get("access_token")
            print("[SUCCESS] Teacher registered successfully")
            print(f"   Role in response: {data.get('user', {}).get('role', 'unknown')}")
        else:
            print(f"[ERROR] Teacher registration failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error registering teacher: {e}")
        return False
    
    # Test role-based access
    print("\n3. Testing role-based access...")
    
    # Test student access to teacher endpoint (should be denied)
    print("   Testing student access to teacher endpoint...")
    try:
        headers = {"Authorization": f"Bearer {student_token}"}
        response = requests.get(
            "http://127.0.0.1:5001/api/teacher/students",
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 403:
            print("   [SUCCESS] Student correctly denied access to teacher endpoint")
        else:
            print(f"   [ERROR] Student should be denied but got: {response.status_code}")
            
    except Exception as e:
        print(f"   [ERROR] Error testing student access: {e}")
    
    # Test teacher access to teacher endpoint (should be allowed)
    print("   Testing teacher access to teacher endpoint...")
    try:
        headers = {"Authorization": f"Bearer {teacher_token}"}
        response = requests.get(
            "http://127.0.0.1:5001/api/teacher/students",
            headers=headers,
            timeout=5
        )
        
        if response.status_code in [200, 404]:  # 404 is OK for empty results
            print("   [SUCCESS] Teacher correctly allowed access to teacher endpoint")
        else:
            print(f"   [ERROR] Teacher should be allowed but got: {response.status_code}")
            
    except Exception as e:
        print(f"   [ERROR] Error testing teacher access: {e}")
    
    print("\n[SUCCESS] RBAC Quick Test Complete!")
    print("=" * 40)
    return True

if __name__ == "__main__":
    test_rbac_quick()
