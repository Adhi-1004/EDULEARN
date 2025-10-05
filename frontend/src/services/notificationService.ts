/**
 * Notification Service
 * Handles all notification-related API calls
 */
import api from '../utils/api';

export interface Notification {
  _id: string;
  user_id: string;
  message: string;
  read: boolean;
  timestamp: string;
  notification_type: string;
  related_id?: string;
}

export interface NotificationResponse {
  notifications: Notification[];
  unread_count: number;
}

export interface UnreadCountResponse {
  unread_count: number;
}

/**
 * Get all notifications for the current user
 */
export const getNotifications = async (): Promise<NotificationResponse> => {
  try {
    const response = await api.get('/notifications/');
    return response.data;
  } catch (error) {
    console.error('Error fetching notifications:', error);
    throw error;
  }
};

/**
 * Mark a specific notification as read
 */
export const markNotificationAsRead = async (notificationId: string): Promise<void> => {
  try {
    await api.post(`/notifications/${notificationId}/read`);
  } catch (error) {
    console.error('Error marking notification as read:', error);
    throw error;
  }
};

/**
 * Mark all notifications as read for the current user
 */
export const markAllNotificationsAsRead = async (): Promise<void> => {
  try {
    await api.post('/notifications/mark-all-read');
  } catch (error) {
    console.error('Error marking all notifications as read:', error);
    throw error;
  }
};

/**
 * Delete a specific notification
 */
export const deleteNotification = async (notificationId: string): Promise<void> => {
  try {
    await api.delete(`/notifications/${notificationId}`);
  } catch (error) {
    console.error('Error deleting notification:', error);
    throw error;
  }
};

/**
 * Get the count of unread notifications
 */
export const getUnreadCount = async (): Promise<number> => {
  try {
    const response = await api.get('/notifications/unread-count');
    return response.data.unread_count;
  } catch (error) {
    console.error('Error fetching unread count:', error);
    return 0;
  }
};

/**
 * Format notification timestamp for display
 */
export const formatNotificationTime = (timestamp: string): string => {
  const date = new Date(timestamp);
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);
  
  if (diffInSeconds < 60) {
    return 'Just now';
  } else if (diffInSeconds < 3600) {
    const minutes = Math.floor(diffInSeconds / 60);
    return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
  } else if (diffInSeconds < 86400) {
    const hours = Math.floor(diffInSeconds / 3600);
    return `${hours} hour${hours > 1 ? 's' : ''} ago`;
  } else if (diffInSeconds < 604800) {
    const days = Math.floor(diffInSeconds / 86400);
    return `${days} day${days > 1 ? 's' : ''} ago`;
  } else {
    return date.toLocaleDateString();
  }
};

/**
 * Get notification type display name
 */
export const getNotificationTypeDisplayName = (type: string): string => {
  const typeMap: { [key: string]: string } = {
    'general': 'General',
    'batch_added': 'Batch Assignment',
    'batch_assignment': 'Batch Assignment',
    'batch_removal': 'Batch Removal',
    'assessment_created': 'New Assessment',
    'assessment_completed': 'Assessment Completed',
    'grade_released': 'Grade Released',
    'system': 'System'
  };
  
  return typeMap[type] || 'Notification';
};

/**
 * Get notification icon based on type
 */
export const getNotificationIcon = (type: string): string => {
  const iconMap: { [key: string]: string } = {
    'general': '📢',
    'batch_added': '👥',
    'batch_assignment': '👥',
    'batch_removal': '👥',
    'assessment_created': '📝',
    'assessment_completed': '✅',
    'grade_released': '🎯',
    'system': '⚙️'
  };
  
  return iconMap[type] || '📢';
};
