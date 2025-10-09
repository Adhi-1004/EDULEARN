"use client"

import React, { useState, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { useToast } from "../../contexts/ToastContext"
import api from "../../utils/api"

interface Notification {
  id: string
  type: "info" | "success" | "warning" | "error"
  title: string
  message: string
  priority: "low" | "normal" | "high" | "urgent"
  is_read: boolean
  created_at: string
  read_at?: string
}

interface RealTimeNotificationsProps {
  isOpen: boolean
  onClose: () => void
}

const RealTimeNotifications: React.FC<RealTimeNotificationsProps> = ({ isOpen, onClose }) => {
  const { success: showSuccess } = useToast()
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [loading, setLoading] = useState(false)
  const [unreadCount, setUnreadCount] = useState(0)

  useEffect(() => {
    if (isOpen) {
      fetchNotifications()
      // Set up polling for real-time updates
      const interval = setInterval(fetchNotifications, 10000) // Poll every 10 seconds
      return () => clearInterval(interval)
    }
  }, [isOpen])

  const fetchNotifications = async () => {
    try {
      setLoading(true)
      const response = await api.get("/api/notifications/")
      
      if (response.data.notifications) {
        setNotifications(response.data.notifications)
        setUnreadCount(response.data.unread_count || 0)
      }
    } catch (err) {
      console.error("❌ [NOTIFICATIONS] Failed to fetch notifications:", err)
    } finally {
      setLoading(false)
    }
  }

  const markAsRead = async (notificationId: string) => {
    try {
      await api.put(`/api/notifications/${notificationId}/read`)
      
      // Update local state
      setNotifications(prev => 
        prev.map(notification => 
          notification.id === notificationId 
            ? { ...notification, is_read: true, read_at: new Date().toISOString() }
            : notification
        )
      )
      setUnreadCount(prev => Math.max(0, prev - 1))
      
      showSuccess("Success", "Notification marked as read")
    } catch (err) {
      console.error("❌ [NOTIFICATIONS] Failed to mark notification as read:", err)
    }
  }

  const markAllAsRead = async () => {
    try {
      await api.put("/api/notifications/mark-all-read")
      
      // Update local state
      setNotifications(prev => 
        prev.map(notification => ({ 
          ...notification, 
          is_read: true, 
          read_at: new Date().toISOString() 
        }))
      )
      setUnreadCount(0)
      
      showSuccess("Success", "All notifications marked as read")
    } catch (err) {
      console.error("❌ [NOTIFICATIONS] Failed to mark all notifications as read:", err)
    }
  }

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case "success":
        return "✅"
      case "warning":
        return "⚠️"
      case "error":
        return "❌"
      default:
        return "ℹ️"
    }
  }

  const getNotificationColor = (type: string) => {
    switch (type) {
      case "success":
        return "border-green-500/30 bg-green-900/20"
      case "warning":
        return "border-yellow-500/30 bg-yellow-900/20"
      case "error":
        return "border-red-500/30 bg-red-900/20"
      default:
        return "border-blue-500/30 bg-blue-900/20"
    }
  }

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000)
    
    if (diffInSeconds < 60) return "Just now"
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`
    return `${Math.floor(diffInSeconds / 86400)}d ago`
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="bg-blue-900 rounded-lg max-w-2xl w-full max-h-[80vh] overflow-hidden"
      >
        {/* Header */}
        <div className="p-6 border-b border-blue-500/30">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-2xl font-bold text-blue-200 mb-2">Notifications</h2>
              <p className="text-blue-300">
                {unreadCount > 0 ? `${unreadCount} unread notifications` : "All caught up!"}
              </p>
            </div>
            <div className="flex items-center gap-2">
              {unreadCount > 0 && (
                <button
                  onClick={markAllAsRead}
                  className="px-3 py-1 bg-blue-500/20 border border-blue-500/30 rounded-md text-blue-300 text-sm hover:bg-blue-500/30 transition-colors"
                >
                  Mark All Read
                </button>
              )}
              <button
                onClick={onClose}
                className="p-2 hover:bg-blue-800/30 rounded-md transition-colors"
              >
                <svg className="w-5 h-5 text-blue-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(80vh-140px)]">
          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-400 mx-auto mb-4"></div>
              <p className="text-blue-300">Loading notifications...</p>
            </div>
          ) : notifications.length === 0 ? (
            <div className="text-center py-8">
              <div className="text-6xl mb-4">🔔</div>
              <h3 className="text-xl font-semibold text-blue-200 mb-2">No notifications</h3>
              <p className="text-blue-300">You're all caught up! Check back later for updates.</p>
            </div>
          ) : (
            <div className="space-y-4">
              <AnimatePresence>
                {notifications.map((notification, index) => (
                  <motion.div
                    key={notification.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ delay: index * 0.05 }}
                    className={`border rounded-lg p-4 transition-all ${
                      notification.is_read 
                        ? "opacity-60" 
                        : "ring-2 ring-blue-500/20"
                    } ${getNotificationColor(notification.type)}`}
                  >
                    <div className="flex items-start gap-3">
                      <div className="text-2xl flex-shrink-0">
                        {getNotificationIcon(notification.type)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between mb-2">
                          <h4 className="font-semibold text-blue-200 text-sm">
                            {notification.title}
                          </h4>
                          <div className="flex items-center gap-2 ml-4">
                            <span className="text-blue-400 text-xs">
                              {formatTimeAgo(notification.created_at)}
                            </span>
                            {!notification.is_read && (
                              <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                            )}
                          </div>
                        </div>
                        <p className="text-blue-300 text-sm mb-3 leading-relaxed">
                          {notification.message}
                        </p>
                        <div className="flex items-center justify-between">
                          <span className={`text-xs px-2 py-1 rounded-full ${
                            notification.priority === "urgent" 
                              ? "bg-red-500/20 text-red-300" 
                              : notification.priority === "high"
                              ? "bg-yellow-500/20 text-yellow-300"
                              : "bg-blue-500/20 text-blue-300"
                          }`}>
                            {notification.priority}
                          </span>
                          {!notification.is_read && (
                            <button
                              onClick={() => markAsRead(notification.id)}
                              className="text-blue-400 hover:text-blue-300 text-xs underline transition-colors"
                            >
                              Mark as read
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          )}
        </div>
      </motion.div>
    </div>
  )
}

export default RealTimeNotifications
