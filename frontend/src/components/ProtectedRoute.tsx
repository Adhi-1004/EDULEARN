import React from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

interface ProtectedRouteProps {
  children: React.ReactNode;
  allowedRoles?: string[];
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ 
  children, 
  allowedRoles 
}) => {
  const { user } = useAuth();

  // If not authenticated, redirect to login
  if (!user) {
    return <Navigate to="/login" replace />;
  }

  // If no specific roles required, allow access
  if (!allowedRoles || allowedRoles.length === 0) {
    return <>{children}</>;
  }

  // Check if user's role is in allowed roles
  const userRole = user.role || "student";
  
  if (allowedRoles.includes(userRole)) {
    return <>{children}</>;
  }

  // If user doesn't have required role, redirect to appropriate dashboard
  switch (userRole) {
    case "teacher":
      return <Navigate to="/teacher-dashboard" replace />;
    case "admin":
      return <Navigate to="/admin-dashboard" replace />;
    default:
      return <Navigate to="/dashboard" replace />;
  }
};

export default ProtectedRoute;
