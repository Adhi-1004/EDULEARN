# Role-Based Access Control (RBAC) Implementation

## Overview
This document describes the comprehensive Role-Based Access Control (RBAC) system implemented in the modLRN platform. The system ensures that users can only access features and endpoints appropriate to their role.

## Role Hierarchy
```
Admin (Level 3) > Teacher (Level 2) > Student (Level 1)
```

## Backend Implementation

### 1. User Model with Role Enum
**File: `backend/app/models/models.py`**

```python
class UserRole(str, Enum):
    student = "student"
    teacher = "teacher"
    admin = "admin"

class UserModel(BaseModel):
    role: UserRole = UserRole.student  # Default role
    # ... other fields
    
    def is_admin_role(self) -> bool:
        return self.role == UserRole.admin
    
    def has_role_or_higher(self, required_role: UserRole) -> bool:
        role_hierarchy = {
            UserRole.student: 1,
            UserRole.teacher: 2,
            UserRole.admin: 3
        }
        return role_hierarchy.get(self.role, 0) >= role_hierarchy.get(required_role, 0)
```

### 2. JWT Tokens with Role Information
**File: `backend/app/api/endpoints/auth.py`**

All authentication endpoints now include role information in JWT tokens:

```python
# Login endpoint
access_token = create_access_token(
    data={
        "sub": str(user["_id"]), 
        "email": user["email"],
        "role": user.get("role", "student")
    }
)

# Registration endpoint
access_token = create_access_token(
    data={
        "sub": str(result.inserted_id), 
        "email": user_data.email,
        "role": user_data.role or "student"
    }
)
```

### 3. Role-Based Dependencies
**File: `backend/app/dependencies.py`**

Comprehensive role-based dependencies for protecting endpoints:

```python
# Basic role dependencies
require_student = require_role("student")
require_teacher = require_role("teacher") 
require_admin = require_role("admin")

# Specific action-based dependencies
async def require_batch_management(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Require teacher or admin role for batch management"""
    user_role = current_user.get("role", "student")
    if user_role not in ["teacher", "admin"]:
        raise HTTPException(status_code=403, detail="Batch management requires teacher or admin privileges")
    return current_user

async def require_user_management(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Require admin role for user management"""
    user_role = current_user.get("role", "student")
    if user_role != "admin":
        raise HTTPException(status_code=403, detail="User management requires admin privileges")
    return current_user
```

### 4. Protected Endpoints
All teacher and admin endpoints are now protected with appropriate RBAC dependencies:

**Teacher Dashboard Endpoints:**
- `/api/teacher/students` - Requires teacher or admin role
- `/api/teacher/batches` - Requires teacher or admin role
- `/api/teacher/analytics/class` - Requires analytics access (teacher/admin)
- `/api/teacher/assessments` - Requires assessment creation (teacher/admin)

**Admin Dashboard Endpoints:**
- `/api/admin/users` - Requires user management (admin only)
- `/api/admin/analytics/platform` - Requires analytics access (teacher/admin)
- `/api/admin/system/health` - Requires platform management (admin only)

**Enhanced Dashboard Endpoints:**
- `/api/teacher/batches/mission-control` - Requires analytics access
- `/api/teacher/assessments/smart-create` - Requires assessment creation
- `/api/admin/metrics/platform-health` - Requires analytics access
- `/api/admin/content/quality-issues` - Requires content management

## Frontend Implementation

### 1. Role-Based Utilities
**File: `frontend/src/utils/roleUtils.ts`**

```typescript
export const hasRole = (user: User | null, requiredRole: UserRole): boolean => {
  if (!user || !user.role) return false;
  return ROLE_HIERARCHY[user.role] >= ROLE_HIERARCHY[requiredRole];
};

export const isAdmin = (user: User | null): boolean => {
  return hasRole(user, 'admin');
};

export const canCreateAssessments = (user: User | null): boolean => {
  return isTeacherOrAdmin(user);
};
```

### 2. Protected Routes
**File: `frontend/src/components/ProtectedRoute.tsx`**

```typescript
const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ 
  children, 
  allowedRoles 
}) => {
  const { user } = useAuth();

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  const userRole = user.role || "student";
  if (allowedRoles.includes(userRole)) {
    return <>{children}</>;
  }

  // Redirect to appropriate dashboard based on role
  switch (userRole) {
    case "teacher":
      return <Navigate to="/teacher-dashboard" replace />;
    case "admin":
      return <Navigate to="/admin-dashboard" replace />;
    default:
      return <Navigate to="/dashboard" replace />;
  }
};
```

### 3. Conditional UI Rendering
**File: `frontend/src/components/Navbar.tsx`**

The navbar uses role-based utilities to show/hide navigation items:

```typescript
import { getNavigationItems, canAccessRoute, getUserDisplayName, getRoleDisplayName } from "../utils/roleUtils";

// Navigation items are filtered based on user role
const navigationItems = getNavigationItems(user);
```

## Security Features

### 1. Backend Security
- **JWT Token Validation**: All protected endpoints validate JWT tokens
- **Role Verification**: Each request checks user role against required permissions
- **Hierarchical Access**: Higher roles can access lower role features
- **Action-Based Permissions**: Specific actions require specific permissions

### 2. Frontend Security
- **Route Protection**: Routes are protected based on user roles
- **UI Conditional Rendering**: UI elements are shown/hidden based on user permissions
- **Automatic Redirects**: Users are redirected to appropriate dashboards based on their role
- **Token Management**: JWT tokens are properly stored and managed

### 3. API Security
- **403 Forbidden**: Unauthorized access returns proper HTTP status codes
- **Detailed Error Messages**: Clear error messages for unauthorized access
- **Token Expiration**: JWT tokens have proper expiration times
- **Role Validation**: Every protected endpoint validates user roles

## Testing

### 1. Backend Testing
Run the comprehensive RBAC test:

```bash
python test_rbac_system.py
```

This test:
- Registers test users for each role
- Tests role-based access to all endpoints
- Verifies JWT token role information
- Tests role hierarchy functionality

### 2. Frontend Testing
The frontend automatically handles role-based access through:
- Protected routes that redirect unauthorized users
- Conditional rendering of UI elements
- Role-based navigation items
- Automatic dashboard redirection

## Usage Examples

### 1. Backend Endpoint Protection
```python
@router.get("/api/teacher/students")
async def get_teacher_students(teacher: dict = Depends(require_teacher_or_admin)):
    """Get all students assigned to this teacher"""
    # Only teachers and admins can access this endpoint
    pass

@router.delete("/api/admin/users/{user_id}")
async def delete_user(user_id: str, admin: dict = Depends(require_user_management)):
    """Delete a user - admin only"""
    # Only admins can delete users
    pass
```

### 2. Frontend Role Checking
```typescript
// Check if user can create assessments
if (canCreateAssessments(user)) {
  return <CreateAssessmentButton />;
}

// Check if user is admin
if (isAdmin(user)) {
  return <AdminPanel />;
}

// Get user's dashboard path
const dashboardPath = getDashboardPath(user);
```

## Benefits

1. **Security**: Prevents unauthorized access to sensitive features
2. **User Experience**: Users only see features they can use
3. **Maintainability**: Centralized role management
4. **Scalability**: Easy to add new roles and permissions
5. **Compliance**: Meets security requirements for educational platforms

## Conclusion

The RBAC system provides comprehensive security for the modLRN platform, ensuring that:
- Students can only access student features
- Teachers can access teacher and student features
- Admins can access all features
- The system is secure both on the backend and frontend
- All endpoints are properly protected with appropriate role checks
