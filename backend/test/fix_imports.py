"""
Fix Import Paths Script
Automatically fixes import paths in modularized API files
"""
import os
import re
from pathlib import Path

def fix_imports_in_file(file_path: str):
    """Fix import paths in a single file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Track if any changes were made
    original_content = content
    
    # Fix relative imports based on file location
    if '/api/admin/' in file_path:
        # Admin files need to go up 3 levels
        content = re.sub(r'from \.\.db import', 'from ...db import', content)
        content = re.sub(r'from \.\.dependencies import', 'from ...dependencies import', content)
        content = re.sub(r'from \.\.models\.models import', 'from ...models.models import', content)
        content = re.sub(r'from \.\.schemas\.schemas import', 'from ...schemas.schemas import', content)
        content = re.sub(r'from \.\.services\.', 'from ...services.', content)
        content = re.sub(r'from \.\.utils\.', 'from ...utils.', content)
    elif '/api/teacher/' in file_path:
        # Teacher files need to go up 3 levels
        content = re.sub(r'from \.\.db import', 'from ...db import', content)
        content = re.sub(r'from \.\.dependencies import', 'from ...dependencies import', content)
        content = re.sub(r'from \.\.models\.models import', 'from ...models.models import', content)
        content = re.sub(r'from \.\.schemas\.schemas import', 'from ...schemas.schemas import', content)
        content = re.sub(r'from \.\.services\.', 'from ...services.', content)
        content = re.sub(r'from \.\.utils\.', 'from ...utils.', content)
    elif '/api/assessments/' in file_path:
        # Assessment files need to go up 3 levels
        content = re.sub(r'from \.\.db import', 'from ...db import', content)
        content = re.sub(r'from \.\.dependencies import', 'from ...dependencies import', content)
        content = re.sub(r'from \.\.models\.models import', 'from ...models.models import', content)
        content = re.sub(r'from \.\.schemas\.schemas import', 'from ...schemas.schemas import', content)
        content = re.sub(r'from \.\.services\.', 'from ...services.', content)
        content = re.sub(r'from \.\.utils\.', 'from ...utils.', content)
    elif '/api/coding/' in file_path:
        # Coding files need to go up 3 levels
        content = re.sub(r'from \.\.db import', 'from ...db import', content)
        content = re.sub(r'from \.\.dependencies import', 'from ...dependencies import', content)
        content = re.sub(r'from \.\.models\.models import', 'from ...models.models import', content)
        content = re.sub(r'from \.\.schemas\.schemas import', 'from ...schemas.schemas import', content)
        content = re.sub(r'from \.\.services\.', 'from ...services.', content)
        content = re.sub(r'from \.\.utils\.', 'from ...utils.', content)
    
    # Write back if changes were made
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed imports in: {file_path}")
        return True
    return False

def main():
    """Main function to fix all import paths"""
    backend_path = Path("backend/app/api")
    
    # Find all Python files in subdirectories
    python_files = []
    for root, dirs, files in os.walk(backend_path):
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                python_files.append(os.path.join(root, file))
    
    fixed_count = 0
    for file_path in python_files:
        if fix_imports_in_file(file_path):
            fixed_count += 1
    
    print(f"Fixed imports in {fixed_count} files")

if __name__ == "__main__":
    main()
