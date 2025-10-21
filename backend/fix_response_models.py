"""
Fix Response Models Script
Converts all response model classes to proper Pydantic BaseModel classes
"""
import os
import re
from pathlib import Path

def fix_response_models_in_file(file_path: str):
    """Fix response model classes in a single file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Track if any changes were made
    original_content = content
    
    # Add BaseModel import if not present
    if 'from pydantic import BaseModel' not in content and 'class ' in content:
        # Find the first import line and add BaseModel import
        import_match = re.search(r'(from fastapi import.*?\n)', content)
        if import_match:
            content = content.replace(
                import_match.group(1),
                import_match.group(1) + 'from pydantic import BaseModel\n'
            )
        else:
            # Add at the beginning after docstring
            content = re.sub(
                r'("""[^"]*"""\n)',
                r'\1from pydantic import BaseModel\n',
                content,
                count=1
            )
    
    # Fix response model classes
    # Pattern to match class definitions that should inherit from BaseModel
    class_pattern = r'class\s+(\w+Response[^:]*):'
    matches = re.findall(class_pattern, content)
    
    for match in matches:
        class_name = match.strip()
        # Replace class definition to inherit from BaseModel
        old_pattern = f'class {class_name}:'
        new_pattern = f'class {class_name}(BaseModel):'
        content = content.replace(old_pattern, new_pattern)
    
    # Write back if changes were made
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed response models in: {file_path}")
        return True
    return False

def main():
    """Main function to fix all response model classes"""
    backend_path = Path("backend/app/api")
    
    # Find all Python files in subdirectories
    python_files = []
    for root, dirs, files in os.walk(backend_path):
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                python_files.append(os.path.join(root, file))
    
    fixed_count = 0
    for file_path in python_files:
        if fix_response_models_in_file(file_path):
            fixed_count += 1
    
    print(f"Fixed response models in {fixed_count} files")

if __name__ == "__main__":
    main()
