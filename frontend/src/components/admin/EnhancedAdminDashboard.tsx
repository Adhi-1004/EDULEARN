"use client"

/**
 * Enhanced Admin Dashboard
 * Comprehensive platform management and oversight
 */
import type React from "react"
import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import {
  Users,
  BarChart3,
  BookOpen,
  Settings,
  Shield,
  Activity,
  TrendingUp,
  CheckCircle,
  Clock,
  Zap,
  RefreshCw,
} from "lucide-react"
import { useToast } from "../../contexts/ToastContext"
import { useAuth } from "../../hooks/useAuth"
import UserManagement from "./UserManagement"
import SystemAnalytics from "./SystemAnalytics"
import ContentOversight from "./ContentOversight"
import Card from "../ui/Card"
import Button from "../ui/Button"
import LoadingSpinner from "../ui/LoadingSpinner"
import api from "../../utils/api"

interface DashboardStats {
  total_users: number
  active_users_today: number
  active_users_week: number
  total_teachers: number
  total_students: number
  total_assessments: number
  platform_health_score: number
  user_engagement_rate: number
  pending_reviews: number
  system_alerts: number
}

const EnhancedAdminDashboard: React.FC = () => {
  const { user } = useAuth()
  const { success, error: showError } = useToast()
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<"overview" | "users" | "analytics" | "content" | "settings">("overview")
  const [refreshKey, setRefreshKey] = useState(0)

  // Fetch dashboard stats
  const fetchStats = async () => {
    try {
      setLoading(true)
      const response = await api.get("/admin/analytics/platform")
      setStats(response.data)
      console.log("📊 [ADMIN] Dashboard stats loaded:", response.data)
    } catch (err: any) {
      console.error("❌ [ADMIN] Error fetching stats:", err)
      showError("Failed to fetch dashboard stats", err.response?.data?.detail || "Unknown error")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (user) {
      fetchStats()
    }
  }, [user, refreshKey])

  const getHealthColor = (score: number) => {
    if (score >= 80) return "text-green-600 dark:text-green-400"
    if (score >= 60) return "text-yellow-600 dark:text-yellow-400"
    return "text-red-600 dark:text-red-400"
  }

  const getHealthBg = (score: number) => {
    if (score >= 80) return "bg-green-100 dark:bg-green-900/20"
    if (score >= 60) return "bg-yellow-100 dark:bg-yellow-900/20"
    return "bg-red-100 dark:bg-red-900/20"
  }

  const handleRefresh = () => {
    setRefreshKey((prev) => prev + 1)
    success("Dashboard refreshed successfully")
  }

  if (!user) {
    return (
      <div className="min-h-screen pt-20 px-4 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-foreground mb-4">Loading...</h1>
          <p className="text-muted-foreground">Please wait while we load your dashboard.</p>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="min-h-screen pt-20 px-4 flex items-center justify-center">
        <div className="text-center">
          <LoadingSpinner size="lg" />
          <h1 className="text-2xl font-bold text-foreground mb-4 mt-4">Loading Admin Dashboard...</h1>
          <p className="text-muted-foreground">Please wait while we load your comprehensive admin panel.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen pt-20 px-4">
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4 mb-8"
        >
          <div>
            <h1 className="text-4xl font-bold text-foreground mb-2">Admin Dashboard</h1>
            <p className="text-muted-foreground text-lg">Comprehensive platform management and oversight</p>
            <div className="flex items-center mt-2 text-muted-foreground">
              <Clock className="h-4 w-4 mr-2" />
              <span className="text-sm">Last updated: {new Date().toLocaleTimeString()}</span>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <Button onClick={handleRefresh} variant="secondary" className="flex items-center gap-2">
              <RefreshCw className="h-4 w-4" />
              Refresh
            </Button>

            <div className="flex items-center text-foreground">
              <div className="w-3 h-3 bg-green-400 rounded-full mr-2 animate-pulse"></div>
              <span className="text-sm">System Online</span>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="mb-8"
        >
          <div className="bg-card rounded-xl p-2 border border-border">
            <nav className="flex space-x-2 overflow-x-auto">
              {[
                { id: "overview", label: "Overview", icon: BarChart3, color: "blue" },
                { id: "users", label: "User Management", icon: Users, color: "blue" },
                { id: "analytics", label: "System Analytics", icon: TrendingUp, color: "blue" },
                { id: "content", label: "Content Oversight", icon: BookOpen, color: "blue" },
                { id: "settings", label: "Settings", icon: Settings, color: "blue" },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`flex items-center gap-2 px-4 py-3 rounded-lg font-medium text-sm whitespace-nowrap transition-all duration-200 ${
                    activeTab === tab.id
                      ? `bg-${tab.color}-500 text-white shadow-lg`
                      : "text-foreground hover:text-white hover:bg-card"
                  }`}
                >
                  <tab.icon className="h-4 w-4" />
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>
        </motion.div>

        {activeTab === "overview" && stats && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="space-y-8"
          >
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
                <Card className="bg-card rounded-xl p-2 border border-border hover:bg-card-hover transition-all duration-300">
                  <div className="flex items-center">
                    <div className="p-3 bg-blue-500/20 rounded-xl">
                      <Users className="h-6 w-6 text-blue-400" />
                    </div>
                    <div className="ml-4">
                      <p className="text-sm font-medium text-foreground">Total Users</p>
                      <p className="text-2xl font-bold text-foreground">{(stats.total_users || 0).toLocaleString()}</p>
                      <p className="text-xs text-muted-foreground">
                        {stats.total_teachers || 0} teachers, {stats.total_students || 0} students
                      </p>
                    </div>
                  </div>
                </Card>
              </motion.div>

              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
                <Card className="bg-card rounded-xl p-2 border border-border hover:bg-card-hover transition-all duration-300">
                  <div className="flex items-center">
                    <div className="p-3 bg-green-500/20 rounded-xl">
                      <Activity className="h-6 w-6 text-green-400" />
                    </div>
                    <div className="ml-4">
                      <p className="text-sm font-medium text-foreground">Active Today</p>
                      <p className="text-2xl font-bold text-foreground">
                        {(stats.active_users_today || 0).toLocaleString()}
                      </p>
                      <p className="text-xs text-muted-foreground">{stats.active_users_week || 0} this week</p>
                    </div>
                  </div>
                </Card>
              </motion.div>

              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
                <Card className="bg-card rounded-xl p-2 border border-border hover:bg-card-hover transition-all duration-300">
                  <div className="flex items-center">
                    <div className="p-3 bg-blue-500/20 rounded-xl">
                      <BookOpen className="h-6 w-6 text-blue-400" />
                    </div>
                    <div className="ml-4">
                      <p className="text-sm font-medium text-foreground">Total Content</p>
                      <p className="text-2xl font-bold text-foreground">
                        {(stats.total_assessments || 0).toLocaleString()}
                      </p>
                      <p className="text-xs text-muted-foreground">Assessments and materials</p>
                    </div>
                  </div>
                </Card>
              </motion.div>

              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
                <Card className="bg-card rounded-xl p-2 border border-border hover:bg-card-hover transition-all duration-300">
                  <div className="flex items-center">
                    <div className={`p-3 rounded-xl ${getHealthBg(stats.platform_health_score || 0)}`}>
                      <Zap className={`h-6 w-6 ${getHealthColor(stats.platform_health_score || 0)}`} />
                    </div>
                    <div className="ml-4">
                      <p className="text-sm font-medium text-foreground">Platform Health</p>
                      <p className={`text-2xl font-bold ${getHealthColor(stats.platform_health_score || 0)}`}>
                        {(stats.platform_health_score || 0).toFixed(1)}%
                      </p>
                      <p className="text-xs text-muted-foreground">Overall system health</p>
                    </div>
                  </div>
                </Card>
              </motion.div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
                <Card className="bg-card rounded-xl p-2 border border-border hover:bg-card-hover transition-all duration-300">
                  <h3 className="text-lg font-semibold text-foreground mb-4">User Engagement</h3>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-foreground">Engagement Rate</span>
                      <span className="text-sm font-medium text-foreground">
                        {(stats.user_engagement_rate || 0).toFixed(1)}%
                      </span>
                    </div>
                    <div className="w-full bg-card rounded-full h-2">
                      <div
                        className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${Math.min(stats.user_engagement_rate || 0, 100)}%` }}
                      ></div>
                    </div>

                    <div className="flex justify-between items-center">
                      <span className="text-sm text-foreground">Active Users</span>
                      <span className="text-sm font-medium text-foreground">{stats.active_users_today || 0} today</span>
                    </div>
                  </div>
                </Card>
              </motion.div>

              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}>
                <Card className="bg-card rounded-xl p-2 border border-border hover:bg-card-hover transition-all duration-300">
                  <h3 className="text-lg font-semibold text-foreground mb-4">System Status</h3>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <CheckCircle className="h-5 w-5 text-green-400 mr-2" />
                        <span className="text-sm text-foreground">System Online</span>
                      </div>
                      <span className="text-sm font-medium text-green-400">Operational</span>
                    </div>

                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <Shield className="h-5 w-5 text-blue-400 mr-2" />
                        <span className="text-sm text-foreground">Security</span>
                      </div>
                      <span className="text-sm font-medium text-blue-400">Secure</span>
                    </div>

                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <Activity className="h-5 w-5 text-blue-400 mr-2" />
                        <span className="text-sm text-foreground">Performance</span>
                      </div>
                      <span className="text-sm font-medium text-blue-400">Optimal</span>
                    </div>
                  </div>
                </Card>
              </motion.div>
            </div>

            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.7 }}>
              <Card className="bg-card rounded-xl p-2 border border-border hover:bg-card-hover transition-all duration-300">
                <h3 className="text-lg font-semibold text-foreground mb-4">Quick Actions</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  <button
                    onClick={() => setActiveTab("users")}
                    className="flex items-center p-4 border border-border rounded-lg hover:bg-card-hover transition-all duration-200 group"
                  >
                    <Users className="h-5 w-5 text-blue-400 mr-3 group-hover:scale-110 transition-transform" />
                    <div className="text-left">
                      <div className="font-medium text-foreground">Manage Users</div>
                      <div className="text-sm text-muted-foreground">View and edit users</div>
                    </div>
                  </button>

                  <button
                    onClick={() => setActiveTab("analytics")}
                    className="flex items-center p-4 border border-border rounded-lg hover:bg-card-hover transition-all duration-200 group"
                  >
                    <BarChart3 className="h-5 w-5 text-green-400 mr-3 group-hover:scale-110 transition-transform" />
                    <div className="text-left">
                      <div className="font-medium text-foreground">View Analytics</div>
                      <div className="text-sm text-muted-foreground">Platform insights</div>
                    </div>
                  </button>

                  <button
                    onClick={() => setActiveTab("content")}
                    className="flex items-center p-4 border border-border rounded-lg hover:bg-card-hover transition-all duration-200 group"
                  >
                    <BookOpen className="h-5 w-5 text-blue-400 mr-3 group-hover:scale-110 transition-transform" />
                    <div className="text-left">
                      <div className="font-medium text-foreground">Content Library</div>
                      <div className="text-sm text-muted-foreground">Manage content</div>
                    </div>
                  </button>

                  <button
                    onClick={() => setActiveTab("settings")}
                    className="flex items-center p-4 border border-border rounded-lg hover:bg-card-hover transition-all duration-200 group"
                  >
                    <Settings className="h-5 w-5 text-gray-400 mr-3 group-hover:scale-110 transition-transform" />
                    <div className="text-left">
                      <div className="font-medium text-foreground">Settings</div>
                      <div className="text-sm text-muted-foreground">Platform settings</div>
                    </div>
                  </button>
                </div>
              </Card>
            </motion.div>
          </motion.div>
        )}

        {activeTab === "users" && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <UserManagement />
          </motion.div>
        )}

        {activeTab === "analytics" && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <SystemAnalytics />
          </motion.div>
        )}

        {activeTab === "content" && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <ContentOversight />
          </motion.div>
        )}

        {activeTab === "settings" && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="space-y-6"
          >
            <Card className="bg-card rounded-xl p-2 border border-border hover:bg-card-hover transition-all duration-300">
              <h3 className="text-lg font-semibold text-foreground mb-4">Platform Settings</h3>
              <p className="text-muted-foreground">
                Platform settings and configuration options will be available here.
              </p>
            </Card>
          </motion.div>
        )}
      </div>
    </div>
  )
}

export default EnhancedAdminDashboard
