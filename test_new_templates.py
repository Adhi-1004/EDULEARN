#!/usr/bin/env python3

import json
import subprocess
import tempfile
import os

def test_python_template():
    """Test the new Python template format"""
    print("Testing Python Template...")

    # New sophisticated Python template
    python_code = '''# Complete the solve function below
# Input will be automatically parsed and passed to your function
def solve(input_data):
    # TODO: Implement your solution here
    # input_data contains the parsed input (array, string, number, etc.)
    # Return the result as specified in the problem
    # For array sum problem
    if isinstance(input_data, list):
        return sum(input_data)
    return input_data

# DO NOT MODIFY BELOW THIS LINE
# The code below handles input parsing and output printing automatically
import sys
import json

if __name__ == '__main__':
    # Read input from stdin
    input_str = sys.stdin.read().strip()

    # Parse input based on format
    try:
        input_data = json.loads(input_str)
    except:
        input_data = input_str

    # Call your function
    result = solve(input_data)

    # Print result
    print(json.dumps(result) if not isinstance(result, str) else result)
'''

    # Test with array input
    test_input = '[1, 2, 3, 4, 5]'

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(python_code)
        temp_file = f.name

    try:
        # Run the code
        result = subprocess.run(
            ['python', temp_file],
            input=test_input,
            text=True,
            capture_output=True,
            timeout=10
        )

        expected_output = '15'  # sum of [1,2,3,4,5]
        actual_output = result.stdout.strip()

        print(f"Input: {test_input}")
        print(f"Expected: {expected_output}")
        print(f"Actual: {actual_output}")
        print(f"Success: {actual_output == expected_output}")

        return actual_output == expected_output

    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        os.unlink(temp_file)

def test_javascript_template():
    """Test the new JavaScript template format"""
    print("\nTesting JavaScript Template...")

    js_code = '''// Complete the solve function below
// Input will be automatically parsed and passed to your function
function solve(inputData) {
    // TODO: Implement your solution here
    // inputData contains the parsed input (array, string, number, etc.)
    // Return the result as specified in the problem
    // For array sum problem
    if (Array.isArray(inputData)) {
        return inputData.reduce((sum, num) => sum + num, 0);
    }
    return inputData;
}

// DO NOT MODIFY BELOW THIS LINE
// The code below handles input parsing and output printing automatically
const fs = require('fs');
const input = fs.readFileSync(0, 'utf-8').trim();

let inputData;
try {
    inputData = JSON.parse(input);
} catch {
    inputData = input;
}

const result = solve(inputData);
console.log(typeof result === 'string' ? result : JSON.stringify(result));
'''

    test_input = '[1, 2, 3, 4, 5]'

    with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
        f.write(js_code)
        temp_file = f.name

    try:
        # Run the code
        result = subprocess.run(
            ['node', temp_file],
            input=test_input,
            text=True,
            capture_output=True,
            timeout=10
        )

        expected_output = '15'
        actual_output = result.stdout.strip()

        print(f"Input: {test_input}")
        print(f"Expected: {expected_output}")
        print(f"Actual: {actual_output}")
        print(f"Success: {actual_output == expected_output}")

        return actual_output == expected_output

    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        os.unlink(temp_file)

if __name__ == "__main__":
    print("Testing New Template Formats")
    print("=" * 40)

    python_success = test_python_template()
    js_success = test_javascript_template()

    print("\n" + "=" * 40)
    print(f"Python Template: {'PASS' if python_success else 'FAIL'}")
    print(f"JavaScript Template: {'PASS' if js_success else 'FAIL'}")

    if python_success and js_success:
        print("All template tests PASSED!")
    else:
        print("Some template tests FAILED!")
        exit(1)
