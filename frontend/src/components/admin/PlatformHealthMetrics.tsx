import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import Card from "../ui/Card";
import Button from "../ui/Button";
import LoadingSpinner from "../ui/LoadingSpinner";
import api from "../../utils/api";

interface PlatformMetrics {
  dailyActiveUsers: number;
  monthlyActiveUsers: number;
  dauMauRatio: number;
  contentCompletionRate: number;
  featureAdoption: {
    mcq: number;
    coding: number;
    assessments: number;
    aiFeatures: number;
  };
  userEngagement: {
    averageSessionTime: number;
    pagesPerSession: number;
    bounceRate: number;
  };
  contentFunnel: {
    startedAssessments: number;
    completedAssessments: number;
    completionRate: number;
  };
  systemHealth: {
    uptime: number;
    responseTime: number;
    errorRate: number;
  };
}

interface PlatformHealthMetricsProps {
  adminId: string;
}

const PlatformHealthMetrics: React.FC<PlatformHealthMetricsProps> = ({ adminId }) => {
  const [metrics, setMetrics] = useState<PlatformMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  useEffect(() => {
    fetchPlatformMetrics();
    // Set up auto-refresh every 5 minutes
    const interval = setInterval(fetchPlatformMetrics, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, [adminId]);

  const fetchPlatformMetrics = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/api/admin-dashboard/platform-metrics/${adminId}`);
      setMetrics(response.data);
      setLastUpdated(new Date());
    } catch (err) {
      console.error("Failed to fetch platform metrics:", err);
      setError("Failed to load platform metrics");
    } finally {
      setLoading(false);
    }
  };

  const getHealthColor = (value: number, thresholds: { good: number; warning: number }) => {
    if (value >= thresholds.good) return "text-green-400";
    if (value >= thresholds.warning) return "text-yellow-400";
    return "text-red-400";
  };

  const getHealthBgColor = (value: number, thresholds: { good: number; warning: number }) => {
    if (value >= thresholds.good) return "bg-green-500/20 border-green-500/30";
    if (value >= thresholds.warning) return "bg-yellow-500/20 border-yellow-500/30";
    return "bg-red-500/20 border-red-500/30";
  };

  if (loading && !metrics) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center h-64">
          <LoadingSpinner />
        </div>
      </Card>
    );
  }

  if (error && !metrics) {
    return (
      <Card className="p-6">
        <div className="text-center text-red-400">
          <p>{error}</p>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={fetchPlatformMetrics}
            className="mt-4"
          >
            Retry
          </Button>
        </div>
      </Card>
    );
  }

  if (!metrics) return null;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-purple-200 mb-2">
            📊 Platform Health & Engagement Metrics
          </h2>
          <p className="text-purple-300">
            Real-time insights into platform performance and user engagement
          </p>
        </div>
        <div className="text-right">
          <p className="text-sm text-purple-400">
            Last updated: {lastUpdated?.toLocaleTimeString()}
          </p>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={fetchPlatformMetrics}
            disabled={loading}
          >
            {loading ? <LoadingSpinner size="sm" /> : "Refresh"}
          </Button>
        </div>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* DAU/MAU Ratio */}
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-purple-200">User Engagement</h3>
            <span className="text-2xl">👥</span>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-purple-300">DAU:</span>
              <span className="text-purple-200 font-semibold">{metrics.dailyActiveUsers.toLocaleString()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-purple-300">MAU:</span>
              <span className="text-purple-200 font-semibold">{metrics.monthlyActiveUsers.toLocaleString()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-purple-300">DAU/MAU:</span>
              <span className={`font-semibold ${getHealthColor(metrics.dauMauRatio, { good: 0.2, warning: 0.1 })}`}>
                {(metrics.dauMauRatio * 100).toFixed(1)}%
              </span>
            </div>
          </div>
        </Card>

        {/* Content Completion */}
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-purple-200">Content Funnel</h3>
            <span className="text-2xl">📈</span>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-purple-300">Started:</span>
              <span className="text-purple-200 font-semibold">{metrics.contentFunnel.startedAssessments.toLocaleString()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-purple-300">Completed:</span>
              <span className="text-purple-200 font-semibold">{metrics.contentFunnel.completedAssessments.toLocaleString()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-purple-300">Rate:</span>
              <span className={`font-semibold ${getHealthColor(metrics.contentFunnel.completionRate, { good: 70, warning: 50 })}`}>
                {metrics.contentFunnel.completionRate.toFixed(1)}%
              </span>
            </div>
          </div>
        </Card>

        {/* System Health */}
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-purple-200">System Health</h3>
            <span className="text-2xl">⚡</span>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-purple-300">Uptime:</span>
              <span className={`font-semibold ${getHealthColor(metrics.systemHealth.uptime, { good: 99, warning: 95 })}`}>
                {metrics.systemHealth.uptime.toFixed(2)}%
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-purple-300">Response:</span>
              <span className={`font-semibold ${getHealthColor(1000 - metrics.systemHealth.responseTime, { good: 500, warning: 200 })}`}>
                {metrics.systemHealth.responseTime}ms
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-purple-300">Errors:</span>
              <span className={`font-semibold ${getHealthColor(100 - metrics.systemHealth.errorRate, { good: 99, warning: 95 })}`}>
                {metrics.systemHealth.errorRate.toFixed(2)}%
              </span>
            </div>
          </div>
        </Card>

        {/* User Engagement */}
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-purple-200">Engagement</h3>
            <span className="text-2xl">🎯</span>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-purple-300">Session Time:</span>
              <span className="text-purple-200 font-semibold">{Math.round(metrics.userEngagement.averageSessionTime / 60)}m</span>
            </div>
            <div className="flex justify-between">
              <span className="text-purple-300">Pages/Session:</span>
              <span className="text-purple-200 font-semibold">{metrics.userEngagement.pagesPerSession.toFixed(1)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-purple-300">Bounce Rate:</span>
              <span className={`font-semibold ${getHealthColor(100 - metrics.userEngagement.bounceRate, { good: 30, warning: 50 })}`}>
                {metrics.userEngagement.bounceRate.toFixed(1)}%
              </span>
            </div>
          </div>
        </Card>
      </div>

      {/* Feature Adoption Chart */}
      <Card className="p-6">
        <h3 className="text-xl font-semibold text-purple-200 mb-6">Feature Adoption</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {Object.entries(metrics.featureAdoption).map(([feature, adoption]) => (
            <div key={feature} className="text-center">
              <div className="text-2xl mb-2">
                {feature === 'mcq' && '📝'}
                {feature === 'coding' && '💻'}
                {feature === 'assessments' && '📊'}
                {feature === 'aiFeatures' && '🤖'}
              </div>
              <h4 className="font-semibold text-purple-200 capitalize mb-2">
                {feature === 'mcq' ? 'MCQ Tests' : 
                 feature === 'coding' ? 'Coding Problems' :
                 feature === 'assessments' ? 'Assessments' : 'AI Features'}
              </h4>
              <div className="w-full bg-purple-900/20 rounded-full h-2 mb-2">
                <div 
                  className="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full transition-all duration-500"
                  style={{ width: `${adoption}%` }}
                ></div>
              </div>
              <p className="text-sm text-purple-300">{adoption.toFixed(1)}%</p>
            </div>
          ))}
        </div>
      </Card>

      {/* Health Status Summary */}
      <Card className="p-6">
        <h3 className="text-xl font-semibold text-purple-200 mb-4">Platform Health Summary</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className={`p-4 rounded-lg border ${getHealthBgColor(metrics.dauMauRatio * 100, { good: 20, warning: 10 })}`}>
            <div className="flex items-center justify-between">
              <span className="text-purple-200 font-medium">User Engagement</span>
              <span className={`text-sm font-semibold ${getHealthColor(metrics.dauMauRatio * 100, { good: 20, warning: 10 })}`}>
                {metrics.dauMauRatio >= 0.2 ? 'Excellent' : metrics.dauMauRatio >= 0.1 ? 'Good' : 'Needs Attention'}
              </span>
            </div>
          </div>
          
          <div className={`p-4 rounded-lg border ${getHealthBgColor(metrics.contentFunnel.completionRate, { good: 70, warning: 50 })}`}>
            <div className="flex items-center justify-between">
              <span className="text-purple-200 font-medium">Content Completion</span>
              <span className={`text-sm font-semibold ${getHealthColor(metrics.contentFunnel.completionRate, { good: 70, warning: 50 })}`}>
                {metrics.contentFunnel.completionRate >= 70 ? 'Excellent' : metrics.contentFunnel.completionRate >= 50 ? 'Good' : 'Needs Attention'}
              </span>
            </div>
          </div>
          
          <div className={`p-4 rounded-lg border ${getHealthBgColor(metrics.systemHealth.uptime, { good: 99, warning: 95 })}`}>
            <div className="flex items-center justify-between">
              <span className="text-purple-200 font-medium">System Stability</span>
              <span className={`text-sm font-semibold ${getHealthColor(metrics.systemHealth.uptime, { good: 99, warning: 95 })}`}>
                {metrics.systemHealth.uptime >= 99 ? 'Excellent' : metrics.systemHealth.uptime >= 95 ? 'Good' : 'Needs Attention'}
              </span>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default PlatformHealthMetrics;
