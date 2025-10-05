"use client"

import React, { useState, useEffect } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { motion } from "framer-motion"
import { useAuth } from "../hooks/useAuth"
import { useToast } from "../contexts/ToastContext"
import Card from "../components/ui/Card"
import Button from "../components/ui/Button"
import LoadingState from "../components/LoadingState"
import ErrorState from "../components/ErrorState"
import api from "../utils/api"

interface TestResult {
  submission_id: string
  assessment_id: string
  title: string
  subject: string
  difficulty: string
  score: number
  percentage: number
  time_taken: number
  submitted_at: string
  total_questions: number
}

const TestResultDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { user } = useAuth()
  const { success, error: showError } = useToast()
  
  const [result, setResult] = useState<TestResult | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (id) {
      fetchResult()
    }
  }, [id])

  const fetchResult = async () => {
    try {
      setLoading(true)
      
      // Get student's assessment history and find the specific result
      const response = await api.get("/api/assessments/student/history")
      const history = response.data || []
      
      // Find the result with matching assessment_id
      const foundResult = history.find((item: any) => item.assessment_id === id)
      
      if (foundResult) {
        setResult(foundResult)
      } else {
        setError("Result not found")
      }
      
    } catch (err: any) {
      console.error("❌ [TEST_RESULT] Error fetching result:", err)
      setError("Failed to load test result. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
  }

  const getScoreColor = (percentage: number) => {
    if (percentage >= 80) return "text-green-400"
    if (percentage >= 60) return "text-yellow-400"
    return "text-red-400"
  }

  const getScoreMessage = (percentage: number) => {
    if (percentage >= 90) return "Excellent work! 🎉"
    if (percentage >= 80) return "Great job! 👏"
    if (percentage >= 70) return "Good effort! 👍"
    if (percentage >= 60) return "Not bad! Keep practicing! 💪"
    return "Don't give up! Practice more! 📚"
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingState size="lg" />
      </div>
    )
  }

  if (error || !result) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Card className="p-8 text-center">
          <ErrorState
            title="Result Not Found"
            message={error || "The test result you're looking for doesn't exist."}
            onBack={() => navigate("/dashboard")}
            backText="Return to Dashboard"
            showCard={true}
          />
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen pt-20 px-4 bg-gray-900">
      <div className="max-w-4xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <h1 className="text-4xl font-bold text-white mb-4">Test Results</h1>
          <p className="text-gray-300 text-lg">{result.title}</p>
        </motion.div>

        {/* Score Card */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
          className="mb-8"
        >
          <Card className="p-8 text-center">
            <div className="mb-6">
              <div className={`text-6xl font-bold mb-4 ${getScoreColor(result.percentage)}`}>
                {result.percentage}%
              </div>
              <h2 className="text-2xl font-semibold text-white mb-2">
                {getScoreMessage(result.percentage)}
              </h2>
              <p className="text-gray-300">
                You scored {result.score} out of {result.total_questions} questions
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-400 mb-2">{result.score}</div>
                <div className="text-gray-300">Correct Answers</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-400 mb-2">{formatTime(result.time_taken)}</div>
                <div className="text-gray-300">Time Taken</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-400 mb-2">{result.difficulty}</div>
                <div className="text-gray-300">Difficulty</div>
              </div>
            </div>

            <div className="text-sm text-gray-400">
              Submitted on {new Date(result.submitted_at).toLocaleDateString()} at {new Date(result.submitted_at).toLocaleTimeString()}
            </div>
          </Card>
        </motion.div>

        {/* Assessment Details */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="mb-8"
        >
          <Card className="p-6">
            <h3 className="text-xl font-semibold text-white mb-4">Assessment Details</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <span className="text-gray-400">Subject:</span>
                <span className="text-white ml-2">{result.subject}</span>
              </div>
              <div>
                <span className="text-gray-400">Difficulty:</span>
                <span className="text-white ml-2 capitalize">{result.difficulty}</span>
              </div>
              <div>
                <span className="text-gray-400">Total Questions:</span>
                <span className="text-white ml-2">{result.total_questions}</span>
              </div>
              <div>
                <span className="text-gray-400">Time Taken:</span>
                <span className="text-white ml-2">{formatTime(result.time_taken)}</span>
              </div>
            </div>
          </Card>
        </motion.div>

        {/* Action Buttons */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="flex flex-col sm:flex-row gap-4 justify-center"
        >
          <Button
            onClick={() => navigate("/dashboard")}
            variant="primary"
            className="px-8 py-3"
          >
            Back to Dashboard
          </Button>
          <Button
            onClick={() => navigate("/assessconfig")}
            variant="secondary"
            className="px-8 py-3"
          >
            Take Another Test
          </Button>
        </motion.div>
      </div>
    </div>
  )
}

export default TestResultDetail