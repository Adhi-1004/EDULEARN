"use client"

/**
 * System Analytics Component
 * Comprehensive platform metrics and analytics
 */
import type React from "react"
import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { Users, Activity, Award, BookOpen, BarChart3, Zap } from "lucide-react"
import { useToast } from "../../contexts/ToastContext"
import api from "../../utils/api"

interface PlatformMetrics {
  total_users: number
  active_users_today: number
  active_users_week: number
  active_users_month: number
  total_teachers: number
  total_students: number
  total_assessments: number
  total_questions: number
  total_batches: number
  platform_health_score: number
  user_engagement_rate: number
  content_completion_rate: number
}

interface ContentAnalytics {
  content_id: string
  title: string
  type: string
  creator: string
  views: number
  completions: number
  average_score: number
  popularity_score: number
  difficulty_rating: number
  last_updated: string
}

interface TeacherPerformance {
  teacher_id: string
  name: string
  email: string
  total_students: number
  total_batches: number
  total_assessments_created: number
  average_student_score: number
  student_satisfaction: number
  content_quality_score: number
  engagement_score: number
}

const SystemAnalytics: React.FC = () => {
  const { error } = useToast()
  const [metrics, setMetrics] = useState<PlatformMetrics | null>(null)
  const [contentAnalytics, setContentAnalytics] = useState<ContentAnalytics[]>([])
  const [teacherPerformance, setTeacherPerformance] = useState<TeacherPerformance[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<"overview" | "content" | "teachers">("overview")

  // Fetch platform metrics
  const fetchMetrics = async () => {
    try {
      const response = await api.get("/api/admin/analytics/platform")
      setMetrics(response.data)
    } catch (err: any) {
      error("Failed to fetch platform metrics", err.response?.data?.detail || "Unknown error")
    }
  }

  // Fetch content analytics
  const fetchContentAnalytics = async () => {
    try {
      const response = await api.get("/api/admin/analytics/content")
      setContentAnalytics(response.data.content_analytics || [])
    } catch (err: any) {
      error("Failed to fetch content analytics", err.response?.data?.detail || "Unknown error")
      setContentAnalytics([]) // Set empty array on error
    }
  }

  // Fetch teacher performance
  const fetchTeacherPerformance = async () => {
    try {
      const response = await api.get("/api/admin/analytics/teachers")
      setTeacherPerformance(response.data.teacher_performance || [])
    } catch (err: any) {
      error("Failed to fetch teacher performance", err.response?.data?.detail || "Unknown error")
      setTeacherPerformance([]) // Set empty array on error
    }
  }

  useEffect(() => {
    const fetchAllData = async () => {
      setLoading(true)
      await Promise.all([fetchMetrics(), fetchContentAnalytics(), fetchTeacherPerformance()])
      setLoading(false)
    }

    fetchAllData()
  }, [])

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

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">System Analytics</h2>
        <p className="text-gray-600 dark:text-gray-400">Comprehensive platform metrics and insights</p>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200 dark:border-gray-700">
        <nav className="-mb-px flex space-x-8">
          {[
            {
              id: "overview",
              label: "Overview",
              icon: BarChart3,
            },
            {
              id: "content",
              label: "Content Analytics",
              icon: BookOpen,
            },
            {
              id: "teachers",
              label: "Teacher Performance",
              icon: Award,
            },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? "border-blue-500 text-blue-600 dark:text-blue-400"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300"
              }`}
            >
              <tab.icon className="h-4 w-4" />
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Overview Tab */}
      {activeTab === "overview" && metrics && (
        <div className="space-y-6">
          {/* Key Metrics Cards */}
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
                    {(metrics.total_users || 0).toLocaleString()}
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
                    {(metrics.active_users_today || 0).toLocaleString()}
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
                <div className="p-2 bg-blue-100 dark:bg-blue-900/20 rounded-lg">
                  <BookOpen className="h-6 w-6 text-blue-600 dark:text-blue-400" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Content</p>
                  <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                    {(metrics.total_assessments || 0).toLocaleString()}
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
                <div className={`p-2 rounded-lg ${getHealthBg(metrics.platform_health_score || 0)}`}>
                  <Zap className={`h-6 w-6 ${getHealthColor(metrics.platform_health_score || 0)}`} />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Platform Health</p>
                  <p className={`text-2xl font-semibold ${getHealthColor(metrics.platform_health_score || 0)}`}>
                    {(metrics.platform_health_score || 0).toFixed(1)}%
                  </p>
                </div>
              </div>
            </motion.div>
          </div>

          {/* Detailed Metrics */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">User Engagement</h3>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Engagement Rate</span>
                  <span className="text-sm font-medium text-gray-900 dark:text-white">
                    {(metrics.user_engagement_rate || 0).toFixed(1)}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${Math.min(metrics.user_engagement_rate || 0, 100)}%` }}
                  ></div>
                </div>

                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Content Completion</span>
                  <span className="text-sm font-medium text-gray-900 dark:text-white">
                    {(metrics.content_completion_rate || 0).toFixed(1)}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-green-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${Math.min(metrics.content_completion_rate || 0, 100)}%` }}
                  ></div>
                </div>
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">User Distribution</h3>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <div className="flex items-center">
                    <div className="w-3 h-3 bg-blue-500 rounded-full mr-2"></div>
                    <span className="text-sm text-gray-600 dark:text-gray-400">Students</span>
                  </div>
                  <span className="text-sm font-medium text-gray-900 dark:text-white">
                    {(metrics.total_students || 0).toLocaleString()}
                  </span>
                </div>

                <div className="flex justify-between items-center">
                  <div className="flex items-center">
                    <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
                    <span className="text-sm text-gray-600 dark:text-gray-400">Teachers</span>
                  </div>
                  <span className="text-sm font-medium text-gray-900 dark:text-white">
                    {(metrics.total_teachers || 0).toLocaleString()}
                  </span>
                </div>

                <div className="flex justify-between items-center">
                  <div className="flex items-center">
                    <div className="w-3 h-3 bg-blue-500 rounded-full mr-2"></div>
                    <span className="text-sm text-gray-600 dark:text-gray-400">Batches</span>
                  </div>
                  <span className="text-sm font-medium text-gray-900 dark:text-white">
                    {(metrics.total_batches || 0).toLocaleString()}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Activity Timeline */}
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Activity Overview</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">{metrics.active_users_today}</div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Active Today</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600 dark:text-green-400">{metrics.active_users_week}</div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Active This Week</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">{metrics.active_users_month}</div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Active This Month</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Content Analytics Tab */}
      {activeTab === "content" && (
        <div className="space-y-6">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Content Performance</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead className="bg-gray-50 dark:bg-gray-700">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Content
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Creator
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Views
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Completions
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Avg Score
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Popularity
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                  {(contentAnalytics || []).map((content) => (
                    <tr key={content.content_id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div>
                          <div className="text-sm font-medium text-gray-900 dark:text-white">{content.title}</div>
                          <div className="text-sm text-gray-500 dark:text-gray-400">{content.type}</div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                        {content.creator}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                        {(content.views || 0).toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                        {(content.completions || 0).toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                        {(content.average_score || 0).toFixed(1)}%
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="w-16 bg-gray-200 dark:bg-gray-600 rounded-full h-2 mr-2">
                            <div
                              className="h-2 rounded-full"
                              style={{
                                width: `${Math.min(content.popularity_score || 0, 100)}%`,
                                background: "linear-gradient(90deg, var(--primary), var(--accent))",
                              }}
                            ></div>
                          </div>
                          <span className="text-sm text-gray-600 dark:text-gray-400">
                            {(content.popularity_score || 0).toFixed(1)}%
                          </span>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Teacher Performance Tab */}
      {activeTab === "teachers" && (
        <div className="space-y-6">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Teacher Performance</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead className="bg-gray-50 dark:bg-gray-700">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Teacher
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Students
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Batches
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Content
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Avg Score
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Satisfaction
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Quality
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                  {(teacherPerformance || []).map((teacher) => (
                    <tr key={teacher.teacher_id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div>
                          <div className="text-sm font-medium text-gray-900 dark:text-white">{teacher.name}</div>
                          <div className="text-sm text-gray-500 dark:text-gray-400">{teacher.email}</div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                        {teacher.total_students}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                        {teacher.total_batches}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                        {teacher.total_assessments_created}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                        {(teacher.average_student_score || 0).toFixed(1)}%
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="w-16 bg-gray-200 dark:bg-gray-600 rounded-full h-2 mr-2">
                            <div
                              className="h-2 rounded-full"
                              style={{
                                width: `${Math.min(teacher.student_satisfaction || 0, 100)}%`,
                                background: "linear-gradient(90deg, var(--primary), var(--accent))",
                              }}
                            ></div>
                          </div>
                          <span className="text-sm text-gray-600 dark:text-gray-400">
                            {(teacher.student_satisfaction || 0).toFixed(1)}%
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="w-16 bg-gray-200 dark:bg-gray-600 rounded-full h-2 mr-2">
                            <div
                              className="h-2 rounded-full"
                              style={{
                                width: `${Math.min(teacher.content_quality_score || 0, 100)}%`,
                                background: "linear-gradient(90deg, var(--primary), var(--accent))",
                              }}
                            ></div>
                          </div>
                          <span className="text-sm text-gray-600 dark:text-gray-400">
                            {(teacher.content_quality_score || 0).toFixed(1)}%
                          </span>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default SystemAnalytics
