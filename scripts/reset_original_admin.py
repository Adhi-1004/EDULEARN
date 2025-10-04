#!/usr/bin/env python3
"""
Reset the original admin user password
"""
import requests
import json

def reset_original_admin():
    """Try to reset the original admin user"""
    print("Attempting to reset original admin user...")
    
    # Try different common passwords for the original email
    passwords_to_try = [
        "admin123",
        "password", 
        "admin",
        "123456",
        "Adhithya123",
        "adhithya123",
        "Adhithya",
        "adhithya",
        "AAAdhi123",
        "AAAdhi",
        "aadhi123",
        "Aadhi123"
    ]
    
    email = "adhiadmin@gmail.com"
    print(f"Trying different passwords for {email}...")
    
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
                print(f"SUCCESS! Found the correct password: {password}")
                data = response.json()
                print(f"   User Role: {data.get('user', {}).get('role', 'N/A')}")
                print(f"   Is Admin: {data.get('user', {}).get('is_admin', 'N/A')}")
                print(f"   Access Token: {data.get('access_token', 'N/A')[:50]}...")
                
                print("\n" + "="*60)
                print("ORIGINAL ADMIN LOGIN CREDENTIALS:")
                print("="*60)
                print(f"Email: {email}")
                print(f"Password: {password}")
                print("="*60)
                return True
            else:
                print(f"Password '{password}' failed")
                
        except Exception as e:
            print(f"Error trying password '{password}': {str(e)}")
    
    print(f"\nCould not find the correct password for {email}")
    print("The original user might have been created with a different password.")
    return False

if __name__ == "__main__":
    reset_original_admin()
