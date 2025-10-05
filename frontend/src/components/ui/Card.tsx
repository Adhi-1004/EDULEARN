"use client"

import type React from "react"
import { motion } from "framer-motion"

interface CardProps {
  children: React.ReactNode
  className?: string
  hover?: boolean
}

const Card: React.FC<CardProps> = ({ children, className = "", hover = true }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={hover ? { y: -2, scale: 1.01 } : {}}
      transition={{ duration: 0.3, ease: "easeOut" }}
      className={`
        relative rounded-2xl border border-border bg-card text-foreground
        ${hover ? "hover:shadow-lg hover:ring-1 hover:ring-border/60" : ""}
        ${className}
      `}
    >
      <div className="relative">{children}</div>
    </motion.div>
  )
}

export default Card
