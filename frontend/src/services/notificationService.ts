"use client"

/**
 * Notification Service
 * Handles all notification-related API calls and provides a stateful hook for components.
 */
import api from "../utils/api"
import { useState, useEffect, useCallback } from "react"

// --- TYPE DEFINITIONS (from Code A) ---
export interface Notification {
  _id: string
  user_id: string
  message: string
  read: boolean
  timestamp: string
  notification_type: string
  related_id?: string
}

export interface NotificationResponse {
  notifications: Notification[]
  unread_count: number
}

// --- MODERN REACT HOOK (Pattern from Code B) ---

type UseNotificationsOptions = {
  pollInterval?: number // Polling interval in milliseconds
}

/**
 * A stateful hook to manage notifications.
 * It handles fetching, state management (loading, error), and provides actions
 * to interact with the notification data.
 */
export const useNotifications = (options: UseNotificationsOptions = {}) => {
  const { pollInterval = 30000 } = options // Default poll every 30 seconds

  const [notifications, setNotifications] = useState<Notification[]>([])
  const [unreadCount, setUnreadCount] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  const fetchNotifications = useCallback(async () => {
    // Don't set loading to true on background polls
    // Only on the initial fetch
    if (notifications.length === 0) {
      setLoading(true)
    }
    setError(null)
    try {
      const data = await getNotifications()
      setNotifications(data.notifications)
      setUnreadCount(data.unread_count)
    } catch (err: any) {
      setError(err)
      console.error("Hook failed to fetch notifications:", err)
    } finally {
      setLoading(false)
    }
  }, [notifications.length])

  // Effect for initial fetch and polling
  useEffect(() => {
    fetchNotifications()
    if (pollInterval > 0) {
      const intervalId = setInterval(fetchNotifications, pollInterval)
      return () => clearInterval(intervalId)
    }
  }, [fetchNotifications, pollInterval])

  const markOneAsRead = useCallback(async (notificationId: string) => {
    // Optimistically update the UI for a better UX
    setNotifications((prev) =>
      prev.map((n) => (n._id === notificationId ? { ...n, read: true } : n)),
    )
    setUnreadCount((prev) => (prev > 0 ? prev - 1 : 0))

    try {
      await markNotificationAsRead(notificationId)
    } catch (err) {
      // If API call fails, revert the state
      console.error("Failed to mark as read, reverting UI.", err)
      fetchNotifications() // Re-fetch to sync with the server
    }
  }, [fetchNotifications])

  const markAllAsRead = useCallback(async () => {
    // Optimistic UI update
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })))
    setUnreadCount(0)
    try {
      await markAllNotificationsAsRead()
    } catch (err) {
      console.error("Failed to mark all as read, reverting UI.", err)
      fetchNotifications()
    }
  }, [fetchNotifications])

  const deleteOne = useCallback(async (notificationId: string) => {
    // Optimistic UI update
    const originalNotifications = notifications;
    setNotifications((prev) => prev.filter((n) => n._id !== notificationId))
    // Recalculate unread count
    setUnreadCount(notifications.filter(n => n._id !== notificationId && !n.read).length);

    try {
      await deleteNotification(notificationId)
    } catch (err) {
      console.error("Failed to delete, reverting UI.", err)
      setNotifications(originalNotifications); // Revert on failure
    }
  }, [notifications])


  return {
    notifications,
    unreadCount,
    loading,
    error,
    refresh: fetchNotifications,
    markOneAsRead,
    markAllAsRead,
    deleteOne,
  }
}

// --- STANDALONE API FUNCTIONS (from Code A) ---

/**
 * Get all notifications for the current user
 */
export const getNotifications = async (): Promise<NotificationResponse> => {
  const response = await api.get("/notifications/")
  return response.data
}

/**
 * Mark a specific notification as read
 */
export const markNotificationAsRead = async (notificationId: string): Promise<void> => {
  await api.post(`/notifications/${notificationId}/read`)
}

/**
 * Mark all notifications as read for the current user
 */
export const markAllNotificationsAsRead = async (): Promise<void> => {
  await api.post("/notifications/mark-all-read")
}

/**
 * Delete a specific notification
 */
export const deleteNotification = async (notificationId: string): Promise<void> => {
  await api.delete(`/notifications/${notificationId}`)
}

// --- HELPER FUNCTIONS (from Code A) ---

/**
 * Format notification timestamp for display
 */
export const formatNotificationTime = (timestamp: string): string => {
  const date = new Date(timestamp)
  const now = new Date()
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000)

  if (diffInSeconds < 60) return "Just now"
  if (diffInSeconds < 3600) {
    const minutes = Math.floor(diffInSeconds / 60)
    return `${minutes} minute${minutes > 1 ? "s" : ""} ago`
  }
  if (diffInSeconds < 86400) {
    const hours = Math.floor(diffInSeconds / 3600)
    return `${hours} hour${hours > 1 ? "s" : ""} ago`
  }
  const days = Math.floor(diffInSeconds / 86400)
  return `${days} day${days > 1 ? "s" : ""} ago`
}

/**
 * Get notification icon based on type
 */
export const getNotificationIcon = (type: string): string => {
  const iconMap: { [key: string]: string } = {
    general: "📢",
    batch_assignment: "👥",
    batch_removal: "👥",
    assessment_created: "📝",
    assessment_completed: "✅",
    grade_released: "🎯",
    system: "⚙️",
  }
  return iconMap[type] || "📢"
}