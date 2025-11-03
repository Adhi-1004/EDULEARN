"use client"

import type React from "react"
import { motion, HTMLMotionProps } from "framer-motion"

interface ButtonProps extends Omit<HTMLMotionProps<"button">, "onDrag" | "onDragStart" | "onDragEnd"> {
  variant?: "primary" | "secondary" | "outline" | "ghost"
  size?: "sm" | "md" | "lg"
  isLoading?: boolean
  children: React.ReactNode
}

const Button: React.FC<ButtonProps> = ({
  variant = "primary",
  size = "md",
  isLoading = false,
  children,
  className = "",
  disabled,
  ...props
}) => {
  const baseClasses =
    "font-medium rounded-lg transition-all duration-300 focus:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:opacity-50 disabled:cursor-not-allowed"

  const variantClasses = {
    primary: "bg-primary text-white hover:bg-primary/90 active:bg-primary shadow-sm",
    secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/90 active:bg-secondary shadow-sm",
    outline: "border border-border text-foreground hover:bg-muted/30",
    ghost: "text-muted-foreground hover:text-foreground hover:bg-muted/20",
  }

  const sizeClasses = {
    sm: "px-3 py-1.5 text-sm",
    md: "px-6 py-3 text-base",
    lg: "px-8 py-4 text-lg",
  }

  const isDisabled = disabled || isLoading

  return (
    <motion.button
      whileHover={!isDisabled ? { scale: 1.02, y: -1 } : {}}
      whileTap={!isDisabled ? { scale: 0.98 } : {}}
      className={` 
        ${baseClasses}
        ${variantClasses[variant]}
        ${sizeClasses[size]}
        ${className}
      `}
      disabled={isDisabled}
      {...props}
    >
      {isLoading ? (
        <div className="flex items-center justify-center">
          <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent mr-2" />
          Loading...
        </div>
      ) : (
        children
      )}
    </motion.button>
  )
}

export default Button
