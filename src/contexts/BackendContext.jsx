"use client"

import { createContext, useContext, useState, useEffect } from "react"

const BackendContext = createContext()

export const useBackend = () => {
  const context = useContext(BackendContext)
  if (!context) {
    throw new Error('useBackend must be used within a BackendProvider')
  }
  return context
}

export const BackendProvider = ({ children }) => {
  const [isOnline, setIsOnline] = useState(false)
  const [isChecking, setIsChecking] = useState(true)
  const [lastChecked, setLastChecked] = useState(null)
  const [error, setError] = useState(null)

  const checkBackendStatus = async () => {
    setIsChecking(true)
    setError(null)
    
    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 5000)
      
      const response = await fetch('http://localhost:5003/getQuestions', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: controller.signal
      })
      
      clearTimeout(timeoutId)
      
      if (response.ok) {
        setIsOnline(true)
        setLastChecked(new Date())
      } else {
        setIsOnline(false)
        setError(`HTTP ${response.status}: ${response.statusText}`)
      }
    } catch (error) {
      console.log('Backend connection failed:', error.message)
      setIsOnline(false)
      setLastChecked(new Date())
      
      if (error.name === 'AbortError') {
        setError('Connection timeout')
      } else {
        setError(error.message)
      }
    } finally {
      setIsChecking(false)
    }
  }

  const makeApiCall = async (endpoint, options = {}) => {
    if (!isOnline) {
      throw new Error('Backend is offline')
    }

    try {
      const response = await fetch(`http://localhost:5003${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        },
        ...options
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      return await response.json()
    } catch (error) {
      console.error('API call failed:', error)
      throw error
    }
  }

  useEffect(() => {
    // Initial check
    checkBackendStatus()

    // Set up periodic checks every 30 seconds
    const interval = setInterval(checkBackendStatus, 30000)

    return () => clearInterval(interval)
  }, [])

  const value = {
    isOnline,
    isChecking,
    lastChecked,
    error,
    checkBackendStatus,
    makeApiCall
  }

  return (
    <BackendContext.Provider value={value}>
      {children}
    </BackendContext.Provider>
  )
}
