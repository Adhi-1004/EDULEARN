import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import HomePage from './pages/HomePage';
import { StudentDashboard } from './pages/student/StudentDashboard';
import { TeacherDashboard } from './pages/teacher/TeacherDashboard';
import { useAuth, AuthProvider } from './hooks/useAuth.tsx';
import LoginPage from './pages/LoginPage.jsx';
import RegisterPage from './pages/RegisterPage.jsx';
import MCQAssessment from './pages/student/MCQAssessment.jsx';
import ResultsPage from './pages/student/ResultsPage.jsx';
import { BackendProvider } from './contexts/BackendContext.jsx';

function InnerApp() {
  const { user, login, logout, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 text-lg">Loading EduLearn AI...</p>
        </div>
      </div>
    );
  }

  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage onLogin={login} />} />
        <Route path="/register" element={<RegisterPage onLogin={login} />} />
        
        {/* Student Routes */}
        <Route
          path="/student/dashboard"
          element={
            user?.role === 'student' ? (
              <StudentDashboard user={user} onLogout={logout} />
            ) : (
              <Navigate to="/" replace />
            )
          }
        />

        <Route
          path="/student/mcq"
          element={
            user?.role === 'student' ? (
              <MCQAssessment />
            ) : (
              <Navigate to="/" replace />
            )
          }
        />

        <Route
          path="/student/results"
          element={
            user?.role === 'student' ? (
              <ResultsPage user={user} onLogout={logout} />
            ) : (
              <Navigate to="/" replace />
            )
          }
        />

        {/* Teacher Routes */}
        <Route
          path="/teacher/dashboard"
          element={
            user?.role === 'teacher' ? (
              <TeacherDashboard user={user} onLogout={logout} />
            ) : (
              <Navigate to="/" replace />
            )
          }
        />

        {/* Catch all route */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

function App() {
  return (
    <AuthProvider>
      <BackendProvider>
        <InnerApp />
      </BackendProvider>
    </AuthProvider>
  );
}

export default App;
