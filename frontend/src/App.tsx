"use client"

import type React from "react"
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
import TestResultDetail from "./pages/TestResultDetail"
import Login from "./pages/Login"
import Signup from "./pages/Signup"
import UserProfile from "./pages/UserProfile"
import Settings from "./pages/Settings"
import CodingPlatform from "./pages/CodingPlatform"
import CodingProblemPage from "./pages/CodingProblem"
import UnifiedAssessment from "./pages/UnifiedAssessment"
import TeacherDashboard from "./pages/TeacherDashboard"
import EnhancedAdminDashboard from "./components/admin/EnhancedAdminDashboard"
import TestPage from "./pages/TestPage"

const AppContent: React.FC = () => {
  const { user, setUser, logout, isLoading } = useAuth()
  const { toasts, removeToast } = useToast()

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

  if (isLoading) {
    return <LoadingState text="Loading application..." size="lg" fullScreen={true} />
  }

  return (
    <ThemeProvider>
      <ToastProvider>
        <Router>
          <div className="min-h-screen relative overflow-hidden transition-colors duration-300 bg-background text-foreground">
            <div className="app-bg" aria-hidden="true" />
            <Navbar user={user} setUser={logout} />
            <ToastContainer toasts={toasts} onClose={removeToast} />
            <AnimatePresence mode="wait">
              <Routes>
                <Route path="/" element={user ? <Navigate to={getDashboardPath(user)} replace /> : <LandingPage />} />
                <Route
                  path="/login"
                  element={user ? <Navigate to={getDashboardPath(user)} replace /> : <Login setUser={setUser} />}
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
                  path="/admin-dashboard"
                  element={
                    <ProtectedRoute allowedRoles={["admin"]}>
                      <EnhancedAdminDashboard />
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
                  path="/test-result/:id"
                  element={
                    <ProtectedRoute allowedRoles={["student"]}>
                      <TestResultDetail />
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
                  {user && <UserProfile user={user} />}
                </ProtectedRoute>
              }
            />
            <Route
              path="/settings"
              element={
                <ProtectedRoute allowedRoles={["student", "teacher", "admin"]}>
                  {user && <Settings user={user} />}
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
      </ToastProvider>
    </ThemeProvider>
  )
}

const App: React.FC = () => {
  return (
    <ThemeProvider>
      <ToastProvider>
        <AppContent />
      </ToastProvider>
    </ThemeProvider>
  )
}

export default App
