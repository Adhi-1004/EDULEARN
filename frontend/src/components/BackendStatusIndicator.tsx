"use client"

import type React from "react"
import { useState, useEffect, useCallback } from "react"
import { motion } from "framer-motion"
import { useTheme } from "../contexts/ThemeContext"
import { API_BASE_URL } from "../utils/constants"

interface BackendStatusIndicatorProps {
  className?: string
}

const BackendStatusIndicator: React.FC<BackendStatusIndicatorProps> = ({ className = "" }) => {
  const { mode, colorScheme } = useTheme()
  const [backendStatus, setBackendStatus] = useState<"online" | "offline" | "checking">("checking")

  const checkBackendStatus = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/health`, {
        method: "GET",
        headers: { "Content-Type": "application/json" },
        signal: AbortSignal.timeout(3000),
      })

      setBackendStatus(response.ok ? "online" : "offline")
    } catch (error) {
      setBackendStatus("offline")
    }
  }, [])

  useEffect(() => {
    checkBackendStatus()
    const interval = setInterval(checkBackendStatus, 30000)

    return () => {
      clearInterval(interval)
    }
  }, [checkBackendStatus])

  return (
    <motion.div
      className={`
                group relative flex items-center gap-2 rounded-lg px-2 py-1 border border-base bg-elevated
                ${
                  colorScheme === "dark"
                    ? mode === "professional"
                      ? "bg-gray-800/30 hover:bg-gray-700/50"
                      : "bg-gray-900/20 hover:bg-gray-800/30"
                    : mode === "professional"
                      ? "bg-gray-100/30 hover:bg-gray-200/50"
                      : "bg-gray-100/20 hover:bg-gray-200/30"
                }
                ${className}
            `}
      title={
        backendStatus === "online" ? "Backend Online" : backendStatus === "offline" ? "Backend Offline" : "Checking..."
      }
      aria-label="Backend status"
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      <span
        className={`inline-block w-2.5 h-2.5 rounded-full`}
        style={{
          backgroundColor: backendStatus === "online" ? "#22c55e" : backendStatus === "offline" ? "#ef4444" : "#f59e0b",
        }}
      />
      <span className="hidden sm:inline text-xs text-muted-fg">
        {backendStatus === "online" ? "Online" : backendStatus === "offline" ? "Offline" : "Checking"}
      </span>
    </motion.div>
  )
}

export default BackendStatusIndicator
