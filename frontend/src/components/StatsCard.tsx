"use client"

import type React from "react"
import Card from "./ui/Card"
import LoadingSpinner from "./ui/LoadingSpinner"

interface StatsCardProps {
  title: string
  value: number | string
  icon: React.ReactNode
  /** Tailwind gradient classes e.g. "from-emerald-500 to-green-400" */
  color: string
  /** Optional background/border classes e.g. "bg-emerald-500/10 border-emerald-500/30 hover:bg-emerald-500/15 hover:border-emerald-500/50" */
  bgClass?: string
  loading?: boolean
  className?: string
}

const StatsCard: React.FC<StatsCardProps> = ({ title, value, icon, color, bgClass = "", loading = false, className = "" }) => {
  return (
    <Card className={`p-6 text-center ${bgClass} ${className}`} hover={true}>
      <div
        className={`w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4 text-white bg-gradient-to-r ${color}`}
      >
        {icon}
      </div>
      <h3 className="text-2xl font-bold text-fg mb-2">{loading ? <LoadingSpinner size="sm" /> : value}</h3>
      <p className="text-muted-fg text-sm">{title}</p>
    </Card>
  )
}

export default StatsCard
