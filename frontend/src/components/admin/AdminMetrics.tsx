import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import Card from '../ui/Card';
import LoadingSpinner from '../ui/LoadingSpinner';
import api from '../../utils/api';

interface AdminMetrics {
  total_users: number;
  total_students: number;
  total_teachers: number;
  total_admins: number;
  active_users_24h: number;
  assessments_completed: number;
  coding_submissions: number;
}

interface RecentActivity {
  type: string;
  message: string;
  timestamp: string;
  user_id: string;
  role?: string;
  score?: number;
  total?: number;
  status?: string;
}

interface RegistrationData {
  date: string;
  students: number;
  teachers: number;
  total: number;
}

const AdminMetrics: React.FC = () => {
  const [metrics, setMetrics] = useState<AdminMetrics | null>(null);
  const [recentActivities, setRecentActivities] = useState<RecentActivity[]>([]);
  const [registrationData, setRegistrationData] = useState<RegistrationData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchMetrics();
  }, []);

  const fetchMetrics = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/admin/metrics/overview');
      
      if (response.data.success) {
        setMetrics(response.data.metrics);
        setRecentActivities(response.data.recent_activities);
        setRegistrationData(response.data.registration_chart);
      }
    } catch (error: any) {
      console.error('Error fetching admin metrics:', error);
      setError(error.response?.data?.detail || 'Failed to fetch metrics');
    } finally {
      setLoading(false);
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'user_registration':
        return '👤';
      case 'assessment_completed':
        return '📝';
      case 'coding_submission':
        return '💻';
      default:
        return '📊';
    }
  };

  const getActivityColor = (type: string) => {
    switch (type) {
      case 'user_registration':
        return 'text-green-400';
      case 'assessment_completed':
        return 'text-blue-400';
      case 'coding_submission':
        return 'text-purple-400';
      default:
        return 'text-gray-400';
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <p className="text-red-400">Error: {error}</p>
        <button 
          onClick={fetchMetrics}
          className="mt-4 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-300 text-sm">Total Users</p>
                <p className="text-3xl font-bold text-purple-200">{metrics?.total_users || 0}</p>
                <div className="flex space-x-4 mt-2 text-sm">
                  <span className="text-green-400">{metrics?.total_students || 0} Students</span>
                  <span className="text-blue-400">{metrics?.total_teachers || 0} Teachers</span>
                  <span className="text-yellow-400">{metrics?.total_admins || 0} Admins</span>
                </div>
              </div>
              <div className="text-4xl">👥</div>
            </div>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-300 text-sm">Active Users (24h)</p>
                <p className="text-3xl font-bold text-purple-200">{metrics?.active_users_24h || 0}</p>
                <p className="text-sm text-purple-400 mt-1">Recently active</p>
              </div>
              <div className="text-4xl">⚡</div>
            </div>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-300 text-sm">Assessments Completed</p>
                <p className="text-3xl font-bold text-purple-200">{metrics?.assessments_completed || 0}</p>
                <p className="text-sm text-purple-400 mt-1">Total submissions</p>
              </div>
              <div className="text-4xl">📝</div>
            </div>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-300 text-sm">Coding Submissions</p>
                <p className="text-3xl font-bold text-purple-200">{metrics?.coding_submissions || 0}</p>
                <p className="text-sm text-purple-400 mt-1">Code solutions</p>
              </div>
              <div className="text-4xl">💻</div>
            </div>
          </Card>
        </motion.div>
      </div>

      {/* Recent Activity and Registration Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Recent Activity Feed */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.5 }}
        >
          <Card className="p-6">
            <h3 className="text-xl font-bold text-purple-200 mb-4">Recent Activity</h3>
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {recentActivities.length > 0 ? (
                recentActivities.map((activity, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.6 + index * 0.1 }}
                    className="flex items-start space-x-3 p-3 rounded-lg bg-purple-900/20 border border-purple-500/30"
                  >
                    <span className="text-2xl">{getActivityIcon(activity.type)}</span>
                    <div className="flex-1">
                      <p className={`text-sm ${getActivityColor(activity.type)}`}>
                        {activity.message}
                      </p>
                      <p className="text-xs text-purple-400 mt-1">
                        {formatTimestamp(activity.timestamp)}
                      </p>
                      {activity.score !== undefined && (
                        <p className="text-xs text-green-400 mt-1">
                          Score: {activity.score}/{activity.total}
                        </p>
                      )}
                    </div>
                  </motion.div>
                ))
              ) : (
                <p className="text-purple-400 text-center py-4">No recent activity</p>
              )}
            </div>
          </Card>
        </motion.div>

        {/* User Registration Chart */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.5 }}
        >
          <Card className="p-6">
            <h3 className="text-xl font-bold text-purple-200 mb-4">User Registration (30 days)</h3>
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {registrationData.length > 0 ? (
                registrationData.slice(-7).map((data, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.6 + index * 0.1 }}
                    className="flex items-center justify-between p-3 rounded-lg bg-purple-900/20 border border-purple-500/30"
                  >
                    <div>
                      <p className="text-sm text-purple-200">{data.date}</p>
                      <div className="flex space-x-4 mt-1 text-xs">
                        <span className="text-green-400">{data.students} Students</span>
                        <span className="text-blue-400">{data.teachers} Teachers</span>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-bold text-purple-200">{data.total}</p>
                      <p className="text-xs text-purple-400">Total</p>
                    </div>
                  </motion.div>
                ))
              ) : (
                <p className="text-purple-400 text-center py-4">No registration data</p>
              )}
            </div>
          </Card>
        </motion.div>
      </div>
    </div>
  );
};

export default AdminMetrics;
