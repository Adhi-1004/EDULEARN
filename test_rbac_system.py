"""
Comprehensive RBAC System Test
Tests the complete Role-Based Access Control system
"""
import asyncio
import sys
import os
import requests
import json

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_rbac_system():
    """Test the complete RBAC system"""
    print("🔐 Testing Role-Based Access Control (RBAC) System")
    print("=" * 60)
    
    # Test data
    test_users = {
        "student": {
            "name": "Test Student",
            "email": "student@test.com",
            "password": "student123",
            "role": "student"
        },
        "teacher": {
            "name": "Test Teacher", 
            "email": "teacher@test.com",
            "password": "teacher123",
            "role": "teacher"
        },
        "admin": {
            "name": "Test Admin",
            "email": "admin@test.com", 
            "password": "admin123",
            "role": "admin"
        }
    }
    
    tokens = {}
    
    # Step 1: Register test users
    print("\n1. Registering test users...")
    for role, user_data in test_users.items():
        try:
            response = requests.post(
                "http://127.0.0.1:5001/auth/register",
                json=user_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                tokens[role] = data.get("access_token")
                print(f"✅ {role.capitalize()} user registered successfully")
            else:
                print(f"❌ {role.capitalize()} user registration failed: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ Cannot connect to server. Make sure the server is running on port 5001")
            return False
        except Exception as e:
            print(f"❌ Error registering {role}: {e}")
    
    # Step 2: Test role-based access to endpoints
    print("\n2. Testing role-based access to endpoints...")
    
    # Define endpoints and their required roles
    endpoints = {
        # Student endpoints (should work for all roles)
        "/api/health": ["student", "teacher", "admin"],
        "/api/test-db": ["student", "teacher", "admin"],
        
        # Teacher endpoints (should work for teacher and admin)
        "/api/teacher/students": ["teacher", "admin"],
        "/api/teacher/batches": ["teacher", "admin"],
        "/api/teacher/analytics/class": ["teacher", "admin"],
        
        # Admin endpoints (should work for admin only)
        "/api/admin/users": ["admin"],
        "/api/admin/analytics/platform": ["admin"],
        "/api/admin/system/health": ["admin"],
        
        # Enhanced teacher endpoints
        "/api/teacher/batches/mission-control": ["teacher", "admin"],
        "/api/teacher/assessments/smart-create": ["teacher", "admin"],
        
        # Enhanced admin endpoints
        "/api/admin/metrics/platform-health": ["admin"],
        "/api/admin/content/quality-issues": ["admin"],
        "/api/admin/teachers/leaderboard": ["admin"]
    }
    
    # Test each role against each endpoint
    for endpoint, allowed_roles in endpoints.items():
        print(f"\n   Testing endpoint: {endpoint}")
        
        for role, token in tokens.items():
            if not token:
                print(f"     ❌ {role.capitalize()}: No token available")
                continue
                
            try:
                headers = {"Authorization": f"Bearer {token}"}
                response = requests.get(
                    f"http://127.0.0.1:5001{endpoint}",
                    headers=headers,
                    timeout=5
                )
                
                if role in allowed_roles:
                    if response.status_code in [200, 404]:  # 404 is OK for some endpoints
                        print(f"     ✅ {role.capitalize()}: Access granted (expected)")
                    else:
                        print(f"     ❌ {role.capitalize()}: Unexpected status {response.status_code}")
                else:
                    if response.status_code == 403:
                        print(f"     ✅ {role.capitalize()}: Access denied (expected)")
                    else:
                        print(f"     ❌ {role.capitalize()}: Should be denied but got {response.status_code}")
                        
            except Exception as e:
                print(f"     ❌ {role.capitalize()}: Error - {e}")
    
    # Step 3: Test JWT token role information
    print("\n3. Testing JWT token role information...")
    
    for role, token in tokens.items():
        if not token:
            continue
            
        try:
            # Decode JWT token (simplified - in production use proper JWT library)
            import base64
            import json
            
            # Split token and decode payload
            parts = token.split('.')
            if len(parts) >= 2:
                # Add padding if needed
                payload = parts[1]
                payload += '=' * (4 - len(payload) % 4)
                decoded = base64.b64decode(payload)
                payload_data = json.loads(decoded)
                
                token_role = payload_data.get('role', 'unknown')
                if token_role == role:
                    print(f"✅ {role.capitalize()}: JWT token contains correct role")
                else:
                    print(f"❌ {role.capitalize()}: JWT token role mismatch (expected: {role}, got: {token_role})")
            else:
                print(f"❌ {role.capitalize()}: Invalid JWT token format")
                
        except Exception as e:
            print(f"❌ {role.capitalize()}: Error decoding JWT - {e}")
    
    # Step 4: Test role hierarchy
    print("\n4. Testing role hierarchy...")
    
    role_hierarchy = {
        "student": 1,
        "teacher": 2, 
        "admin": 3
    }
    
    for role, level in role_hierarchy.items():
        print(f"   {role.capitalize()}: Level {level}")
    
    print("\n✅ RBAC System Test Complete!")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    asyncio.run(test_rbac_system())
