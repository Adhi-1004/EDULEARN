"""
Test script to verify the coding platform setup
Run this to ensure Judge0 integration and coding endpoints work correctly
"""
import asyncio
import os
from dotenv import load_dotenv
from services.judge0_execution_service import judge0_execution_service

load_dotenv()

async def test_judge0_connection():
    """Test basic Judge0 API connection"""
    print("🧪 Testing Judge0 API Connection...")
    print(f"API Host: {os.getenv('JUDGE0_API_HOST')}")
    print(f"API Key configured: {'✅ Yes' if os.getenv('JUDGE0_API_KEY') else '❌ No'}")
    
    if not os.getenv('JUDGE0_API_KEY') or os.getenv('JUDGE0_API_KEY') == 'your-judge0-api-key':
        print("\n⚠️  WARNING: Judge0 API key not configured!")
        print("Please update JUDGE0_API_KEY in your .env file")
        print("Get your key from: https://rapidapi.com/judge0-official/api/judge0-ce")
        return False
    
    print("\n✅ Judge0 configuration looks good!")
    return True

def test_python_execution():
    """Test Python code execution"""
    print("\n🐍 Testing Python Code Execution...")
    
    code = """
def solution(nums):
    return sum(nums)

# Test
result = solution([1, 2, 3, 4, 5])
print(result)
"""
    
    test_cases = [
        {"input": [1, 2, 3, 4, 5], "output": "15"},
        {"input": [10, 20, 30], "output": "60"},
    ]
    
    try:
        results = judge0_execution_service.run_tests("python", code, test_cases)
        
        print(f"\nTotal test cases: {len(results)}")
        passed = sum(1 for r in results if r.get('passed'))
        print(f"Passed: {passed}/{len(results)}")
        
        for i, result in enumerate(results):
            status = "✅ PASSED" if result.get('passed') else "❌ FAILED"
            print(f"\nTest {i+1}: {status}")
            print(f"  Input: {result.get('input')}")
            print(f"  Expected: {result.get('expected')}")
            print(f"  Output: {result.get('output')}")
            if result.get('error'):
                print(f"  Error: {result.get('error')}")
            print(f"  Time: {result.get('execution_time')}ms")
        
        return passed == len(results)
    
    except Exception as e:
        print(f"\n❌ Error during execution: {str(e)}")
        return False

def test_javascript_execution():
    """Test JavaScript code execution"""
    print("\n🟨 Testing JavaScript Code Execution...")
    
    code = """
function solution(nums) {
    return nums.reduce((a, b) => a + b, 0);
}

// Test
console.log(solution([1, 2, 3, 4, 5]));
"""
    
    test_cases = [
        {"input": [1, 2, 3, 4, 5], "output": "15"},
    ]
    
    try:
        results = judge0_execution_service.run_tests("javascript", code, test_cases)
        passed = sum(1 for r in results if r.get('passed'))
        print(f"Passed: {passed}/{len(results)}")
        return passed == len(results)
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

async def main():
    """Run all tests"""
    print("=" * 60)
    print("🚀 CODING PLATFORM TEST SUITE")
    print("=" * 60)
    
    # Test 1: Check configuration
    config_ok = await test_judge0_connection()
    
    if not config_ok:
        print("\n" + "=" * 60)
        print("❌ SETUP INCOMPLETE")
        print("=" * 60)
        print("\nPlease configure Judge0 API key before testing execution.")
        return
    
    # Test 2: Python execution
    python_ok = test_python_execution()
    
    # Test 3: JavaScript execution
    js_ok = test_javascript_execution()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Configuration: {'✅ PASS' if config_ok else '❌ FAIL'}")
    print(f"Python Execution: {'✅ PASS' if python_ok else '❌ FAIL'}")
    print(f"JavaScript Execution: {'✅ PASS' if js_ok else '❌ FAIL'}")
    
    if config_ok and python_ok and js_ok:
        print("\n🎉 All tests passed! Your coding platform is ready!")
        print("\nNext steps:")
        print("1. Start the backend: python start_server.py")
        print("2. Start the frontend: cd frontend && npm run dev")
        print("3. Login as a student")
        print("4. Go to Assessment Choice → Coding Challenge")
        print("5. Generate a problem and start coding!")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        print("\nTroubleshooting:")
        print("1. Verify JUDGE0_API_KEY in .env file")
        print("2. Check your RapidAPI subscription status")
        print("3. Ensure you have internet connectivity")
        print("4. Check if you've exceeded free tier limits (50 requests/day)")
    
    print("=" * 60)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()

