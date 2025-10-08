"use client"

import Card from "@/components/ui/Card"
import Button from "@/components/ui/Button"

import type React from "react"
import { Link } from "react-router-dom"
import { motion } from "framer-motion"
import { ANIMATION_VARIANTS, SPRING_TRANSITION } from "../utils/constants"

interface Feature {
  title: string
  description: string
  icon: React.ReactNode
  color: string
}

interface Stat {
  number: string
  label: string
  icon: React.ReactNode
}

const features: Feature[] = [
  {
    title: "AI-Powered Assessments",
    description:
      "Generate unique questions with our advanced AI that creates personalized assessments based on topic, difficulty, and learning objectives.",
    icon: (
      <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
        />
      </svg>
    ),
    color: "from-blue-500 to-cyan-500",
  },
  {
    title: "Real-time Code Execution",
    description:
      "Practice coding with our integrated code editor and real-time execution environment supporting multiple programming languages.",
    icon: (
      <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
      </svg>
    ),
    color: "from-green-500 to-emerald-500",
  },
  {
    title: "Smart Analytics",
    description:
      "Get detailed insights into your performance with comprehensive analytics, progress tracking, and personalized recommendations.",
    icon: (
      <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
        />
      </svg>
    ),
    color: "from-blue-500 to-cyan-500",
  },
  {
    title: "Batch Management",
    description:
      "Teachers can create and manage student batches, assign assessments, and track progress across multiple classes.",
    icon: (
      <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-5.523-4.477-10-10-10S-3 12.477-3 18v2m20 0H3m16 0v-2a3 3 0 00-5.356-1.857M7 20H3v-2a3 3 0 015.356-1.857M7 20v-2c0-5.523 4.477-10 10-10s10 4.477 10 10v2"
        />
      </svg>
    ),
    color: "from-orange-500 to-red-500",
  },
  {
    title: "Instant Notifications",
    description:
      "Students receive real-time notifications for new assessments, deadlines, and important updates from teachers.",
    icon: (
      <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M15 17h5l-5 5v-5zM4.828 7l2.586 2.586a2 2 0 002.828 0L12.828 7H4.828zM4.828 7H3a1 1 0 00-1 1v10a1 1 0 001 1h10a1 1 0 001-1V8a1 1 0 00-1-1h-1.828M4.828 7L7.414 4.414A2 2 0 0110.242 4.414L12.828 7"
        />
      </svg>
    ),
    color: "from-indigo-500 to-blue-500",
  },
  {
    title: "Leaderboards & Rankings",
    description:
      "Compete with peers through dynamic leaderboards, track rankings, and celebrate achievements in your learning journey.",
    icon: (
      <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138z"
        />
      </svg>
    ),
    color: "from-yellow-500 to-orange-500",
  },
]

const stats: Stat[] = [
  {
    number: "10K+",
    label: "Active Students",
    icon: (
      <svg className="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 014 0z"
        />
      </svg>
    ),
  },
  {
    number: "500+",
    label: "Teachers",
    icon: (
      <svg className="w-6 h-6 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
        />
      </svg>
    ),
  },
  {
    number: "50K+",
    label: "Questions Generated",
    icon: (
      <svg className="w-6 h-6 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
        />
      </svg>
    ),
  },
  {
    number: "99.9%",
    label: "Uptime",
    icon: (
      <svg className="w-6 h-6 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
      </svg>
    ),
  },
]

const LandingPage: React.FC = () => {
  return (
    <>
      <motion.div
        initial="initial"
        animate="animate"
        exit="exit"
        variants={ANIMATION_VARIANTS.fadeIn}
        className="container mx-auto px-4 py-8 relative z-20"
      >
        {/* Hero Section */}
        <div className="text-center max-w-6xl mx-auto mt-20">
          <motion.h1
            initial={{ y: -50, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={SPRING_TRANSITION}
            className="text-balance text-5xl md:text-7xl font-bold text-foreground mb-6"
          >
            EduLearn
          </motion.h1>

          <motion.p
            variants={ANIMATION_VARIANTS.slideUp}
            initial="initial"
            animate="animate"
            transition={{ delay: 0.2 }}
            className="text-xl md:text-2xl mb-4 text-muted-foreground leading-relaxed font-medium"
          >
            The Future of Education is Here
          </motion.p>

          <motion.p
            variants={ANIMATION_VARIANTS.slideUp}
            initial="initial"
            animate="animate"
            transition={{ delay: 0.3 }}
            className="text-base md:text-lg mb-10 text-muted-foreground leading-relaxed max-w-3xl mx-auto"
          >
            Experience the next generation of learning with our AI-powered assessment platform. Generate unique
            questions, practice coding, track progress, and compete with peers in real-time.
          </motion.p>

          <motion.div
            variants={ANIMATION_VARIANTS.scaleIn}
            initial="initial"
            animate="animate"
            transition={{ delay: 0.4 }}
            className="flex flex-col sm:flex-row gap-6 justify-center items-center"
          >
            <Link to="/signup">
              <Button variant="primary" size="lg" className="text-xl px-12 py-4">
                Start Learning Now
              </Button>
            </Link>
            <Link to="/login">
              <Button variant="outline" size="lg" className="text-xl px-12 py-4 bg-transparent">
                Sign In
              </Button>
            </Link>
          </motion.div>
        </div>

        {/* Features Section */}
        <motion.div
          variants={ANIMATION_VARIANTS.slideUp}
          initial="initial"
          animate="animate"
          transition={{ delay: 0.8 }}
          className="mt-32"
        >
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-foreground mb-4">Powerful Features</h2>
            <p className="text-lg text-muted-foreground max-w-3xl mx-auto">
              Everything you need to create, manage, and excel in your learning journey
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                variants={ANIMATION_VARIANTS.slideUp}
                transition={{ delay: 0.9 + index * 0.1 }}
                whileHover={{ y: -5 }}
              >
                <Card className="p-8 h-full hover:shadow-2xl transition-all duration-300 bg-card">
                  <motion.div
                    className={`h-16 w-16 rounded-full bg-gradient-to-r ${feature.color} flex items-center justify-center mb-6`}
                    whileHover={{ scale: 1.1, rotate: 5 }}
                    transition={SPRING_TRANSITION}
                  >
                    {feature.icon}
                  </motion.div>
                  <h3 className="text-2xl font-bold mb-3 text-foreground">{feature.title}</h3>
                  <p className="text-muted-foreground leading-relaxed text-base">{feature.description}</p>
                </Card>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* How It Works Section */}
        <motion.div
          variants={ANIMATION_VARIANTS.slideUp}
          initial="initial"
          animate="animate"
          transition={{ delay: 1.0 }}
          className="mt-32"
        >
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-foreground mb-4">How It Works</h2>
            <p className="text-lg text-muted-foreground max-w-3xl mx-auto">
              Simple steps to get started with your AI-powered learning journey
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                step: "01",
                title: "Sign Up & Choose Role",
                description: "Create your account as a student, teacher, or admin and get started immediately.",
              },
              {
                step: "02",
                title: "Create or Take Assessments",
                description:
                  "Teachers generate AI-powered questions, students take assessments with real-time feedback.",
              },
              {
                step: "03",
                title: "Track & Compete",
                description:
                  "Monitor progress with detailed analytics, compete on leaderboards, and celebrate achievements.",
              },
            ].map((step, index) => (
              <motion.div
                key={step.step}
                variants={ANIMATION_VARIANTS.slideUp}
                transition={{ delay: 1.1 + index * 0.2 }}
                className="text-center"
              >
                <Card className="p-8 bg-card hover:scale-105 transition-all duration-300 border border-border">
                  <div className="text-6xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-400 mb-4">
                    {step.step}
                  </div>
                  <h3 className="text-2xl font-bold text-white mb-4">{step.title}</h3>
                  <p className="text-gray-300 leading-relaxed">{step.description}</p>
                </Card>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Statistics Dashboard Section */}
        <motion.div
          variants={ANIMATION_VARIANTS.slideUp}
          initial="initial"
          animate="animate"
          transition={{ delay: 1.4 }}
          className="mt-32"
        >
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-foreground mb-4">Platform Statistics</h2>
            <p className="text-lg text-muted-foreground max-w-3xl mx-auto">Trusted by thousands of users worldwide</p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <motion.div
                key={stat.label}
                variants={ANIMATION_VARIANTS.slideUp}
                transition={{ delay: 1.5 + index * 0.1 }}
                className="text-center"
              >
                <Card className="p-8 bg-card hover:scale-105 transition-all duration-300 border border-border">
                  <div className="flex items-center justify-center mb-6">
                    <div className="p-4 rounded-full bg-gradient-to-r from-blue-500/20 to-cyan-500/20">
                      {stat.icon}
                    </div>
                  </div>
                  <div className="text-4xl font-bold text-white mb-3">{stat.number}</div>
                  <div className="text-purple-300 font-medium text-lg">{stat.label}</div>
                </Card>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* CTA Section */}
        <motion.div
          variants={ANIMATION_VARIANTS.slideUp}
          initial="initial"
          animate="animate"
          transition={{ delay: 1.6 }}
          className="mt-32 text-center"
        >
          <Card className="p-16 max-w-4xl mx-auto bg-card border border-border">
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">Ready to Transform Your Learning?</h2>
            <p className="text-xl text-purple-200 mb-12 max-w-3xl mx-auto">
              Join thousands of students and teachers who are already experiencing the future of education. Start your
              journey today and unlock your full potential.
            </p>
            <div className="flex flex-col sm:flex-row gap-6 justify-center items-center">
              <Link to="/signup">
                <Button variant="primary" size="lg" className="text-xl px-12 py-4">
                  Get Started Free
                </Button>
              </Link>
              <Link to="/login">
                <Button variant="outline" size="lg" className="text-xl px-12 py-4 bg-transparent">
                  Sign In
                </Button>
              </Link>
            </div>
            <p className="text-purple-300 mt-8 text-sm">
              No credit card required • Free forever • Start learning in minutes
            </p>
          </Card>
        </motion.div>
      </motion.div>
    </>
  )
}

export default LandingPage
