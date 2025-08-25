import { useEffect, useState } from "react"
import { useBackend } from "../contexts/BackendContext"

const BackendNotification = () => {
  const { isOnline, isChecking, error } = useBackend()
  const [showNotification, setShowNotification] = useState(false)
  const [notificationType, setNotificationType] = useState('')

  useEffect(() => {
    if (!isChecking) {
      if (!isOnline) {
        setNotificationType('error')
        setShowNotification(true)
      } else if (showNotification && notificationType === 'error') {
        setNotificationType('success')
        setShowNotification(true)
      }
    }
  }, [isOnline, isChecking, showNotification, notificationType])

  useEffect(() => {
    if (showNotification) {
      const timer = setTimeout(() => {
        setShowNotification(false)
      }, 5000)
      return () => clearTimeout(timer)
    }
  }, [showNotification])

  if (!showNotification) return null

  const getNotificationStyles = () => {
    if (notificationType === 'error') {
      return 'bg-red-500 text-white'
    }
    return 'bg-green-500 text-white'
  }

  const getNotificationIcon = () => {
    if (notificationType === 'error') {
      return (
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
        </svg>
      )
    }
    return (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
      </svg>
    )
  }

  const getNotificationMessage = () => {
    if (notificationType === 'error') {
      return 'Backend connection lost. Some features may be unavailable.'
    }
    return 'Backend connection restored!'
  }

  return (
    <div className={`fixed top-4 right-4 z-50 ${getNotificationStyles()} rounded-lg shadow-lg p-4 max-w-sm`}>
      <div className="flex items-start space-x-3">
        <div className="flex-shrink-0">
          {getNotificationIcon()}
        </div>
        <div className="flex-1">
          <p className="text-sm font-medium">
            {getNotificationMessage()}
          </p>
          {error && notificationType === 'error' && (
            <p className="text-xs opacity-90 mt-1">
              Error: {error}
            </p>
          )}
        </div>
        <button
          onClick={() => setShowNotification(false)}
          className="flex-shrink-0 ml-2"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
  )
}

export default BackendNotification
