"use client"

import React, { useState, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Bell, X, Clock, CheckCircle, AlertCircle, Users } from "lucide-react"
import { useAuth } from "../hooks/useAuth"
import api from "../utils/api"

interface Notification {
  id: string
  type: "assessment_assigned" | "assessment_due" | "result_available" | "batch_assignment" | "batch_removal"
  title: string
  message: string
  assessment_id?: string
  batch_id?: string
  teacher_id?: string
  created_at: string
  is_read: boolean
}

const NotificationBar: React.FC = () => {
  const { user } = useAuth()
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [isOpen, setIsOpen] = useState(false)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (user?.role === "student") {
      fetchNotifications()
    }
  }, [user])

  const fetchNotifications = async () => {
    try {
      setLoading(true)
      const response = await api.get(`/api/assessments/notifications`)
      setNotifications(response.data || [])
    } catch (error) {
      console.error("Failed to fetch notifications:", error)
    } finally {
      setLoading(false)
    }
  }

  const markAsRead = async (notificationId: string) => {
    try {
      await api.patch(`/api/assessments/notifications/${notificationId}/read`)
      setNotifications((prev) =>
        prev.map((notif) => (notif.id === notificationId ? { ...notif, is_read: true } : notif)),
      )
    } catch (error) {
      console.error("Failed to mark notification as read:", error)
    }
  }

  const handleNotificationClick = async (notification: Notification) => {
    if (!notification.is_read) {
      await markAsRead(notification.id)
    }

    if (notification.type === "assessment_assigned" && notification.assessment_id) {
      // Navigate to test interface
      window.location.href = `/test/${notification.assessment_id}`
    }
  }

  // Retained all notification types from Code A
  const getNotificationIcon = (type: string) => {
    switch (type) {
      case "assessment_assigned":
        return <Bell className="w-5 h-5 text-blue-400" />
      case "assessment_due":
        return <Clock className="w-5 h-5 text-orange-400" />
      case "result_available":
        return <CheckCircle className="w-5 h-5 text-green-400" />
      case "batch_assignment":
        return <Users className="w-5 h-5 text-green-400" />
      case "batch_removal":
        return <Users className="w-5 h-5 text-red-400" />
      default:
        return <AlertCircle className="w-5 h-5 text-blue-400" />
    }
  }
  
  // Retained all notification color logic from Code A
  const getNotificationColor = (type: string) => {
    switch (type) {
      case "assessment_assigned":
        return "border-blue-500/30 bg-blue-900/20"
      case "assessment_due":
        return "border-orange-500/30 bg-orange-900/20"
      case "result_available":
        return "border-green-500/30 bg-green-900/20"
      case "batch_assignment":
        return "border-green-500/30 bg-green-900/20"
      case "batch_removal":
        return "border-red-500/30 bg-red-900/20"
      default:
        return "border-blue-500/30 bg-blue-900/20"
    }
  }

  const unreadCount = notifications.filter((n) => !n.is_read).length

  if (user?.role !== "student") return null

  return (
    <div className="fixed top-20 right-4 z-40">
      {/* Notification Bell (Styled like Code B) */}
      <motion.button
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-3 rounded-full shadow-soft transition-colors bg-primary hover:opacity-95"
      >
        <Bell className="w-6 h-6 text-on-primary" />
        {unreadCount > 0 && (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-6 h-6 flex items-center justify-center font-bold"
          >
            {unreadCount}
          </motion.div>
        )}
      </motion.button>

      {/* Notification Panel (Styled like Code B) */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -20, scale: 0.95 }}
            className="absolute top-16 right-0 w-80 bg-surface rounded-lg shadow-soft border border-base max-h-96 overflow-hidden"
          >
            <div className="p-4 border-b border-base">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-fg">Notifications</h3>
                <button
                  onClick={() => setIsOpen(false)}
                  className="text-muted-fg hover:text-fg transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>

            <div className="max-h-80 overflow-y-auto">
              {loading ? (
                <div className="p-4 text-center text-muted-fg">Loading notifications...</div>
              ) : notifications.length === 0 ? (
                // Added better empty state handling from Code B
                <div className="p-4 text-center text-muted-fg">No notifications yet</div>
              ) : (
                <div className="space-y-2 p-2">
                  {notifications.map((notification) => (
                    <motion.div
                      key={notification.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      className={`p-3 rounded-lg border cursor-pointer transition-all hover:bg-blue-800/50 ${
                        notification.is_read ? "opacity-60" : "opacity-100"
                      } ${getNotificationColor(notification.type)}`}
                      onClick={() => handleNotificationClick(notification)}
                    >
                      <div className="flex items-start space-x-3">
                        {getNotificationIcon(notification.type)}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between">
                            <h4 className={`text-sm font-medium ${
                                notification.is_read ? "text-blue-300" : "text-blue-200"
                              }`}
                            >
                              {notification.title}
                            </h4>
                            {!notification.is_read && (
                              <div className="w-2 h-2 bg-blue-400 rounded-full flex-shrink-0" />
                            )}
                          </div>
                          <p className="text-xs text-blue-400 mt-1">
                            {notification.message}
                          </p>
                          <p className="text-xs text-blue-500 mt-1">
                            {new Date(notification.created_at).toLocaleString()}
                          </p>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default NotificationBar