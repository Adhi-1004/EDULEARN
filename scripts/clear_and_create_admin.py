#!/usr/bin/env python3
"""
Clear existing user and create fresh admin user
"""
import requests
import json

def clear_and_create_admin():
    """Clear existing user and create fresh admin"""
    print("Clearing existing user and creating fresh admin...")
    
    # Step 1: Try to login with the existing user to see what happens
    print("\nStep 1: Testing existing user login...")
    try:
        body = {
            "email": "adhiadmin@gmail.com",
            "password": "admin123"
        }
        
        response = requests.post(
            "http://localhost:5001/auth/login",
            json=body,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("SUCCESS! Existing user login works!")
            data = response.json()
            print(f"   User Role: {data.get('user', {}).get('role', 'N/A')}")
            print(f"   Is Admin: {data.get('user', {}).get('is_admin', 'N/A')}")
            return True
        else:
            print(f"Existing user login failed: {response.text}")
            
    except Exception as e:
        print(f"Error testing existing user: {str(e)}")
    
    # Step 2: Create a completely new admin user with different email
    print("\nStep 2: Creating new admin user with fresh email...")
    try:
        body = {
            "username": "Adhithya",
            "email": "adhithya.admin@modlrn.com", 
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
            print("SUCCESS! New admin user created!")
            data = response.json()
            print(f"   Email: adhithya.admin@modlrn.com")
            print(f"   Password: admin123")
            print(f"   Role: {data.get('user', {}).get('role', 'N/A')}")
            print(f"   Is Admin: {data.get('user', {}).get('is_admin', 'N/A')}")
            
            # Test the login immediately
            print("\nStep 3: Testing new admin login...")
            login_body = {
                "email": "adhithya.admin@modlrn.com",
                "password": "admin123"
            }
            
            login_response = requests.post(
                "http://localhost:5001/auth/login",
                json=login_body,
                headers={"Content-Type": "application/json"}
            )
            
            if login_response.status_code == 200:
                print("SUCCESS! New admin login works perfectly!")
                login_data = login_response.json()
                print(f"   Access Token: {login_data.get('access_token', 'N/A')[:50]}...")
                print(f"   User Role: {login_data.get('user', {}).get('role', 'N/A')}")
                print(f"   Is Admin: {login_data.get('user', {}).get('is_admin', 'N/A')}")
                
                print("\n" + "="*60)
                print("ADMIN LOGIN CREDENTIALS:")
                print("="*60)
                print("Email: adhithya.admin@modlrn.com")
                print("Password: admin123")
                print("Role: admin")
                print("="*60)
                return True
            else:
                print(f"New admin login failed: {login_response.text}")
                return False
        else:
            print(f"Failed to create new admin: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error creating new admin: {str(e)}")
        return False

if __name__ == "__main__":
    clear_and_create_admin()
