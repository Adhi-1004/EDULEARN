#!/usr/bin/env python3
"""
Test script to verify HackerEarth service can load the client secret
"""
import os
import sys
from dotenv import load_dotenv

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

print("=" * 60)
print("Testing HackerEarth Service Configuration")
print("=" * 60)

# Load .env file first
load_dotenv()

print(f"\n1. Working Directory:")
print(f"   {os.getcwd()}")

print(f"\n2. Loading HackerEarth service module...")
try:
    # Import after load_dotenv()
    sys.path.insert(0, script_dir)
    from app.services.hackerearth_execution_service import HackerEarthExecutionService, HACKEREARTH_CLIENT_SECRET
    
    print(f"\n3. HACKEREARTH_CLIENT_SECRET from service module:")
    if HACKEREARTH_CLIENT_SECRET:
        print(f"   [OK] Set: Yes")
        print(f"   Length: {len(HACKEREARTH_CLIENT_SECRET)} characters")
        print(f"   First 10 chars: {HACKEREARTH_CLIENT_SECRET[:10]}...")
        print(f"   Full value: {HACKEREARTH_CLIENT_SECRET}")
    else:
        print(f"   [ERROR] Set: No (None or empty)")
    
    print(f"\n4. Creating HackerEarthExecutionService instance...")
    try:
        service = HackerEarthExecutionService()
        print(f"   [OK] Service instance created successfully")
        print(f"   Service headers client-secret: {service.headers.get('client-secret', 'Not set')[:10]}...")
    except ValueError as e:
        print(f"   [ERROR] Failed to create service: {e}")
    except Exception as e:
        print(f"   [ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        
except Exception as e:
    print(f"   [ERROR] Failed to import service: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Test Complete")
print("=" * 60)

