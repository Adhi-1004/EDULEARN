"use client"

import type React from "react"
import { motion } from "framer-motion"

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  icon?: React.ReactNode
}

const Input: React.FC<InputProps> = ({ label, error, icon, className = "", ...props }) => {
  return (
    <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} className="space-y-2">
      {label && <label className="block text-sm font-medium text-muted-foreground">{label}</label>}
      <div className="relative">
        {icon && <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground">{icon}</div>}
        <input
          className={`
            w-full px-4 py-3 rounded-lg border border-input bg-background
            text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring
            transition-all duration-300 ${icon ? "pl-10" : ""} ${error ? "border-destructive focus:ring-destructive" : ""} ${className}
          `}
          {...props}
        />
      </div>
      {error && (
        <motion.p initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="text-destructive text-sm">
          {error}
        </motion.p>
      )}
    </motion.div>
  )
}

export default Input
