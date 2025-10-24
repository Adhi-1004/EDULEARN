#!/usr/bin/env python3
"""
Test password hashing consistency
"""
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.models.models import UserModel
from app.utils.auth_utils import get_password_hash, verify_password

def test_password_hashing():
    """Test password hashing consistency"""
    print("Testing password hashing consistency...")
    
    test_password = "student23"
    
    # Test UserModel methods
    print(f"\n🧪 Testing UserModel methods:")
    hash1 = UserModel.hash_password(test_password)
    verify1 = UserModel.verify_password(test_password, hash1)
    print(f"   Hash: {hash1[:30]}...")
    print(f"   Verification: {verify1}")
    
    # Test auth_utils methods
    print(f"\n🧪 Testing auth_utils methods:")
    hash2 = get_password_hash(test_password)
    verify2 = verify_password(test_password, hash2)
    print(f"   Hash: {hash2[:30]}...")
    print(f"   Verification: {verify2}")
    
    # Test cross-verification
    print(f"\n🧪 Testing cross-verification:")
    cross_verify1 = UserModel.verify_password(test_password, hash2)
    cross_verify2 = verify_password(test_password, hash1)
    print(f"   UserModel.verify_password with auth_utils hash: {cross_verify1}")
    print(f"   verify_password with UserModel hash: {cross_verify2}")
    
    # Test with different passwords
    print(f"\n🧪 Testing with different passwords:")
    wrong_verify1 = UserModel.verify_password("wrongpassword", hash1)
    wrong_verify2 = verify_password("wrongpassword", hash2)
    print(f"   UserModel with wrong password: {wrong_verify1}")
    print(f"   auth_utils with wrong password: {wrong_verify2}")
    
    if verify1 and verify2 and cross_verify1 and cross_verify2 and not wrong_verify1 and not wrong_verify2:
        print(f"\n✅ All password tests passed!")
        return True
    else:
        print(f"\n❌ Some password tests failed!")
        return False

if __name__ == "__main__":
    test_password_hashing()
