"use client"

import React, { useEffect, useMemo, useRef, useState } from "react"
import { motion, AnimatePresence, useScroll, useTransform } from "framer-motion"
import {
  ArrowRight,
  BookOpen,
  Brain,
  CheckCircle,
  Crown,
  GraduationCap,
  Lightbulb,
  Medal,
  Microscope,
  Play,
  Rocket,
  Sparkles,
  Star,
  Target,
  TrendingUp,
  Trophy,
  Users,
  Menu,
  X,
  Mail,
  Lock,
} from "lucide-react"
import { Scene3D } from "../components/3D/Scene3D"
import { useNavigate } from "react-router-dom"
import { useAuth } from "../hooks/useAuth.tsx"

/**
 * Single-file dark futuristic homepage with orange-to-purple gradients:
 * - Dark theme with orange/purple accent colors matching the reference design
 * - Includes a custom FancyButton and lightweight AuthModal in this file
 * - Keeps sections: Nav, Hero, Features, Stats, Testimonials, CTA, Footer
 */

/* FancyButton: orange-to-purple gradient variants for dark theme */
type FancyButtonProps = {
  children?: React.ReactNode
  className?: string
  onClick?: () => void
  size?: "sm" | "md" | "lg"
  variant?: "default" | "outline" | "ghost" | "secondary"
  type?: "button" | "submit" | "reset"
  "aria-label"?: string
}
function FancyButton({
  children = "Click",
  className,
  onClick,
  size = "md",
  variant = "default",
  type = "button",
  ...props
}: FancyButtonProps) {
  const sizes = size === "sm" ? "h-8 px-3 text-sm" : size === "lg" ? "h-12 px-6 text-base" : "h-10 px-4 text-sm"
  const isOutline = variant === "outline"
  const isGhost = variant === "ghost"
  const isSecondary = variant === "secondary"
  return (
    <button
      type={type}
      onClick={onClick}
      className={[
        "relative inline-flex items-center justify-center rounded-xl font-medium transition-all duration-300",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-orange-400/60",
        sizes,
        !isOutline && !isGhost && !isSecondary && "text-white",
        isSecondary && "bg-white text-orange-700 hover:bg-white/90",
        isGhost && "bg-transparent text-white/80 hover:text-white",
        isOutline && "text-white border border-white/30 hover:border-white bg-transparent",
        !isGhost && "before:absolute before:inset-0 before:rounded-xl before:p-[1px] before:content-['']",
        !isGhost &&
          "before:[background:linear-gradient(140deg,rgba(249,115,22,.85),rgba(168,85,247,.85))_padding-box]",
        !isOutline &&
          !isGhost &&
          !isSecondary &&
          "bg-gradient-to-r from-orange-500 to-purple-600",
        !isOutline &&
          !isGhost &&
          !isSecondary &&
          "hover:shadow-[0_0_40px_rgba(249,115,22,.25),inset_0_0_20px_rgba(168,85,247,.15)]",
        isOutline && "hover:bg-white/5",
        className || "",
      ].join(" ")}
      {...props}
    >
      <span className="relative z-10">{children}</span>
    </button>
  )
}

/* Simple in-file AuthModal (no external UI libs) */
function AuthModal({
  open,
  onClose,
  initialMode = "login",
  onLogin,
}: {
  open: boolean
  onClose: () => void
  initialMode?: "login" | "register"
  onLogin: (user: { email: string; role: "student" | "teacher" }) => void
}) {
  const [mode, setMode] = useState<"login" | "register">(initialMode)
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [role, setRole] = useState<"student" | "teacher">("student")

  useEffect(() => setMode(initialMode), [initialMode])

  if (!open) return null
  return (
    <div role="dialog" aria-modal="true" className="fixed inset-0 z-[100] flex items-center justify-center">
      <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" onClick={onClose} aria-hidden="true" />
      {/* Gradient frame */}
      <div className="relative z-10 w-full max-w-md p-[2px] rounded-2xl bg-gradient-to-r from-orange-500/70 to-purple-600/70 shadow-[0_0_40px_rgba(168,85,247,.25)]">
        <div className="rounded-2xl bg-[#14101a]/95 border border-white/10 p-6 text-white">
          {/* Header */}
          <div className="mb-5">
            <div className="inline-flex items-center gap-2 rounded-full bg-white/5 px-3 py-1 ring-1 ring-white/10">
              <Sparkles className="h-4 w-4 text-amber-300" />
              <span className="text-xs text-white/80">EduLearn Access</span>
            </div>
            <h3 className="mt-3 text-2xl font-bold tracking-tight">
              {mode === 'login' ? 'Welcome back' : 'Create your account'}
            </h3>
            <p className="text-sm text-white/70">
              {mode === 'login' ? 'Sign in to your account' : 'Join the next generation of learners.'}
            </p>
          </div>

          {/* Inputs */}
          <div className="space-y-4">
            <div>
              <label className="mb-1 block text-sm text-white/90">Email</label>
              <div className="relative">
                <Mail className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-white/40" />
                <input
                  type="email"
                  className="w-full rounded-lg border border-white/10 bg-white/5 pl-10 pr-3 py-2 text-white placeholder:text-white/40 outline-none focus:ring-2 focus:ring-orange-500/50 focus:border-orange-500/40"
                  placeholder="you@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
            </div>

            <div>
              <label className="mb-1 block text-sm text-white/90">Password</label>
              <div className="relative">
                <Lock className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-white/40" />
                <input
                  type="password"
                  className="w-full rounded-lg border border-white/10 bg-white/5 pl-10 pr-3 py-2 text-white placeholder:text-white/40 outline-none focus:ring-2 focus:ring-purple-600/50 focus:border-purple-600/40"
                  placeholder="********"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
            </div>

            {/* Role segmented control */}
            <div>
              <label className="mb-2 block text-sm text-white/90">Role</label>
              <div className="rounded-xl bg-white/5 p-1 ring-1 ring-white/10 flex">
                <button
                  onClick={() => setRole('student')}
                  className={`flex-1 rounded-lg px-3 py-2 text-sm font-medium transition-all ${
                    role === 'student'
                      ? 'bg-gradient-to-r from-orange-500 to-purple-600 text-white shadow'
                      : 'text-white/80 hover:text-white hover:bg-white/10'
                  }`}
                >
                  Student
                </button>
                <button
                  onClick={() => setRole('teacher')}
                  className={`flex-1 rounded-lg px-3 py-2 text-sm font-medium transition-all ${
                    role === 'teacher'
                      ? 'bg-gradient-to-r from-orange-500 to-purple-600 text-white shadow'
                      : 'text-white/80 hover:text-white hover:bg-white/10'
                  }`}
                >
                  Teacher
                </button>
              </div>
            </div>

            <FancyButton
              className="w-full h-11"
              onClick={() => {
                onLogin({ email, role })
                onClose()
              }}
            >
              {mode === 'login' ? 'Sign In' : 'Create Account'}
            </FancyButton>

            <p className="text-center text-sm text-white/70">
              {mode === 'login' ? (
                <>
                  Don&apos;t have an account?{' '}
                  <button onClick={() => setMode('register')} className="underline underline-offset-4 hover:text-white">
                    Create one
                  </button>
                </>
              ) : (
                <>
                  Already have an account?{' '}
                  <button onClick={() => setMode('login')} className="underline underline-offset-4 hover:text-white">
                    Sign in
                  </button>
                </>
              )}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

/* Page */
export default function HomePage() {
  const navigate = useNavigate()
  const { login } = useAuth()
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false)
  const [authMode, setAuthMode] = useState<"login" | "register">("login")
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const [currentFeature, setCurrentFeature] = useState(0)

  const { scrollY } = useScroll()
  const heroY = useTransform(scrollY, [0, 500], [0, -150])
  const heroOpacity = useTransform(scrollY, [0, 300], [1, 0.3])

  const featuresRef = useRef<HTMLDivElement | null>(null)
  const statsRef = useRef<HTMLDivElement | null>(null)
  const testimonialsRef = useRef<HTMLDivElement | null>(null)

  const openAuthModal = (mode: "login" | "register") => {
    setAuthMode(mode)
    setIsAuthModalOpen(true)
  }

  const scrollToSection = (ref: React.RefObject<HTMLDivElement | null>) => {
    ref.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentFeature((prev) => (prev + 1) % 6)
    }, 4000)
    return () => clearInterval(interval)
  }, [])

  // Motion helpers
  const staggerContainer = useMemo(
    () => ({
      hidden: { opacity: 0 },
      visible: { opacity: 1, transition: { staggerChildren: 0.2 } },
    }),
    [],
  )
  const fadeInUp = useMemo(
    () => ({
    hidden: { opacity: 0, y: 60 },
      visible: { opacity: 1, y: 0, transition: { duration: 0.8, ease: "easeOut" as const } },
    }),
    [],
  )

  // Content
  const featureTiles = useMemo(
    () => [
    {
      icon: Brain,
        title: "AI-Powered Assessment",
        description: "Intelligent grading with detailed feedback and personalized recommendations.",
        color: "from-orange-500 to-purple-600",
        items: ["Instant Feedback", "Smart Grading", "Learning Analytics"],
      },
      {
        icon: Microscope,
        title: "Virtual Laboratory",
        description: "Immersive 3D-like lab experiences and interactive experiments.",
        color: "from-orange-500 to-purple-600",
        items: ["Simulations", "Safe Environment", "Unlimited Resources"],
      },
      {
        icon: Users,
        title: "Study Groups",
        description: "Collaborate with peers via shared boards and group projects.",
        color: "from-orange-500 to-purple-600",
        items: ["Live Sessions", "Shared Workspace", "Projects"],
      },
      {
        icon: Target,
        title: "Personalized Learning",
        description: "Adaptive paths that fit your pace and style.",
        color: "from-orange-500 to-purple-600",
        items: ["Adaptive Paths", "Style-aware", "Pace Control"],
      },
      {
        icon: TrendingUp,
        title: "Advanced Analytics",
        description: "Track progress with predictive insights and reports.",
        color: "from-orange-500 to-purple-600",
        items: ["Tracking", "Predictive", "Reports"],
      },
      {
        icon: Rocket,
        title: "Career Guidance",
        description: "Recommendations and opportunities tailored by AI.",
        color: "from-orange-500 to-purple-600",
        items: ["Career Match", "Internships", "Skill Map"],
      },
    ],
    [],
  )

  const rotating = useMemo(
    () => [
      {
        icon: Brain,
        title: "AI-Powered Learning",
        description: "Personalized learning paths with intelligent tutoring",
        color: "from-orange-500 to-purple-600",
    },
    {
      icon: Microscope,
        title: "Virtual Labs",
        description: "Immersive experiments from anywhere",
        color: "from-orange-500 to-purple-600",
    },
    {
      icon: Users,
        title: "Collaborative Learning",
        description: "Peer-to-peer groups and projects",
        color: "from-orange-500 to-purple-600",
    },
    {
      icon: Trophy,
        title: "Gamified Progress",
        description: "Achievements, badges and leaderboards",
        color: "from-orange-500 to-purple-600",
    },
    {
      icon: TrendingUp,
        title: "Advanced Analytics",
        description: "Insights into learning progress",
        color: "from-orange-500 to-purple-600",
      },
      {
        icon: Target,
        title: "Personalized Paths",
        description: "Adaptive and style-aware",
        color: "from-orange-500 to-purple-600",
      },
    ],
    [],
  )

  return (
    <div className="min-h-screen overflow-hidden bg-[radial-gradient(40rem_40rem_at_10%_10%,rgba(249,115,22,0.16),transparent_60%),radial-gradient(35rem_35rem_at_90%_15%,rgba(168,85,247,0.16),transparent_60%),radial-gradient(32rem_32rem_at_15%_85%,rgba(249,115,22,0.16),transparent_60%),radial-gradient(30rem_30rem_at_85%_85%,rgba(168,85,247,0.16),transparent_60%),linear-gradient(180deg,#0b0a12_0%,#140e19_45%,#1e1524_100%)]">
      {/* Soft aurora ring */}
      <div className="pointer-events-none absolute inset-0 z-0">
        <motion.div
          className="absolute -top-24 left-1/3 h-[28rem] w-[60rem] rounded-full blur-3xl"
          style={{
            background:
              "conic-gradient(from 30deg, rgba(249,115,22,.22), rgba(168,85,247,.22), rgba(249,115,22,.22), rgba(168,85,247,.22), rgba(249,115,22,.22))",
          }}
          animate={{ rotate: [0, 360] }}
          transition={{ duration: 40, repeat: Number.POSITIVE_INFINITY, ease: "linear" }}
        />
      </div>

      {/* Navigation */}
      <motion.nav
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        className="fixed left-0 right-0 top-0 z-50 border-b border-white/10 bg-black/30 backdrop-blur-md"
      >
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <motion.div whileHover={{ scale: 1.05 }} className="flex items-center space-x-2">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-orange-500 to-purple-600">
                <GraduationCap className="h-5 w-5 text-white" />
              </div>
              <span className="bg-gradient-to-r from-orange-300 via-yellow-300 to-purple-300 bg-clip-text text-xl font-bold text-transparent">
                EduLearn AI
              </span>
            </motion.div>

            <div className="hidden items-center space-x-8 md:flex">
              <button
                onClick={() => scrollToSection(featuresRef)}
                className="font-medium text-white/70 transition-colors hover:text-white"
              >
                Features
              </button>
              <button
                onClick={() => scrollToSection(statsRef)}
                className="font-medium text-white/70 transition-colors hover:text-white"
              >
                About
              </button>
              <button
                onClick={() => scrollToSection(testimonialsRef)}
                className="font-medium text-white/70 transition-colors hover:text-white"
              >
                Testimonials
              </button>
            </div>

            <div className="hidden items-center space-x-3 md:flex">
              <FancyButton variant="ghost" onClick={() => openAuthModal("login")} aria-label="Sign In">
                Sign In
              </FancyButton>
              <FancyButton onClick={() => openAuthModal("register")} aria-label="Get Started">
                <span className="flex items-center">
                Get Started
                  <ArrowRight className="ml-2 h-4 w-4" />
                </span>
              </FancyButton>
            </div>

            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="p-2 text-white md:hidden"
              aria-label="Toggle menu"
            >
              {isMobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>

        <AnimatePresence>
          {isMobileMenuOpen && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="border-t border-white/10 bg-black/50 backdrop-blur md:hidden"
            >
              <div className="space-y-4 px-4 py-4">
                <button
                  onClick={() => {
                    scrollToSection(featuresRef)
                    setIsMobileMenuOpen(false)
                  }}
                  className="block w-full text-left font-medium text-white/80 hover:text-white"
                >
                  Features
                </button>
                <button
                  onClick={() => {
                    scrollToSection(statsRef)
                    setIsMobileMenuOpen(false)
                  }}
                  className="block w-full text-left font-medium text-white/80 hover:text-white"
                >
                  About
                </button>
                <button
                  onClick={() => {
                    scrollToSection(testimonialsRef)
                    setIsMobileMenuOpen(false)
                  }}
                  className="block w-full text-left font-medium text-white/80 hover:text-white"
                >
                  Testimonials
                </button>

                <div className="space-y-2 border-t border-white/10 pt-4">
                  <FancyButton variant="ghost" className="w-full" onClick={() => openAuthModal("login")}>
                    Sign In
                  </FancyButton>
                  <FancyButton className="w-full" onClick={() => openAuthModal("register")}>
                    Get Started
                  </FancyButton>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.nav>

      {/* Hero */}
      <section className="relative flex min-h-screen items-center justify-center overflow-hidden">
            <motion.div
          className="absolute -left-20 top-1/4 h-24 w-[60rem] rotate-12 bg-gradient-to-r from-orange-300/20 via-white/10 to-purple-300/20"
          animate={{ opacity: [0.3, 0.6, 0.3], x: [-20, 0, -20] }}
          transition={{ duration: 10, repeat: Number.POSITIVE_INFINITY, ease: "easeInOut" }}
        />
            <motion.div
          className="absolute -right-24 top-2/3 h-24 w-[60rem] -rotate-12 bg-gradient-to-r from-purple-300/20 via-white/10 to-orange-300/20"
          animate={{ opacity: [0.25, 0.55, 0.25], x: [20, 0, 20] }}
          transition={{ duration: 12, repeat: Number.POSITIVE_INFINITY, ease: "easeInOut" }}
        />
        <div
          className="pointer-events-none absolute inset-0"
          aria-hidden="true"
              style={{
            backgroundImage:
              "linear-gradient(rgba(255,255,255,0.06) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.06) 1px, transparent 1px)",
            backgroundSize: "38px 38px",
            backgroundPosition: "0 0, 0 0",
          }}
        />

        <motion.div
          style={{ y: heroY, opacity: heroOpacity }}
          className="relative z-10 mx-auto max-w-7xl px-4 pt-28 sm:px-6 lg:px-8"
        >
          <div className="grid grid-cols-1 items-center gap-12 lg:grid-cols-2">
            <motion.div
              initial={{ opacity: 0, x: -50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8 }}
              className="text-center lg:text-left"
            >
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="mb-6 inline-flex items-center rounded-full bg-gradient-to-r from-orange-200/20 to-purple-200/20 px-4 py-2 text-sm font-medium text-white/90 ring-1 ring-white/10"
              >
                <Sparkles className="mr-2 h-4 w-4" />
                Next-Generation Learning Platform
              </motion.div>

              <motion.h1
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
                className="mb-6 text-4xl font-bold text-white md:text-6xl"
              >
                Transform Your{" "}
                <span className="bg-gradient-to-r from-orange-400 via-yellow-300 to-purple-400 bg-clip-text text-transparent">
                  Educational Journey
                </span>{" "}
                with AI
              </motion.h1>

              <motion.p
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 }}
                className="mb-8 max-w-2xl text-xl leading-relaxed text-white/70"
              >
                Experience the future of education with interactive labs, collaborative groups, and adaptive learning
                paths — everything you need for academic excellence.
              </motion.p>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.8 }}
                className="mb-8 flex flex-col gap-4 sm:flex-row sm:justify-center lg:justify-start"
              >
                <FancyButton onClick={() => openAuthModal("register")} size="lg">
                  <span className="relative z-10 flex items-center">
                    Start Learning Free
                    <ArrowRight className="ml-2 h-5 w-5" />
                  </span>
                </FancyButton>
                <FancyButton variant="outline" size="lg" onClick={() => scrollToSection(featuresRef)}>
                  <Play className="mr-2 h-5 w-5" />
                  Explore Features
                </FancyButton>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1 }}
                className="grid grid-cols-3 gap-8"
              >
                {[
                  { value: "100K+", label: "Students", icon: Users },
                  { value: "5K+", label: "Courses", icon: BookOpen },
                  { value: "99%", label: "Success", icon: Trophy },
                ].map((stat, index) => (
                  <motion.div key={index} whileHover={{ scale: 1.05 }} className="group text-center">
                    <div className="mb-2 flex items-center justify-center">
                      <div className="mr-2 flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-orange-500 to-purple-600 shadow">
                        {React.createElement(stat.icon, { className: "h-4 w-4 text-white" })}
                      </div>
                      <div className="text-2xl font-bold text-white md:text-3xl">{stat.value}</div>
                    </div>
                    <div className="font-medium text-white/70">{stat.label}</div>
                  </motion.div>
                ))}
              </motion.div>
            </motion.div>

            {/* 3D Laptops Hero Scene */}
            <motion.div
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="relative h-96 lg:h-[500px]"
            >
              <Scene3D type="laptops" className="h-full w-full rounded-2xl ring-1 ring-white/10" />
              <motion.div
                key={currentFeature}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="absolute bottom-4 left-4 right-4 rounded-2xl bg-black/40 p-4 shadow-lg ring-1 ring-white/10 backdrop-blur"
              >
                <div className="flex items-center justify-between gap-4">
                  <div className="min-w-0 flex items-center gap-3">
                    <div
                      className={`flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br ${rotating[currentFeature].color} shadow-sm`}
                    >
                      {React.createElement(rotating[currentFeature].icon, { className: "h-5 w-5 text-white" })}
                  </div>
                    <div className="min-w-0">
                      <h3 className="truncate font-semibold text-white">{rotating[currentFeature].title}</h3>
                      <p className="truncate text-sm text-white/70">{rotating[currentFeature].description}</p>
                  </div>
                  </div>
                  <FancyButton size="sm">Explore</FancyButton>
                </div>
              </motion.div>

              <motion.div
                animate={{ y: [0, -20, 0] }}
                transition={{ duration: 6, repeat: Number.POSITIVE_INFINITY, ease: "easeInOut", delay: 1 }}
                className="absolute -right-4 -top-4 flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-br from-orange-400 to-purple-500 shadow-lg"
              >
                <Crown className="h-8 w-8 text-white" />
              </motion.div>
              <motion.div
                animate={{ y: [0, -20, 0] }}
                transition={{ duration: 6, repeat: Number.POSITIVE_INFINITY, ease: "easeInOut", delay: 2 }}
                className="absolute -bottom-4 -left-4 flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-orange-400 to-purple-500 shadow-lg"
              >
                <Medal className="h-6 w-6 text-white" />
              </motion.div>
            </motion.div>
          </div>
        </motion.div>

        {/* Scroll cue */}
        <motion.div
          animate={{ y: [0, 10, 0] }}
          transition={{ duration: 2, repeat: Number.POSITIVE_INFINITY }}
          className="absolute bottom-8 left-1/2 -translate-x-1/2 transform"
        >
          <button
            onClick={() => scrollToSection(featuresRef)}
            className="group flex flex-col items-center text-white/80 transition-colors hover:text-white"
            aria-label="Discover more"
          >
            <span className="mb-2 text-sm font-medium">Discover More</span>
            <div className="flex h-10 w-6 justify-center rounded-full border-2 border-white/30 transition-colors group-hover:border-white">
              <motion.div 
                className="mt-2 h-3 w-1 rounded-full bg-white/30 transition-colors group-hover:bg-white"
                animate={{ y: [0, 8, 0] }}
                transition={{ duration: 1.5, repeat: Number.POSITIVE_INFINITY }}
              />
            </div>
          </button>
        </motion.div>
      </section>

      {/* Features */}
      <section ref={featuresRef} className="relative bg-gradient-to-br from-[#0e0a12] via-[#160f1c] to-[#221628] py-20">
        <div className="absolute inset-0 opacity-40">
          <motion.div
            className="absolute left-10 top-10 h-40 w-40 rounded-full bg-orange-500/20 blur-3xl"
            animate={{ x: [0, 20, -10, 0], y: [0, -10, 15, 0] }}
            transition={{ duration: 18, repeat: Number.POSITIVE_INFINITY, ease: "easeInOut" }}
          />
          <motion.div
            className="absolute right-10 bottom-10 h-48 w-48 rounded-full bg-purple-500/20 blur-3xl"
            animate={{ x: [0, -15, 10, 0], y: [0, 10, -15, 0] }}
            transition={{ duration: 20, repeat: Number.POSITIVE_INFINITY, ease: "easeInOut" }}
          />
        </div>

        <div className="relative z-10 mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={staggerContainer}
            className="mb-16 text-center"
          >
            <motion.div variants={fadeInUp}>
              <span className="mb-4 inline-flex items-center rounded-full bg-orange-300/10 px-4 py-2 text-sm font-medium text-orange-200 ring-1 ring-orange-300/20">
                <Lightbulb className="mr-2 h-4 w-4" />
                Innovative Features
              </span>
            </motion.div>
            <motion.h2 variants={fadeInUp} className="mb-6 text-3xl font-bold text-white md:text-5xl">
              Everything You Need for{" "}
              <span className="bg-gradient-to-r from-orange-300 to-purple-300 bg-clip-text text-transparent">
                Academic Success
              </span>
            </motion.h2>
            <motion.p variants={fadeInUp} className="mx-auto max-w-3xl text-xl text-white/70">
              A unified platform blending AI with proven pedagogy for better outcomes
            </motion.p>
          </motion.div>

          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={staggerContainer}
            className="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-3"
          >
            {featureTiles.map((f, i) => (
              <motion.div key={i} variants={fadeInUp}>
                <div className="relative h-full overflow-hidden rounded-2xl border border-white/10 bg-white/5 p-6 shadow-2xl backdrop-blur transition-all duration-300 hover:shadow-[0_0_0_1px_rgba(255,255,255,0.1)]">
                  <div
                    className="absolute inset-0 opacity-0 transition-opacity duration-300 hover:opacity-100"
                    style={{
                      background: "radial-gradient(60rem 24rem at 0% 0%, rgba(249,115,22,0.08), transparent 50%)",
                    }}
                  />
                  <div className="relative z-10">
                    <div
                      className={`mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br ${f.color} shadow`}
                    >
                      {React.createElement(f.icon, { className: "h-6 w-6 text-white" })}
                    </div>
                    <h3 className="mb-3 text-xl font-semibold text-white">{f.title}</h3>
                    <p className="mb-4 text-white/70">{f.description}</p>
                    <div className="space-y-2">
                      {f.items.map((item: string, idx: number) => (
                        <div key={idx} className="flex items-center text-sm text-white/60">
                          <CheckCircle className="mr-2 h-4 w-4 text-amber-400" />
                          {item}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Stats */}
      <section
        ref={statsRef}
        className="relative bg-gradient-to-br from-[#0e0a12] via-[#160f1c] to-[#221628] py-20"
      >
        <div className="absolute inset-0 opacity-40">
            <motion.div
            className="absolute left-10 top-10 h-40 w-40 rounded-full bg-orange-500/20 blur-3xl"
            animate={{ x: [0, 20, -10, 0], y: [0, -10, 15, 0] }}
            transition={{ duration: 18, repeat: Number.POSITIVE_INFINITY, ease: "easeInOut" }}
          />
          <motion.div
            className="absolute right-10 bottom-10 h-48 w-48 rounded-full bg-purple-500/20 blur-3xl"
            animate={{ x: [0, -15, 10, 0], y: [0, 10, -15, 0] }}
            transition={{ duration: 20, repeat: Number.POSITIVE_INFINITY, ease: "easeInOut" }}
          />
        </div>

        <div className="relative z-10 mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={staggerContainer}
            className="mb-12 text-center"
          >
            <motion.h2 variants={fadeInUp} className="mb-6 text-3xl font-bold md:text-5xl">
              Trusted by Students Worldwide
            </motion.h2>
            <motion.p variants={fadeInUp} className="mx-auto max-w-3xl text-xl text-white/90">
              Join millions of learners who have transformed their education with our platform
            </motion.p>
          </motion.div>

          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={staggerContainer}
            className="grid grid-cols-2 gap-8 md:grid-cols-4"
          >
            {[
              { value: "2M+", label: "Active Students", icon: Users, color: "from-orange-400 to-purple-400" },
              { value: "50K+", label: "Courses Available", icon: BookOpen, color: "from-orange-400 to-purple-400" },
              { value: "99.2%", label: "Success Rate", icon: Trophy, color: "from-orange-400 to-purple-400" },
              { value: "24/7", label: "AI Support", icon: Brain, color: "from-orange-400 to-purple-400" },
            ].map((stat, index) => (
              <motion.div key={index} variants={fadeInUp} className="group text-center">
                <motion.div
                  initial={{ scale: 0 }}
                  whileInView={{ scale: 1 }}
                  transition={{ delay: index * 0.1, type: "spring", stiffness: 100 }}
                  className="relative mb-4"
                >
                  <div
                    className={`mx-auto mb-2 flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-br ${stat.color} transition-transform group-hover:scale-110`}
                  >
                    {React.createElement(stat.icon, { className: "h-8 w-8 text-white" })}
                  </div>
                  <div className="mb-2 text-3xl font-bold md:text-4xl">{stat.value}</div>
                </motion.div>
                <div className="font-medium text-white/90">{stat.label}</div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Testimonials */}
      <section ref={testimonialsRef} className="relative bg-gradient-to-br from-[#0e0a12] via-[#160f1c] to-[#221628] py-20">
        <div className="absolute inset-0 opacity-40">
          <motion.div
            className="absolute left-10 top-10 h-40 w-40 rounded-full bg-orange-500/20 blur-3xl"
            animate={{ x: [0, 20, -10, 0], y: [0, -10, 15, 0] }}
            transition={{ duration: 18, repeat: Number.POSITIVE_INFINITY, ease: "easeInOut" }}
          />
          <motion.div
            className="absolute right-10 bottom-10 h-48 w-48 rounded-full bg-purple-500/20 blur-3xl"
            animate={{ x: [0, -15, 10, 0], y: [0, 10, -15, 0] }}
            transition={{ duration: 20, repeat: Number.POSITIVE_INFINITY, ease: "easeInOut" }}
          />
        </div>
        <div className="relative z-10 mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={staggerContainer}
            className="mb-16 text-center"
          >
            <motion.h2 variants={fadeInUp} className="mb-6 text-3xl font-bold text-white md:text-5xl">
              What Our{" "}
              <span className="bg-gradient-to-r from-orange-300 to-purple-300 bg-clip-text text-transparent">
                Students Say
              </span>
            </motion.h2>
            <motion.p variants={fadeInUp} className="mx-auto max-w-3xl text-xl text-white/70">
              Hear from learners who reached their goals with EduLearn
            </motion.p>
          </motion.div>

          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={staggerContainer}
            className="grid grid-cols-1 gap-8 md:grid-cols-3"
          >
            {[
              {
                name: "Sarah Johnson",
                role: "Computer Science Student",
                avatar: "/student-avatar-sj.png",
                content:
                  "The AI feedback system improved my coding skills dramatically. I went from struggling with data structures to acing my exams!",
                rating: 5,
                achievement: "Top 1% in Algorithms",
              },
              {
                name: "Dr. Michael Chen",
                role: "Professor",
                avatar: "/professor-avatar-mc.png",
                content:
                  "I’ve seen remarkable improvements in engagement and performance. Analytics help me identify struggling students early.",
                rating: 5,
                achievement: "Educator of the Year",
              },
              {
                name: "Emily Rodriguez",
                role: "Data Science Student",
                avatar: "/diverse-student-avatars.png",
                content:
                  "Personalized paths and study groups simplified complex topics. The career guidance helped me land my dream internship!",
                rating: 5,
                achievement: "Top Internship Offer",
              },
            ].map((t, i) => (
              <motion.div key={i} variants={fadeInUp}>
                <div className="relative h-full overflow-hidden rounded-2xl border border-white/10 bg-white/5 p-6 shadow-xl backdrop-blur transition-all duration-300 hover:shadow-[0_0_0_1px_rgba(255,255,255,0.1)]">
                  <div className="absolute right-0 top-0 -mr-10 -mt-10 h-20 w-20 rounded-full bg-gradient-to-br from-orange-500/10 to-purple-500/10 transition-transform group-hover:scale-150" />
                  <div className="relative z-10">
                    <div className="mb-4 flex items-center">
                      {Array.from({ length: t.rating }).map((_, s) => (
                        <Star key={s} className="h-5 w-5 fill-current text-amber-400" />
                      ))}
                    </div>
                    <p className="mb-6 italic leading-relaxed text-white/80">"{t.content}"</p>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <img
                          src={t.avatar || "/placeholder.svg"}
                          alt={t.name}
                          className="mr-4 h-12 w-12 rounded-full border-2 border-rose-300/30"
                        />
                        <div>
                          <div className="font-semibold text-white">{t.name}</div>
                          <div className="text-sm text-white/70">{t.role}</div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="rounded-full bg-rose-300/20 px-2 py-1 text-xs font-medium text-rose-200 ring-1 ring-rose-300/20">
                          {t.achievement}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* CTA */}
      <section className="relative overflow-hidden bg-gradient-to-r from-orange-500 to-purple-600 py-20 text-white">
        <div className="absolute inset-0">
          {Array.from({ length: 30 }).map((_, i) => (
            <motion.div
              key={i}
              className="absolute"
              style={{ left: `${Math.random() * 100}%`, top: `${Math.random() * 100}%` }}
              animate={{ y: [0, -100, 0], opacity: [0, 1, 0] }}
              transition={{
                duration: Math.random() * 3 + 2,
                repeat: Number.POSITIVE_INFINITY,
                delay: Math.random() * 2,
              }}
              aria-hidden="true"
            >
              <Sparkles className="h-4 w-4 text-white/40" />
            </motion.div>
          ))}
        </div>

        <div className="relative z-10 mx-auto max-w-4xl px-4 text-center sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
          >
            <h2 className="mb-6 text-3xl font-bold md:text-5xl">
              Ready to Transform Your{" "}
              <span className="bg-gradient-to-r from-orange-300 to-purple-300 bg-clip-text text-transparent">
                Learning Experience?
              </span>
            </h2>
            <p className="mx-auto mb-8 max-w-2xl text-xl leading-relaxed text-white/90">
              Join millions of students and educators experiencing the future of education.
            </p>
            <div className="mb-8 flex flex-col justify-center gap-4 sm:flex-row">
              <FancyButton variant="secondary" size="lg" onClick={() => openAuthModal("register")}>
                <span className="relative z-10 flex items-center">
                  Start Free Trial
                  <ArrowRight className="ml-2 h-5 w-5" />
                </span>
              </FancyButton>
              <FancyButton variant="outline" size="lg">
                <Play className="mr-2 h-5 w-5" />
                Schedule Demo
              </FancyButton>
            </div>
            
            <div className="flex flex-wrap items-center justify-center gap-8 opacity-90">
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-5 w-5" />
                <span className="text-sm">No Credit Card Required</span>
              </div>
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-5 w-5" />
                <span className="text-sm">14-Day Free Trial</span>
              </div>
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-5 w-5" />
                <span className="text-sm">Cancel Anytime</span>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative overflow-hidden bg-[#0b0a12] py-16 text-white">
        <div className="absolute inset-0 bg-gradient-to-br from-[#0b0a12] via-orange-950/20 to-purple-950/20" />
        <div className="relative z-10 mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 gap-8 md:grid-cols-4">
            <div className="md:col-span-2">
              <div className="mb-4 flex items-center space-x-2">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-orange-500 to-purple-600">
                  <GraduationCap className="h-5 w-5 text-white" />
                </div>
                <span className="text-xl font-bold">EduLearn AI</span>
              </div>
              <p className="mb-6 max-w-md leading-relaxed text-white/70">
                Empowering learners worldwide with AI-driven education technology. 
              </p>
              <div className="flex space-x-4">
                {["facebook", "twitter", "linkedin", "instagram", "youtube"].map((social) => (
                  <motion.a
                    key={social}
                    href="#"
                    whileHover={{ scale: 1.1, y: -2 }}
                    className="flex h-10 w-10 items-center justify-center rounded-full bg-white/5 transition-colors hover:bg-white/10"
                    aria-label={social}
                  >
                    <div className="h-5 w-5 rounded-full bg-current" />
                  </motion.a>
                ))}
              </div>
            </div>

            <div>
              <h3 className="mb-4 text-lg font-semibold">Platform</h3>
              <ul className="space-y-2 text-white/70">
                {["Features", "Pricing", "API Documentation", "Integrations", "Mobile App"].map((item) => (
                  <li key={item}>
                    <a href="#" className="transition-colors hover:text-white hover:underline">
                      {item}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <h3 className="mb-4 text-lg font-semibold">Support</h3>
              <ul className="space-y-2 text-white/70">
                {["Help Center", "Contact Us", "Community Forum", "Privacy Policy", "Terms of Service"].map((item) => (
                  <li key={item}>
                    <a href="#" className="transition-colors hover:text-white hover:underline">
                      {item}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <div className="mt-12 flex flex-col items-center justify-between border-t border-white/10 pt-8 md:flex-row">
            <p className="text-sm text-white/70">© 2025 EduLearn AI. All rights reserved.</p>
            <div className="mt-4 flex space-x-6 text-sm text-white/70 md:mt-0">
              <a href="#" className="transition-colors hover:text-white">
                Privacy
              </a>
              <a href="#" className="transition-colors hover:text-white">
                Terms
              </a>
              <a href="#" className="transition-colors hover:text-white">
                Cookies
              </a>
              <a href="#" className="transition-colors hover:text-white">
                Accessibility
              </a>
            </div>
          </div>
        </div>
      </footer>

      {/* Auth Modal */}
      <AuthModal
        open={isAuthModalOpen}
        onClose={() => setIsAuthModalOpen(false)}
        initialMode={authMode}
        onLogin={(user) => {
          login({
            id: Math.random().toString(36).slice(2),
            name: user.role === 'student' ? 'Student User' : 'Teacher User',
            email: user.email,
            role: user.role,
          })
          navigate(`/${user.role}/dashboard`)
        }}
      />
    </div>
  )
}
