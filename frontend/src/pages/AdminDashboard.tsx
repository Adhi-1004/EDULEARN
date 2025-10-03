import React, { useState } from "react";
import { motion } from "framer-motion";
import { useAuth } from "../hooks/useAuth";
import { User } from "../types";
import AnimatedBackground from "../components/AnimatedBackground";
import LoadingSpinner from "../components/ui/LoadingSpinner";
import AdminMetrics from "../components/admin/AdminMetrics";
import UserManagement from "../components/admin/UserManagement";
import ContentOversight from "../components/admin/ContentOversight";

interface AdminDashboardProps {
  user?: User;
}

const AdminDashboard: React.FC<AdminDashboardProps> = ({ user: propUser }) => {
  const { user: authUser } = useAuth();
  
  // Use prop user or auth user
  const user = propUser || authUser;
  
  const [activeTab, setActiveTab] = useState<'overview' | 'users' | 'content'>('overview');
  
  // Show loading if user is not available yet
  if (!user) {
    return (
      <>
        <AnimatedBackground />
        <div className="min-h-screen pt-20 px-4 relative z-10">
          <div className="max-w-7xl mx-auto">
            <div className="bg-purple-900/20 backdrop-blur-sm rounded-xl border border-purple-500/30 p-8 text-center">
              <LoadingSpinner size="lg" />
              <p className="text-purple-300 mt-4">Loading admin dashboard...</p>
            </div>
          </div>
        </div>
      </>
    );
  }

  return (
    <>
      <AnimatedBackground />
      <div className="min-h-screen pt-20 px-4 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-7xl mx-auto"
        >
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-purple-200 mb-2">
              Admin Dashboard
            </h1>
            <p className="text-purple-300 text-lg">
              Welcome back, {user?.name || user?.email || user?.username || 'Admin'}!
            </p>
          </div>

          {/* Navigation Tabs */}
          <div className="flex space-x-2 mb-8">
            <button
              onClick={() => setActiveTab('overview')}
              className={`px-6 py-3 rounded-lg font-medium transition-all ${
                activeTab === 'overview'
                  ? 'bg-purple-600 text-white shadow-lg'
                  : 'bg-purple-900/50 text-purple-300 hover:bg-purple-800/50'
              }`}
            >
              📊 Overview
            </button>
            <button
              onClick={() => setActiveTab('users')}
              className={`px-6 py-3 rounded-lg font-medium transition-all ${
                activeTab === 'users'
                  ? 'bg-purple-600 text-white shadow-lg'
                  : 'bg-purple-900/50 text-purple-300 hover:bg-purple-800/50'
              }`}
            >
              👥 User Management
            </button>
            <button
              onClick={() => setActiveTab('content')}
              className={`px-6 py-3 rounded-lg font-medium transition-all ${
                activeTab === 'content'
                  ? 'bg-purple-600 text-white shadow-lg'
                  : 'bg-purple-900/50 text-purple-300 hover:bg-purple-800/50'
              }`}
            >
              📚 Content Oversight
            </button>
          </div>

          {/* Tab Content */}
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            {activeTab === 'overview' && <AdminMetrics />}
            {activeTab === 'users' && <UserManagement />}
            {activeTab === 'content' && <ContentOversight />}
          </motion.div>
        </motion.div>
      </div>
    </>
  );
};

export default AdminDashboard;