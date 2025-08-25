import type * as React from "react"
import { cn } from "@/lib/utils"

type FancyButtonProps = {
  children?: React.ReactNode
  className?: string
  onClick?: () => void
  size?: "sm" | "md" | "lg"
  variant?: "default" | "outline" | "ghost" | "secondary"
  type?: "button" | "submit" | "reset"
  "aria-label"?: string
}

export function FancyButton({
  children = "Click",
  className,
  onClick,
  size = "md",
  variant = "default",
  type = "button",
  ...props
}: FancyButtonProps) {
  const sizes = {
    sm: "h-8 px-3 text-sm",
    md: "h-10 px-4 text-sm",
    lg: "h-12 px-6 text-base",
  }[size]

  const isOutline = variant === "outline"
  const isGhost = variant === "ghost"
  const isSecondary = variant === "secondary"

  return (
    <button
      type={type}
      onClick={onClick}
      className={cn(
        "relative inline-flex items-center justify-center rounded-xl font-medium transition-all duration-300",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-fuchsia-400/60",
        sizes,
        !isOutline && !isGhost && !isSecondary && "text-white",
        isSecondary && "bg-white text-fuchsia-700 hover:bg-white/90",
        isGhost && "bg-transparent text-white/80 hover:text-white",
        isOutline && "text-white border border-white/30 hover:border-white bg-transparent",
        // Aurora border for default and outline
        !isGhost && "before:absolute before:inset-0 before:rounded-xl before:p-[1px] before:content-['']",
        !isGhost &&
          "before:[background:linear-gradient(140deg,rgba(217,70,239,.8),rgba(16,185,129,.8),rgba(244,63,94,.8))_padding-box]",
        // Inner glow for default
        !isOutline &&
          !isGhost &&
          !isSecondary &&
          "bg-[radial-gradient(circle_at_30%_30%,rgba(217,70,239,.35),transparent_40%),radial-gradient(circle_at_70%_70%,rgba(16,185,129,.35),transparent_40%)]",
        !isOutline &&
          !isGhost &&
          !isSecondary &&
          "hover:shadow-[0_0_40px_rgba(217,70,239,.25),inset_0_0_20px_rgba(16,185,129,.15)]",
        isOutline && "hover:bg-white/5",
        className,
      )}
      {...props}
    >
      <span className="relative z-10">{children}</span>
    </button>
  )
}
