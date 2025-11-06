# Contributing to EDULEARN

Thank you for your interest in contributing to EDULEARN! This document provides guidelines and instructions for contributing.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Contributing Process](#contributing-process)
5. [Coding Standards](#coding-standards)
6. [Testing](#testing)
7. [Documentation](#documentation)
8. [Pull Request Process](#pull-request-process)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors.

### Expected Behavior

- Be respectful and inclusive
- Welcome constructive feedback
- Focus on what is best for the community
- Show empathy towards other community members

### Unacceptable Behavior

- Harassment or discriminatory language
- Trolling or insulting comments
- Public or private harassment
- Publishing others' private information

---

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 18+
- MongoDB 6.0+
- Git

### Fork and Clone

1. **Fork the repository** on GitHub
2. **Clone your fork:**
   ```bash
   git clone https://github.com/your-username/edulearn.git
   cd edulearn
   ```

3. **Add upstream remote:**
   ```bash
   git remote add upstream https://github.com/original-owner/edulearn.git
   ```

---

## Development Setup

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

### Frontend Setup

```bash
cd frontend
npm install
```

### Environment Configuration

1. **Copy environment template:**
   ```bash
   cp backend/env.example backend/.env
   ```

2. **Configure environment variables:**
   ```env
   MONGO_URI=mongodb://localhost:27017
   DB_NAME=edulearn_dev
   SECRET_KEY=your-dev-secret-key
   GEMINI_API_KEY=your-api-key
   ```

3. **Start services:**
   ```bash
   # Terminal 1: Backend
   cd backend
   python main.py
   
   # Terminal 2: Frontend
   cd frontend
   npm run dev
   ```

---

## Contributing Process

### 1. Choose an Issue

- Check [GitHub Issues](https://github.com/your-repo/edulearn/issues)
- Look for "good first issue" labels
- Comment on the issue to express interest

### 2. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

**Branch Naming:**
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions

### 3. Make Changes

- Write clean, readable code
- Follow coding standards
- Add tests for new features
- Update documentation

### 4. Commit Changes

```bash
git add .
git commit -m "feat: add new feature description"
```

**Commit Message Format:**
```
<type>: <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code refactoring
- `test`: Tests
- `chore`: Maintenance

### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

---

## Coding Standards

### Python (Backend)

**Style Guide:** PEP 8

**Key Points:**
- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Use type hints
- Follow naming conventions:
  - Functions: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_SNAKE_CASE`

**Example:**
```python
from typing import Optional, List
from pydantic import BaseModel

class UserModel(BaseModel):
    """User data model."""
    id: str
    email: str
    name: str

async def get_user(user_id: str) -> Optional[UserModel]:
    """Get user by ID."""
    # Implementation
    pass
```

**Linting:**
```bash
# Install linters
pip install flake8 black isort mypy

# Run linters
flake8 app/
black app/
isort app/
mypy app/
```

### TypeScript (Frontend)

**Style Guide:** Airbnb TypeScript Style Guide

**Key Points:**
- Use 2 spaces for indentation
- Use TypeScript strict mode
- Prefer functional components
- Use meaningful variable names

**Example:**
```typescript
interface User {
  id: string;
  email: string;
  name: string;
}

const getUser = async (userId: string): Promise<User | null> => {
  // Implementation
  return null;
};
```

**Linting:**
```bash
npm run lint
npm run type-check
```

### Code Organization

**Backend Structure:**
```
backend/app/
├── api/          # API endpoints
├── core/         # Core configuration
├── db/           # Database
├── models/       # Data models
├── schemas/      # Pydantic schemas
├── services/     # Business logic
└── utils/        # Utilities
```

**Frontend Structure:**
```
frontend/src/
├── api/          # API services
├── components/   # React components
├── pages/        # Page components
├── hooks/        # Custom hooks
├── contexts/     # Context providers
└── utils/        # Utilities
```

---

## Testing

### Backend Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test
pytest tests/test_auth.py
```

**Test Structure:**
```python
import pytest
from fastapi.testclient import TestClient

def test_endpoint():
    """Test endpoint functionality."""
    client = TestClient(app)
    response = client.get("/api/endpoint")
    assert response.status_code == 200
```

### Frontend Testing

```bash
# Run tests
npm test

# Run with coverage
npm test -- --coverage

# Run in watch mode
npm test -- --watch
```

**Test Structure:**
```typescript
import { render, screen } from '@testing-library/react';
import Component from './Component';

test('renders component', () => {
  render(<Component />);
  expect(screen.getByText('Hello')).toBeInTheDocument();
});
```

---

## Documentation

### Code Documentation

**Python Docstrings:**
```python
def function_name(param1: str, param2: int) -> bool:
    """
    Brief description of function.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When invalid input
    """
    pass
```

**TypeScript JSDoc:**
```typescript
/**
 * Brief description of function.
 * 
 * @param param1 - Description of param1
 * @param param2 - Description of param2
 * @returns Description of return value
 */
function functionName(param1: string, param2: number): boolean {
  return true;
}
```

### Documentation Updates

- Update relevant documentation files
- Add examples for new features
- Update API documentation
- Keep README files current

---

## Pull Request Process

### Before Submitting

- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] No merge conflicts
- [ ] Branch is up to date with main

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How was this tested?

## Checklist
- [ ] Code follows style guidelines
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No breaking changes
```

### Review Process

1. **Automated Checks:**
   - Linting passes
   - Tests pass
   - Build succeeds

2. **Code Review:**
   - At least one approval required
   - Address review comments
   - Update PR if needed

3. **Merge:**
   - Squash and merge preferred
   - Delete branch after merge

---

## Additional Resources

### Documentation
- [Backend README](../backend/README.md)
- [Frontend README](../frontend/README.md)
- [API Documentation](../docs/COMPLETE_API_REFERENCE.md)

### Tools
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [TypeScript Documentation](https://www.typescriptlang.org/)

### Communication
- GitHub Issues for bug reports
- GitHub Discussions for questions
- Email for security issues

---

## Questions?

If you have questions about contributing:
1. Check existing documentation
2. Search GitHub Issues
3. Ask in GitHub Discussions
4. Contact maintainers

---

**Thank you for contributing to EDULEARN!** 🎉

