"""
Test login functionality
"""
import requests
import json

def test_login():
    """Test login endpoint"""
    try:
        # Test data
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        print("Testing login endpoint...")
        print(f"Login data: {login_data}")
        
        # Try to connect to the server
        try:
            response = requests.post(
                "http://127.0.0.1:5001/auth/login",
                json=login_data,
                timeout=5
            )
            
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.json()}")
            
            if response.status_code == 200:
                print("[SUCCESS] Login endpoint is working!")
                return True
            else:
                print(f"[ERROR] Login failed with status {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            print("[ERROR] Cannot connect to server. Make sure the server is running on port 5001")
            return False
        except Exception as e:
            print(f"[ERROR] Request failed: {e}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        return False

def test_register():
    """Test register endpoint"""
    try:
        # Test data
        register_data = {
            "name": "Test User",
            "email": "newuser@example.com",
            "password": "newpassword123",
            "role": "student"
        }
        
        print("Testing register endpoint...")
        print(f"Register data: {register_data}")
        
        # Try to connect to the server
        try:
            response = requests.post(
                "http://127.0.0.1:5001/auth/register",
                json=register_data,
                timeout=5
            )
            
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.json()}")
            
            if response.status_code == 200:
                print("[SUCCESS] Register endpoint is working!")
                return True
            else:
                print(f"[ERROR] Register failed with status {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            print("[ERROR] Cannot connect to server. Make sure the server is running on port 5001")
            return False
        except Exception as e:
            print(f"[ERROR] Request failed: {e}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing modLRN Authentication Endpoints")
    print("=" * 50)
    
    print("\n1. Testing Login Endpoint:")
    login_success = test_login()
    
    print("\n2. Testing Register Endpoint:")
    register_success = test_register()
    
    print("\n" + "=" * 50)
    if login_success and register_success:
        print("[SUCCESS] All authentication endpoints are working!")
    else:
        print("[ERROR] Some authentication endpoints are not working.")
        print("Make sure the server is running: python start_server.bat")
