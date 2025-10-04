/**
 * Enhanced Admin Dashboard
 * Comprehensive platform management and oversight
 */
import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Users, 
  BarChart3, 
  BookOpen, 
  Settings, 
  Shield, 
  Activity,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Clock,
  Zap
} from 'lucide-react';
import { useToast } from '../../contexts/ToastContext';
import UserManagement from './UserManagement';
import SystemAnalytics from './SystemAnalytics';
import ContentOversight from './ContentOversight';
import api from '../../utils/api';

interface DashboardStats {
  total_users: number;
  active_users_today: number;
  active_users_week: number;
  total_teachers: number;
  total_students: number;
  total_assessments: number;
  platform_health_score: number;
  user_engagement_rate: number;
  pending_reviews: number;
  system_alerts: number;
}

const EnhancedAdminDashboard: React.FC = () => {
  const { error } = useToast();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'users' | 'analytics' | 'content' | 'settings'>('overview');

  // Fetch dashboard stats
  const fetchStats = async () => {
    try {
      const response = await api.get('/admin/analytics/platform');
      setStats(response.data);
    } catch (err: any) {
      error('Failed to fetch dashboard stats', err.response?.data?.detail || 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  const getHealthColor = (score: number) => {
    if (score >= 80) return 'text-green-600 dark:text-green-400';
    if (score >= 60) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-red-600 dark:text-red-400';
  };

  const getHealthBg = (score: number) => {
    if (score >= 80) return 'bg-green-100 dark:bg-green-900/20';
    if (score >= 60) return 'bg-yellow-100 dark:bg-yellow-900/20';
    return 'bg-red-100 dark:bg-red-900/20';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Admin Dashboard</h1>
          <p className="text-gray-600 dark:text-gray-400">Comprehensive platform management and oversight</p>
        </div>
        
        <div className="flex items-center space-x-2">
          <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
            <Clock className="h-4 w-4 mr-1" />
            Last updated: {new Date().toLocaleTimeString()}
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200 dark:border-gray-700">
        <nav className="-mb-px flex space-x-8 overflow-x-auto">
          {[
            { id: 'overview', label: 'Overview', icon: BarChart3 },
            { id: 'users', label: 'User Management', icon: Users },
            { id: 'analytics', label: 'System Analytics', icon: TrendingUp },
            { id: 'content', label: 'Content Oversight', icon: BookOpen },
            { id: 'settings', label: 'Settings', icon: Settings }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 py-2 px-1 border-b-2 font-medium text-sm whitespace-nowrap ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
              }`}
            >
              <tab.icon className="h-4 w-4" />
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && stats && (
        <div className="space-y-6">
          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow"
            >
              <div className="flex items-center">
                <div className="p-2 bg-blue-100 dark:bg-blue-900/20 rounded-lg">
                  <Users className="h-6 w-6 text-blue-600 dark:text-blue-400" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Users</p>
                  <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                    {stats.total_users.toLocaleString()}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {stats.total_teachers} teachers, {stats.total_students} students
                  </p>
                </div>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow"
            >
              <div className="flex items-center">
                <div className="p-2 bg-green-100 dark:bg-green-900/20 rounded-lg">
                  <Activity className="h-6 w-6 text-green-600 dark:text-green-400" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Active Today</p>
                  <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                    {stats.active_users_today.toLocaleString()}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {stats.active_users_week} this week
                  </p>
                </div>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow"
            >
              <div className="flex items-center">
                <div className="p-2 bg-purple-100 dark:bg-purple-900/20 rounded-lg">
                  <BookOpen className="h-6 w-6 text-purple-600 dark:text-purple-400" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Content</p>
                  <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                    {stats.total_assessments.toLocaleString()}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    Assessments and materials
                  </p>
                </div>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow"
            >
              <div className="flex items-center">
                <div className={`p-2 rounded-lg ${getHealthBg(stats.platform_health_score)}`}>
                  <Zap className={`h-6 w-6 ${getHealthColor(stats.platform_health_score)}`} />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Platform Health</p>
                  <p className={`text-2xl font-semibold ${getHealthColor(stats.platform_health_score)}`}>
                    {stats.platform_health_score.toFixed(1)}%
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    Overall system health
                  </p>
                </div>
              </div>
            </motion.div>
          </div>

          {/* Engagement Metrics */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">User Engagement</h3>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Engagement Rate</span>
                  <span className="text-sm font-medium text-gray-900 dark:text-white">
                    {stats.user_engagement_rate.toFixed(1)}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${Math.min(stats.user_engagement_rate, 100)}%` }}
                  ></div>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Active Users</span>
                  <span className="text-sm font-medium text-gray-900 dark:text-white">
                    {stats.active_users_today} today
                  </span>
                </div>
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">System Status</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
                    <span className="text-sm text-gray-600 dark:text-gray-400">System Online</span>
                  </div>
                  <span className="text-sm font-medium text-green-600 dark:text-green-400">Operational</span>
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <Shield className="h-5 w-5 text-blue-500 mr-2" />
                    <span className="text-sm text-gray-600 dark:text-gray-400">Security</span>
                  </div>
                  <span className="text-sm font-medium text-blue-600 dark:text-blue-400">Secure</span>
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <Activity className="h-5 w-5 text-purple-500 mr-2" />
                    <span className="text-sm text-gray-600 dark:text-gray-400">Performance</span>
                  </div>
                  <span className="text-sm font-medium text-purple-600 dark:text-purple-400">Optimal</span>
                </div>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Quick Actions</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <button
                onClick={() => setActiveTab('users')}
                className="flex items-center p-4 border border-gray-200 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                <Users className="h-5 w-5 text-blue-600 dark:text-blue-400 mr-3" />
                <div className="text-left">
                  <div className="font-medium text-gray-900 dark:text-white">Manage Users</div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">View and edit users</div>
                </div>
              </button>
              
              <button
                onClick={() => setActiveTab('analytics')}
                className="flex items-center p-4 border border-gray-200 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                <BarChart3 className="h-5 w-5 text-green-600 dark:text-green-400 mr-3" />
                <div className="text-left">
                  <div className="font-medium text-gray-900 dark:text-white">View Analytics</div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">Platform insights</div>
                </div>
              </button>
              
              <button
                onClick={() => setActiveTab('content')}
                className="flex items-center p-4 border border-gray-200 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                <BookOpen className="h-5 w-5 text-purple-600 dark:text-purple-400 mr-3" />
                <div className="text-left">
                  <div className="font-medium text-gray-900 dark:text-white">Content Library</div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">Manage content</div>
                </div>
              </button>
              
              <button
                onClick={() => setActiveTab('settings')}
                className="flex items-center p-4 border border-gray-200 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                <Settings className="h-5 w-5 text-gray-600 dark:text-gray-400 mr-3" />
                <div className="text-left">
                  <div className="font-medium text-gray-900 dark:text-white">Settings</div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">Platform settings</div>
                </div>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* User Management Tab */}
      {activeTab === 'users' && <UserManagement />}

      {/* System Analytics Tab */}
      {activeTab === 'analytics' && <SystemAnalytics />}

      {/* Content Oversight Tab */}
      {activeTab === 'content' && <ContentOversight />}

      {/* Settings Tab */}
      {activeTab === 'settings' && (
        <div className="space-y-6">
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Platform Settings</h3>
            <p className="text-gray-600 dark:text-gray-400">
              Platform settings and configuration options will be available here.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default EnhancedAdminDashboard;
