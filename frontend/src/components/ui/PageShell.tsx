import type React from "react"

export default function PageShell({
  title,
  subtitle,
  headerRight,
  children,
}: {
  title?: React.ReactNode
  subtitle?: React.ReactNode
  headerRight?: React.ReactNode
  children: React.ReactNode
}) {
  return (
    <div className="relative min-h-[100dvh] edl-animated-bg">
      <header className="sticky top-0 z-40 bg-background/70 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-b border-border">
        <div className="edl-container flex h-14 items-center justify-between">
          <div className="flex min-w-0 flex-col">
            {title && <h1 className="edl-title">{title}</h1>}
            {subtitle && <p className="edl-subtitle">{subtitle}</p>}
          </div>
          <div className="flex items-center gap-2">{headerRight}</div>
        </div>
      </header>
      <main className="relative z-10">
        <div className="edl-container py-6 sm:py-8">{children}</div>
      </main>
    </div>
  )
}
