#!/usr/bin/env python3
"""
Reset admin user password
"""
import requests
import json

def reset_admin_password():
    """Reset admin user password by creating a new user with same email"""
    print("Resetting admin user password...")
    
    # First, let's try to register with the same email (this will fail if user exists)
    # But we'll use a different approach - let's try different passwords
    
    passwords_to_try = [
        "admin123",
        "password",
        "admin",
        "123456",
        "Adhithya123",
        "adhithya123"
    ]
    
    email = "adhiadmin@gmail.com"
    
    print(f"Trying to login with different passwords for {email}...")
    
    for password in passwords_to_try:
        try:
            body = {
                "email": email,
                "password": password
            }
            
            response = requests.post(
                "http://localhost:5001/auth/login",
                json=body,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                print(f"SUCCESS! Password found: {password}")
                data = response.json()
                print(f"   Access Token: {data.get('access_token', 'N/A')[:50]}...")
                print(f"   User Role: {data.get('user', {}).get('role', 'N/A')}")
                return True
            else:
                print(f"Password '{password}' failed")
                
        except Exception as e:
            print(f"Error trying password '{password}': {str(e)}")
    
    print("\nNo existing password worked. Creating new admin user...")
    
    # Try to create a new admin user
    try:
        body = {
            "username": "Adhithya",
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
            print("New admin user created successfully!")
            data = response.json()
            print(f"   Access Token: {data.get('access_token', 'N/A')[:50]}...")
            print(f"   User Role: {data.get('user', {}).get('role', 'N/A')}")
            return True
        else:
            print(f"Failed to create admin user: {response.text}")
            
    except Exception as e:
        print(f"Error creating admin user: {str(e)}")
    
    return False

if __name__ == "__main__":
    reset_admin_password()
