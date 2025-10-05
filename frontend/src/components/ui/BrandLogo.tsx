export default function BrandLogo({ className = "" }: { className?: string }) {
    return (
      <div className={`flex items-center gap-2 ${className}`} aria-label="EduLearn">
        <span className="inline-flex h-7 w-7 items-center justify-center rounded-md bg-primary/15 text-primary">
          {/* simple geometric mark */}
          <svg width="16" height="16" viewBox="0 0 24 24" className="drop-shadow-sm">
            <path d="M4 8l8-4 8 4-8 4-8-4z" fill="currentColor" opacity="0.95" />
            <path d="M4 12l8 4 8-4" stroke="currentColor" strokeWidth="1.5" fill="none" opacity="0.6" />
          </svg>
        </span>
        <span className="font-semibold tracking-tight">EduLearn</span>
      </div>
    )
}
  