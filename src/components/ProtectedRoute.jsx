import { Navigate } from "react-router-dom"

const ProtectedRoute = ({ user, userType, children }) => {
  if (!user) {
    return <Navigate to="/login" replace />
  }

  if (userType && user.role !== userType) {
    return <Navigate to={`/${user.role}/dashboard`} replace />
  }

  return children
}

export default ProtectedRoute
