import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Modal } from './ui/Modal';
import { Button } from './ui/Button';
import { User, Mail, Lock, Camera, Eye, EyeOff, Sparkles } from 'lucide-react';
import Webcam from 'react-webcam';
import { useCamera } from '../hooks/useCamera';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onLogin: (userData: any) => void;
  initialMode?: 'login' | 'register';
}

export const AuthModal: React.FC<AuthModalProps> = ({
  isOpen,
  onClose,
  onLogin,
  initialMode = 'login'
}) => {
  const [mode, setMode] = useState<'login' | 'register'>(initialMode);
  const [userType, setUserType] = useState<'student' | 'teacher'>('student');
  const [showPassword, setShowPassword] = useState(false);
  const [showFaceAuth, setShowFaceAuth] = useState(false);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: ''
  });

  const { isActive, startCamera, stopCamera, capturePhoto, webcamRef } = useCamera();

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  const handleGoogleAuth = async () => {
    setLoading(true);
    // Simulate Google OAuth
    setTimeout(() => {
      const userData = {
        id: Math.random().toString(36).substr(2, 9),
        name: 'John Doe',
        email: 'john.doe@gmail.com',
        role: userType,
        avatar: '/placeholder.svg?height=40&width=40&text=JD',
        department: userType === 'student' ? 'Computer Science' : 'Engineering',
        year: userType === 'student' ? 3 : undefined,
        semester: userType === 'student' ? 5 : undefined,
        rollNumber: userType === 'student' ? 'CS21B1001' : undefined
      };
      onLogin(userData);
      onClose();
      setLoading(false);
    }, 1500);
  };

  const handleFaceAuth = async () => {
    if (!isActive) {
      await startCamera();
      setShowFaceAuth(true);
    } else {
      const photo = capturePhoto();
      if (photo) {
        setLoading(true);
        // Simulate face recognition
        setTimeout(() => {
          const userData = {
            id: Math.random().toString(36).substr(2, 9),
            name: 'Face User',
            email: 'face.user@example.com',
            role: userType,
            avatar: photo,
            department: userType === 'student' ? 'Computer Science' : 'Engineering',
            year: userType === 'student' ? 2 : undefined,
            semester: userType === 'student' ? 4 : undefined,
            rollNumber: userType === 'student' ? 'CS22B1002' : undefined
          };
          onLogin(userData);
          stopCamera();
          onClose();
          setLoading(false);
        }, 2000);
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    // Simulate API call
    setTimeout(() => {
      const userData = {
        id: Math.random().toString(36).substr(2, 9),
        name: mode === 'register' ? formData.name : 'Demo User',
        email: formData.email,
        role: userType,
        avatar: '/placeholder.svg?height=40&width=40&text=' + (formData.name || 'DU').charAt(0),
        department: userType === 'student' ? 'Computer Science' : 'Engineering',
        year: userType === 'student' ? 1 : undefined,
        semester: userType === 'student' ? 1 : undefined,
        rollNumber: userType === 'student' ? 'CS24B1003' : undefined
      };
      onLogin(userData);
      onClose();
      setLoading(false);
    }, 1500);
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="md">
      <div className="space-y-6">
        <div className="text-center">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: "spring", stiffness: 300, damping: 20 }}
            className="mx-auto w-16 h-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center mb-4 relative"
          >
            <User className="h-8 w-8 text-white" />
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
              className="absolute inset-0 border-2 border-transparent border-t-blue-300 rounded-full"
            />
          </motion.div>
          <h2 className="text-2xl font-bold text-gray-900">
            {mode === 'login' ? 'Welcome Back! 👋' : 'Join EduLearn AI ✨'}
          </h2>
          <p className="text-gray-600 mt-2">
            {mode === 'login' ? 'Sign in to continue your learning journey' : 'Start your educational transformation today'}
          </p>
        </div>

        {/* User Type Toggle */}
        <div className="flex bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-1">
          <button
            type="button"
            onClick={() => setUserType('student')}
            className={`flex-1 py-3 px-4 rounded-md text-sm font-medium transition-all flex items-center justify-center space-x-2 ${
              userType === 'student'
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <User className="h-4 w-4" />
            <span>Student</span>
          </button>
          <button
            type="button"
            onClick={() => setUserType('teacher')}
            className={`flex-1 py-3 px-4 rounded-md text-sm font-medium transition-all flex items-center justify-center space-x-2 ${
              userType === 'teacher'
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <Sparkles className="h-4 w-4" />
            <span>Teacher</span>
          </button>
        </div>

        {/* Face Authentication */}
        {showFaceAuth && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="border-2 border-dashed border-blue-300 rounded-lg p-4 bg-blue-50"
          >
            <div className="text-center">
              <Webcam
                ref={webcamRef}
                audio={false}
                screenshotFormat="image/jpeg"
                className="w-full max-w-sm mx-auto rounded-lg shadow-lg"
              />
              <p className="text-sm text-blue-600 mt-3 font-medium">
                Position your face in the camera and click capture
              </p>
            </div>
          </motion.div>
        )}

        {/* Social Login */}
        <div className="space-y-3">
          <Button
            onClick={handleGoogleAuth}
            variant="outline"
            className="w-full border-2 hover:border-blue-300 hover:bg-blue-50"
            loading={loading}
          >
            <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
            Continue with Google
          </Button>

          <Button
            onClick={handleFaceAuth}
            variant="outline"
            className="w-full border-2 hover:border-purple-300 hover:bg-purple-50"
            loading={loading}
          >
            <Camera className="w-5 h-5 mr-2" />
            {isActive ? 'Capture Face' : 'Use Face Recognition'}
          </Button>
        </div>

        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-300" />
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-2 bg-white text-gray-500">Or continue with email</span>
          </div>
        </div>

        {/* Email Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {mode === 'register' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Full Name
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                  placeholder="Enter your full name"
                  required
                />
              </div>
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email Address
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                placeholder="Enter your email"
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Password
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type={showPassword ? 'text' : 'password'}
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                className="w-full pl-10 pr-12 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                placeholder="Enter your password"
                required
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
              >
                {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
              </button>
            </div>
          </div>

          {mode === 'register' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Confirm Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleInputChange}
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                  placeholder="Confirm your password"
                  required
                />
              </div>
            </div>
          )}

          <Button type="submit" className="w-full py-3" loading={loading}>
            {mode === 'login' ? 'Sign In' : 'Create Account'}
          </Button>
        </form>

        <div className="text-center">
          <button
            onClick={() => setMode(mode === 'login' ? 'register' : 'login')}
            className="text-sm text-blue-600 hover:text-blue-500 font-medium"
          >
            {mode === 'login' 
              ? "Don't have an account? Sign up" 
              : "Already have an account? Sign in"
            }
          </button>
        </div>
      </div>
    </Modal>
  );
};
