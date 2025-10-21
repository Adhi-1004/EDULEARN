"use client"

/**
 * Enhanced Admin Dashboard
 * Comprehensive platform management and oversight
 */
import type React from "react"
import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { useToast } from "../../contexts/ToastContext"
import { useAuth } from "../../hooks/useAuth"
import UserManagement from "./UserManagement"
import ContentDataManager from "./ContentDataManager"
import SettingsPanel from "./SettingsPanel"
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

interface EnhancedAdminDashboardProps {
  activeTab: "users" | "content" | "settings"
  refreshKey: number
}

const EnhancedAdminDashboard: React.FC<EnhancedAdminDashboardProps> = ({ activeTab, refreshKey }) => {
  const { user } = useAuth()
  const { error: showError } = useToast()
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)

  // Fetch dashboard stats
  const fetchStats = async () => {
    try {
      setLoading(true)
      const response = await api.get("/api/admin/analytics/platform")
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
        {activeTab === "users" && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <UserManagement />
          </motion.div>
        )}

        {activeTab === "content" && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <ContentDataManager />
          </motion.div>
        )}

        {activeTab === "settings" && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <SettingsPanel />
          </motion.div>
        )}
      </div>
    </div>
  )
}

export default EnhancedAdminDashboard
