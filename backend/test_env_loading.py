#!/usr/bin/env python3
"""
Test script to verify .env file loading
"""
import os
import sys
from dotenv import load_dotenv

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

print("=" * 60)
print("Testing .env File Loading")
print("=" * 60)

# Check working directory
print(f"\n1. Current Working Directory:")
print(f"   {os.getcwd()}")

# Check if .env file exists
env_file_path = os.path.join(script_dir, ".env")
print(f"\n2. .env File Exists:")
print(f"   {os.path.exists('.env')}")
print(f"   Full path: {env_file_path}")

# Load .env file
print(f"\n3. Loading .env file...")
load_dotenv()

# Check HACKEREARTH_CLIENT_SECRET
print(f"\n4. HACKEREARTH_CLIENT_SECRET Value:")
secret = os.getenv("HACKEREARTH_CLIENT_SECRET")
if secret:
    print(f"   [OK] Set: Yes")
    print(f"   Length: {len(secret)} characters")
    print(f"   First 10 chars: {secret[:10]}...")
    print(f"   Last 10 chars: ...{secret[-10:]}")
    print(f"   Full value: {secret}")
else:
    print(f"   [ERROR] Set: No (None or empty)")

# Also check from .env file directly
print(f"\n5. Reading .env file directly:")
if os.path.exists('.env'):
    with open('.env', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            if 'HACKEREARTH_CLIENT_SECRET' in line:
                print(f"   Found in .env: {line.strip()}")
                break
        else:
            print(f"   [WARNING] HACKEREARTH_CLIENT_SECRET not found in .env file")

print("\n" + "=" * 60)
print("Test Complete")
print("=" * 60)

