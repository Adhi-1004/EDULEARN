"use client"

import React from "react"
import { BrowserRouter as Router, Route, Routes, Navigate } from "react-router-dom"
import { AnimatePresence } from "framer-motion"

import { ThemeProvider } from "./contexts/ThemeContext"
import { ToastProvider, useToast } from "./contexts/ToastContext"
import { useAuth } from "./hooks/useAuth"
import Navbar from "./components/Navbar"
import ToastContainer from "./components/ui/ToastContainer"
import LoadingState from "./components/LoadingState"
import ProtectedRoute from "./components/ProtectedRoute"
import LandingPage from "./pages/LandingPage"
import Dashboard from "./pages/Dashboard"
import Assessment from "./pages/Assessment"
import Results from "./pages/Results"
import CodingResults from "./pages/CodingResults"
import TestResultDetail from "./pages/TestResultDetail"
import Login from "./pages/Login"
import Signup from "./pages/Signup"
import UserProfile from "./pages/UserProfile"
import Settings from "./pages/Settings"
import TeacherProfile from "./pages/TeacherProfile"
import TeacherSettings from "./pages/TeacherSettings"
import CodingPlatform from "./pages/CodingPlatform"
import CodingProblemPage from "./pages/CodingProblem"
import UnifiedAssessment from "./pages/UnifiedAssessment"
import TeacherDashboard from "./pages/TeacherDashboard"
import TeacherResultsDashboard from "./pages/TeacherResultsDashboard"
import TeacherAssessmentResults from "./pages/TeacherAssessmentResults"
import TeacherAssessmentHistory from "./pages/TeacherAssessmentHistory"
import StudentManagement from "./pages/StudentManagement"
import AssessmentManagement from "./pages/AssessmentManagement"
import CreateAssessment from "./pages/CreateAssessment"
import BatchAnalytics from "./pages/BatchAnalytics"
import EnhancedAdminDashboard from "./components/admin/EnhancedAdminDashboard"
import TestPage from "./pages/TestPage"

const AppContent: React.FC = () => {
  const auth = useAuth()
  console.log('Auth object:', auth)
  const { user, setUser, isLoading } = auth
  const logout = auth.logout

  if (isLoading) {
    return <LoadingState text="Loading application..." size="lg" fullScreen={true} />
  }

  return (
    <ThemeProvider>
      <ToastProvider>
        <AppRouter user={user} setUser={setUser} logout={logout} />
      </ToastProvider>
    </ThemeProvider>
  )
}

const AppRouter: React.FC<{ user: any; setUser: any; logout: any }> = ({ user, setUser, logout }) => {
  const { toasts, removeToast } = useToast()
  const [adminTab, setAdminTab] = React.useState<"users" | "content" | "settings">("users")
  const [adminRefreshKey, setAdminRefreshKey] = React.useState(0)

  const handleAdminRefresh = () => {
    setAdminRefreshKey((prev) => prev + 1)
  }

  // Function to get the appropriate dashboard path based on user role
  const getDashboardPath = (user: any) => {
    if (!user) return "/login"

    const userRole = user.role || "student"
    switch (userRole) {
      case "teacher":
        return "/teacher-dashboard"
      case "admin":
        return "/admin-dashboard"
      case "student":
      default:
        return "/dashboard"
    }
  }


  return (
    <Router>
      <div className="min-h-screen relative overflow-hidden transition-colors duration-300 bg-background text-foreground">
        <div className="app-bg" aria-hidden="true" />
        <Navbar 
          user={user} 
          setUser={setUser} 
          logout={logout}
          adminTab={adminTab}
          setAdminTab={setAdminTab}
          onAdminRefresh={handleAdminRefresh}
        />
        <ToastContainer toasts={toasts} onClose={removeToast} />
            <AnimatePresence mode="wait">
              <Routes>
                <Route path="/" element={user ? <Navigate to={getDashboardPath(user)} replace /> : <LandingPage />} />
                <Route
                  path="/login"
                  element={<Login setUser={setUser} />}
                />
                <Route
                  path="/signup"
                  element={user ? <Navigate to={getDashboardPath(user)} replace /> : <Signup setUser={setUser} />}
                />
                <Route
                  path="/dashboard"
                  element={
                    <ProtectedRoute allowedRoles={["student"]}>
                      <Dashboard />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/teacher-dashboard"
                  element={
                    <ProtectedRoute allowedRoles={["teacher"]}>
                      <TeacherDashboard />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/teacher/student-management"
                  element={
                    <ProtectedRoute allowedRoles={["teacher"]}>
                      <StudentManagement />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/teacher/assessment-management"
                  element={
                    <ProtectedRoute allowedRoles={["teacher"]}>
                      <AssessmentManagement />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/teacher/create-assessment"
                  element={
                    <ProtectedRoute allowedRoles={["teacher"]}>
                      <CreateAssessment />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/teacher/batch-analytics"
                  element={
                    <ProtectedRoute allowedRoles={["teacher"]}>
                      <BatchAnalytics />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/teacher/results-dashboard"
                  element={
                    <ProtectedRoute allowedRoles={["teacher"]}>
                      <TeacherResultsDashboard />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/teacher/assessment-history"
                  element={
                    <ProtectedRoute allowedRoles={["teacher"]}>
                      <TeacherAssessmentHistory />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/teacher/assessment/:assessmentId/results"
                  element={
                    <ProtectedRoute allowedRoles={["teacher"]}>
                      <TeacherAssessmentResults />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/teacher/test-result/:resultId"
                  element={
                    <ProtectedRoute allowedRoles={["teacher"]}>
                      <TestResultDetail />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/admin-dashboard"
                  element={
                    <ProtectedRoute allowedRoles={["admin"]}>
                      <EnhancedAdminDashboard activeTab={adminTab} refreshKey={adminRefreshKey} />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/assessconfig"
                  element={
                    <ProtectedRoute allowedRoles={["student"]}>
                      <UnifiedAssessment />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/assessment"
                  element={
                    <ProtectedRoute allowedRoles={["student"]}>
                      <Assessment />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/assessment/:id"
                  element={
                    <ProtectedRoute allowedRoles={["student"]}>
                      <Assessment />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/test/:assessmentId"
                  element={
                    <ProtectedRoute allowedRoles={["student"]}>
                      <TestPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/results"
                  element={
                    <ProtectedRoute allowedRoles={["student"]}>
                      {user && <Results user={user} />}
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/coding-results"
                  element={
                    <ProtectedRoute allowedRoles={["student"]}>
                      <CodingResults />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/test-result/:resultId"
                  element={
                    <ProtectedRoute allowedRoles={["student"]}>
                      <TestResultDetail />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/profile"
                  element={
                    <ProtectedRoute allowedRoles={["student", "teacher", "admin"]}>
                      {user && user.role === "teacher" ? (
                        <TeacherProfile />
                      ) : (
                        <UserProfile user={user} />
                      )}
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/settings"
                  element={
                    <ProtectedRoute allowedRoles={["student", "teacher", "admin"]}>
                      {user && user.role === "teacher" ? (
                        <TeacherSettings />
                      ) : (
                        <Settings user={user} />
                      )}
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/coding"
                  element={
                    <ProtectedRoute allowedRoles={["student"]}>
                      <CodingPlatform />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/coding/problem/:problemId"
                  element={
                    <ProtectedRoute allowedRoles={["student"]}>
                      {user && <CodingProblemPage user={user} />}
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/assessment-choice"
                  element={
                    <ProtectedRoute allowedRoles={["student"]}>
                      <UnifiedAssessment />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/unified-assessment"
                  element={
                    <ProtectedRoute allowedRoles={["student"]}>
                      <UnifiedAssessment />
                    </ProtectedRoute>
                  }
                />
              </Routes>
            </AnimatePresence>
          </div>
        </Router>
  )
}

const App: React.FC = () => {
  return <AppContent />
}

export default App