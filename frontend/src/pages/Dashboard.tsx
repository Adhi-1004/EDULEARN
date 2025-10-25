"use client"

import type React from "react"
import { useState, useEffect } from "react"
import { Link } from "react-router-dom"
import { motion } from "framer-motion"
import type { TestResult } from "../types"
import { useTheme } from "../contexts/ThemeContext"
import { useToast } from "../contexts/ToastContext"
import { useAuth } from "../hooks/useAuth"
import Card from "../components/ui/Card"
import Button from "../components/ui/Button"
import ErrorState from "../components/ErrorState"
import api from "../utils/api"
import { ANIMATION_VARIANTS } from "../utils/constants"


const Dashboard: React.FC = () => {
  const { user } = useAuth()
  console.log("📊 [DASHBOARD] Loading dashboard for user:", user?.email)

  const { } = useTheme()
  const { } = useToast()

  const [recentTests, setRecentTests] = useState<TestResult[]>([])
  const [upcomingTests, setUpcomingTests] = useState<any[]>([])
  const [error] = useState<string | null>(null)

  useEffect(() => {
    if (user?._id || user?.id) {
      console.log("📊 [DASHBOARD] Fetching analytics for user:", user.email)
      fetchRecentTests()
      fetchUpcomingTests()
    }
  }, [user?._id, user?.id])


  const fetchRecentTests = async () => {
    try {
      if (!user) return;
      console.log("🔄 [DASHBOARD] Starting fetchRecentTests...")
      const userId = user._id || user.id
      console.log("👤 [DASHBOARD] User ID:", userId)

      const url = `/api/results/user/${userId}`
      console.log("🌐 [DASHBOARD] Making recent tests API request to:", url)

      const startTime = Date.now()
      const response = await api.get(url)
      const endTime = Date.now()

      console.log("⏱️ [DASHBOARD] Recent tests request completed in:", endTime - startTime, "ms")
      console.log("📥 [DASHBOARD] Response status:", response.status)
      console.log("📥 [DASHBOARD] Response data:", response.data)

      if (response.data.success) {
        const results = response.data.results || []
        console.log("📋 [DASHBOARD] Number of results received:", results.length)
        console.log("📋 [DASHBOARD] Results:", results)

        const recentTests = results.slice(0, 5) // Show last 5 tests
        console.log("📋 [DASHBOARD] Setting recent tests:", recentTests)
        setRecentTests(recentTests)
      } else {
        console.error("❌ [DASHBOARD] Recent tests API returned success: false")
        throw new Error(response.data.error || "Failed to fetch recent tests")
      }

      console.log("✅ [DASHBOARD] fetchRecentTests completed successfully")
    } catch (error: any) {
      console.error("❌ [DASHBOARD] Error in fetchRecentTests:", error)
      console.error("❌ [DASHBOARD] Error details:", {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
        statusText: error.response?.statusText,
        config: error.config,
      })

      // Don't set error for recent tests, just log it
      console.log("⚠️ [DASHBOARD] Recent tests failed, but continuing...")
    }
  }

  const fetchUpcomingTests = async () => {
    try {
      console.log("📊 [DASHBOARD] Fetching upcoming tests for user:", user?.email)
      console.log("👤 [DASHBOARD] User ID:", user?.id)
      console.log("🌐 [DASHBOARD] Making upcoming tests API request to: /api/assessments/student/upcoming")
      
      // Fetch upcoming assessments for the student
      const response = await api.get("/api/assessments/student/upcoming")
      
      console.log("📊 [DASHBOARD] Upcoming tests response:", response.data)
      console.log("📊 [DASHBOARD] Response status:", response.status)
      console.log("📊 [DASHBOARD] Response headers:", response.headers)
      
      const upcomingAssessments = response.data || []
      console.log("📋 [DASHBOARD] Number of upcoming assessments:", upcomingAssessments.length)
      console.log("📋 [DASHBOARD] Upcoming assessments:", upcomingAssessments)
      
      setUpcomingTests(upcomingAssessments)
      console.log("✅ [DASHBOARD] fetchUpcomingTests completed successfully")
    } catch (error: any) {
      console.error("❌ [DASHBOARD] Error in fetchUpcomingTests:", error)
      console.error("❌ [DASHBOARD] Error details:", {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
        statusText: error.response?.statusText,
        config: error.config,
      })
      setUpcomingTests([])
    }
  }



  return (
    <>
      <div className="min-h-screen pt-20 px-4 relative z-10">
        <motion.div
          variants={ANIMATION_VARIANTS.fadeIn}
          initial="initial"
          animate="animate"
          className="max-w-7xl mx-auto"
        >
          <Card className="p-8 mb-8">
            <motion.div variants={ANIMATION_VARIANTS.slideDown} className="text-center mb-8">
              <h1 className="text-3xl md:text-4xl font-bold text-foreground mb-2">
                Welcome back, {user?.username || user?.name || "Learner"}!
              </h1>
              <p className="text-muted-foreground text-base md:text-lg mb-4">
                Ready to continue your learning journey?
              </p>
            </motion.div>

            {/* Action Cards */}
            <motion.div
              variants={ANIMATION_VARIANTS.stagger}
              initial="initial"
              animate="animate"
              className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8"
            >
              <motion.div variants={ANIMATION_VARIANTS.slideUp}>
                <Card className="p-6 h-full">
                  <div className="flex items-center mb-4">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-r from-primary to-accent flex items-center justify-center mr-4">
                      <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                        />
                      </svg>
                    </div>
                    <h3 className="text-xl font-semibold text-foreground">Start New Assessment</h3>
                  </div>
                  <p className="text-muted-foreground mb-6 leading-relaxed">
                    Choose between MCQ assessments or coding challenges. Both powered by AI with personalized difficulty
                    adaptation.
                  </p>
                  <Link to="/assessment-choice">
                    <Button variant="primary" className="w-full">
                      Choose Assessment Type
                    </Button>
                  </Link>
                </Card>
              </motion.div>

              <motion.div variants={ANIMATION_VARIANTS.slideRight}>
                <Card className="p-6 h-full">
                  <div className="flex items-center mb-4">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-r from-primary to-accent flex items-center justify-center mr-4">
                      <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                        />
                      </svg>
                    </div>
                    <h3 className="text-xl font-semibold text-foreground">View Profile</h3>
                  </div>
                  <p className="text-muted-foreground mb-6 leading-relaxed">
                    Manage your account settings and view detailed statistics and progress insights.
                  </p>
                  <Link to="/profile">
                    <Button variant="primary" className="w-full">
                      Go to Profile
                    </Button>
                  </Link>
                </Card>
              </motion.div>
            </motion.div>



            {error && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-center py-8">
                <ErrorState
                  title="Dashboard Error"
                  message={error}
                  onRetry={() => window.location.reload()}
                  retryText="Retry"
                  showCard={false}
                />
              </motion.div>
            )}

            {/* Upcoming Tests */}
            <motion.div
              variants={ANIMATION_VARIANTS.slideUp}
              initial="initial"
              animate="animate"
              transition={{ delay: 0.4 }}
              className="mb-8"
            >
              <Card className="p-6">
                <h3 className="text-lg font-semibold text-foreground mb-6 flex items-center">
                  <span className="mr-2">📅</span>
                  Upcoming Tests
                </h3>
                {upcomingTests.length > 0 ? (
                  <div className="space-y-3">
                    {upcomingTests.map((test, index) => (
                      <motion.div
                        key={test.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className="p-4 rounded-lg bg-blue-500/10 border border-blue-500/30 hover:bg-blue-500/20 hover:border-blue-500/50 transition-all duration-300 cursor-pointer group"
                      >
                        <div className="flex justify-between items-center">
                          <div>
                            <p className="text-foreground font-medium group-hover:text-foreground/80 transition-colors">
                              {test.title}
                            </p>
                            <p className="text-muted-foreground text-sm">
                              {test.subject} • {test.difficulty} • {test.time_limit} minutes
                            </p>
                            <p className="text-blue-400 text-sm mt-1">
                              {test.question_count} questions
                            </p>
                            {test.teacher_name && (
                              <p className="text-blue-300 text-xs mt-1">
                                By: {test.teacher_name}
                              </p>
                            )}
                          </div>
                          <div className="text-right">
                            <Link to={`/test/${test.id}`}>
                              <Button variant="primary" size="sm">
                                Start Test
                              </Button>
                            </Link>
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <div className="text-6xl mb-4">📚</div>
                    <h4 className="text-lg font-semibold text-foreground mb-2">No Upcoming Tests</h4>
                    <p className="text-muted-foreground mb-4">
                      You don't have any tests scheduled at the moment. Check back later or ask your teacher about upcoming assessments.
                    </p>
                    <div className="flex justify-center space-x-3">
                      <Link to="/assessment-choice">
                        <Button variant="outline" size="sm">
                          Practice Assessment
                        </Button>
                      </Link>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => window.location.reload()}
                      >
                        Refresh
                      </Button>
                    </div>
                  </div>
                )}
              </Card>
            </motion.div>

            {/* Recent Test History */}
            {recentTests.length > 0 && (
              <motion.div
                variants={ANIMATION_VARIANTS.slideUp}
                initial="initial"
                animate="animate"
                transition={{ delay: 0.5 }}
                className="mb-8"
              >
                <Card className="p-6">
                  <h3 className="text-lg font-semibold text-foreground mb-6 flex items-center">
                    <span className="mr-2">📊</span>
                    Recent Tests
                  </h3>
                  <div className="space-y-3">
                    {recentTests.map((test, index) => (
                      <Link key={test.id} to={`/test-result/${test.id}`} className="block">
                        <motion.div
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: index * 0.1 }}
                          className="p-4 rounded-lg bg-muted/20 border border-muted/30 hover:bg-muted/30 hover:border-muted/50 transition-all duration-300 cursor-pointer group"
                        >
                          <div className="flex justify-between items-center">
                            <div>
                              <p className="text-foreground font-medium group-hover:text-foreground/80 transition-colors">
                                {test.topic}
                              </p>
                              <p className="text-muted-foreground text-sm">
                                {new Date(test.date).toLocaleDateString()} • {test.difficulty}
                                {test.time_taken && (
                                  <span className="ml-2">
                                    • {Math.floor(test.time_taken / 60)}:
                                    {(test.time_taken % 60).toString().padStart(2, "0")}
                                  </span>
                                )}
                              </p>
                            </div>
                            <div className="text-right">
                              <div
                                className={`text-lg font-bold ${
                                  (test.percentage || (test.score / test.total_questions) * 100) >= 80
                                    ? "text-green-400"
                                    : (test.percentage || (test.score / test.total_questions) * 100) >= 60
                                      ? "text-yellow-400"
                                      : "text-red-400"
                                }`}
                              >
                                {Math.round(test.percentage || (test.score / test.total_questions) * 100)}%
                              </div>
                              <p className="text-muted-foreground text-sm">
                                {test.score}/{test.total_questions}
                              </p>
                            </div>
                          </div>
                        </motion.div>
                      </Link>
                    ))}
                  </div>
                  <div className="text-center mt-4">
                    <Link to="/profile">
                      <Button variant="outline" size="sm">
                        View All Tests
                      </Button>
                    </Link>
                  </div>
                </Card>
              </motion.div>
            )}
          </Card>
        </motion.div>
      </div>
    </>
  )
}

export default Dashboard
