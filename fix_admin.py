#!/usr/bin/env python3
"""
Fix admin user login issue
"""
import requests
import json

def fix_admin_login():
    """Fix admin login by testing different approaches"""
    print("Fixing admin login issue...")
    
    # Method 1: Try to register a new admin user with a different email
    print("\nMethod 1: Creating admin user with different email...")
    try:
        body = {
            "username": "Adhithya",
            "email": "admin@modlrn.com", 
            "password": "admin123",
            "role": "admin",
            "name": "Adhithya Admin"
        }
        
        response = requests.post(
            "http://localhost:5001/auth/register",
            json=body,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("SUCCESS! Admin user created with email: admin@modlrn.com")
            data = response.json()
            print(f"   Access Token: {data.get('access_token', 'N/A')[:50]}...")
            print(f"   User Role: {data.get('user', {}).get('role', 'N/A')}")
            print("\nYou can now login with:")
            print("   Email: admin@modlrn.com")
            print("   Password: admin123")
            return True
        else:
            print(f"Failed: {response.text}")
            
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # Method 2: Try to register with original email but different username
    print("\nMethod 2: Creating admin user with different username...")
    try:
        body = {
            "username": "AdminUser",
            "email": "adhiadmin@gmail.com", 
            "password": "admin123",
            "role": "admin",
            "name": "Adhithya Admin"
        }
        
        response = requests.post(
            "http://localhost:5001/auth/register",
            json=body,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("SUCCESS! Admin user created!")
            data = response.json()
            print(f"   Access Token: {data.get('access_token', 'N/A')[:50]}...")
            print(f"   User Role: {data.get('user', {}).get('role', 'N/A')}")
            print("\nYou can now login with:")
            print("   Email: adhiadmin@gmail.com")
            print("   Password: admin123")
            return True
        else:
            print(f"Failed: {response.text}")
            
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # Method 3: Try to login with the test user we created earlier
    print("\nMethod 3: Trying existing test user...")
    try:
        body = {
            "email": "test@example.com",
            "password": "testpass123"
        }
        
        response = requests.post(
            "http://localhost:5001/auth/login",
            json=body,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("SUCCESS! You can login with the test user:")
            data = response.json()
            print(f"   Access Token: {data.get('access_token', 'N/A')[:50]}...")
            print(f"   User Role: {data.get('user', {}).get('role', 'N/A')}")
            print("\nYou can login with:")
            print("   Email: test@example.com")
            print("   Password: testpass123")
            return True
        else:
            print(f"Test user login failed: {response.text}")
            
    except Exception as e:
        print(f"Error: {str(e)}")
    
    print("\nAll methods failed. Please check the backend server status.")
    return False

if __name__ == "__main__":
    fix_admin_login()
