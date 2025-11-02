"use client"

import React, { useState, useEffect } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { motion } from "framer-motion"
// import { useAuth } from "../hooks/useAuth"  // Not used in this component
// import { useToast } from "../contexts/ToastContext"  // Not used in this component
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
  questions?: QuestionResult[]
  user_answers?: string[]
}

interface QuestionResult {
  question_index?: number
  question: string
  options: string[]
  correct_answer: string | number
  correct_answer_index?: number
  user_answer: string | number
  user_answer_index?: number
  is_correct: boolean
  explanation?: string
}

const TestResultDetail: React.FC = () => {
  const { resultId } = useParams<{ resultId: string }>()
  const navigate = useNavigate()
  // const { user } = useAuth()  // Not used in this component
  // const { error: showError } = useToast()  // Not used in this component
  
  const [result, setResult] = useState<TestResult | null>(null)
  const [questionReviews, setQuestionReviews] = useState<QuestionResult[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (resultId) {
      fetchResult()
    }
  }, [resultId])

  const fetchResult = async () => {
    try {
      setLoading(true)
      
      // Get detailed result directly using the result ID
      const response = await api.get(`/api/results/${resultId}/detailed`)
      
      if (response.data.success) {
        const resultData = response.data.result
        const reviews = response.data.question_reviews || []
        
        console.log("📊 [RESULT DETAIL] Full response:", response.data)
        console.log("📊 [RESULT DETAIL] Question reviews:", reviews)
        if (reviews.length > 0) {
          console.log("📊 [RESULT DETAIL] Sample review:", reviews[0])
          console.log("📊 [RESULT DETAIL] Sample review keys:", Object.keys(reviews[0]))
          console.log("📊 [RESULT DETAIL] Correct answer:", reviews[0].correct_answer)
          console.log("📊 [RESULT DETAIL] Correct answer index:", reviews[0].correct_answer_index)
          console.log("📊 [RESULT DETAIL] User answer:", reviews[0].user_answer)
          console.log("📊 [RESULT DETAIL] User answer index:", reviews[0].user_answer_index)
          console.log("📊 [RESULT DETAIL] Explanation:", reviews[0].explanation)
        }
        
        setResult({
          submission_id: resultData.id,
          assessment_id: resultData.id,
          title: resultData.topic || "Test Result",
          subject: resultData.topic || "",
          difficulty: resultData.difficulty || "medium",
          score: resultData.score,
          percentage: resultData.percentage,
          submitted_at: resultData.date,
          total_questions: resultData.total_questions,
          time_taken: resultData.time_taken || 0,
          questions: resultData.questions || [],
          user_answers: resultData.user_answers || []
        })
        
        setQuestionReviews(reviews)
      } else {
        setError("Result not found")
      }
      
    } catch (err: any) {
      console.error("Error fetching result:", err)
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
                <div className="text-2xl font-bold text-blue-400 mb-2">{result.difficulty}</div>
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

        {/* Question Review */}
        {questionReviews.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="mb-8"
          >
            <Card className="p-6">
              <h3 className="text-xl font-semibold text-white mb-6">Question Review</h3>
              <div className="space-y-8">
                {questionReviews.map((question, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 * index }}
                    className="backdrop-blur-xl border rounded-2xl shadow-2xl overflow-hidden bg-gradient-to-br from-blue-900/20 via-cyan-900/10 to-blue-900/20 border-blue-500/30"
                  >
                    {/* Header */}
                    <div className="p-6 border-b border-blue-500/20">
                      <div className="flex justify-between items-center">
                        <div className="flex items-center space-x-4">
                          <div className="w-12 h-12 rounded-full flex items-center justify-center font-bold text-lg bg-gradient-to-r from-blue-500 to-cyan-500 text-white">
                            {index + 1}
                          </div>
                          <div>
                            <h4 className="text-xl font-semibold text-blue-200">
                              Question {index + 1} of {questionReviews.length}
                            </h4>
                            <div className="flex items-center space-x-2 mt-1">
                              {question.is_correct ? (
                                <div className="flex items-center space-x-1 text-green-400">
                                  <span className="text-lg">✓</span>
                                  <span className="text-sm font-medium">Correct</span>
                                </div>
                              ) : (
                                <div className="flex items-center space-x-1 text-red-400">
                                  <span className="text-lg">✗</span>
                                  <span className="text-sm font-medium">Incorrect</span>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Question Content */}
                    <div className="p-8">
                      <div className="p-6 rounded-xl mb-8 border bg-blue-900/20 border-blue-500/30">
                        <p className="text-xl leading-relaxed text-blue-100 font-sans">
                          {question.question}
                        </p>
                      </div>

                      {/* Options */}
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {question.options.map((option, optIndex) => {
                          // Handle correct answer matching - check both text and index
                          let isCorrectAnswer = false
                          if (question.correct_answer !== undefined && question.correct_answer !== null) {
                            // If correct_answer is text, compare directly
                            if (typeof question.correct_answer === 'string') {
                              isCorrectAnswer = option.trim() === question.correct_answer.trim()
                            }
                            // If correct_answer_index is provided and matches
                            else if (question.correct_answer_index !== undefined && question.correct_answer_index === optIndex) {
                              isCorrectAnswer = true
                            }
                            // If correct_answer is the same as option index
                            else if (typeof question.correct_answer === 'number' && question.correct_answer === optIndex) {
                              isCorrectAnswer = true
                            }
                          }
                          
                          // Handle user answer matching - check both text and index
                          let isUserAnswer = false
                          if (question.user_answer !== undefined && question.user_answer !== null) {
                            // If user_answer is text, compare directly
                            if (typeof question.user_answer === 'string') {
                              isUserAnswer = option.trim() === question.user_answer.trim()
                            }
                            // If user_answer_index is provided and matches
                            else if (question.user_answer_index !== undefined && question.user_answer_index === optIndex) {
                              isUserAnswer = true
                            }
                            // If user_answer is the same as option index
                            else if (typeof question.user_answer === 'number' && question.user_answer === optIndex) {
                              isUserAnswer = true
                            }
                          }
                          
                          const isWrongUserAnswer = isUserAnswer && !question.is_correct
                          
                          return (
                            <div
                              key={optIndex}
                              className={`
                                group relative p-6 rounded-xl text-left transition-all duration-300 overflow-hidden
                                ${isCorrectAnswer 
                                  ? "bg-green-900/30 border-2 border-green-500/50 shadow-lg shadow-green-500/20" 
                                  : isWrongUserAnswer
                                    ? "bg-red-900/30 border-2 border-red-500/50 shadow-lg shadow-red-500/20"
                                    : "bg-gray-800/30 border border-gray-600/30"
                                }
                              `}
                            >
                              <div className="flex items-center space-x-4 relative z-10">
                                <div className={`
                                  w-10 h-10 rounded-full flex items-center justify-center font-bold text-white
                                  ${isCorrectAnswer 
                                    ? "bg-gradient-to-r from-green-500 to-green-600" 
                                    : isWrongUserAnswer
                                      ? "bg-gradient-to-r from-red-500 to-red-600"
                                      : "bg-gradient-to-r from-gray-500 to-gray-600"
                                  }
                                `}>
                                  {String.fromCharCode(65 + optIndex)}
                                </div>
                                <span className={`
                                  flex-1 font-medium font-sans
                                  ${isCorrectAnswer 
                                    ? "text-green-200" 
                                    : isWrongUserAnswer
                                      ? "text-red-200"
                                      : "text-gray-300"
                                  }
                                `}>
                                  {option}
                                </span>
                                {isCorrectAnswer && (
                                  <div className="text-green-400 text-xl font-bold">✓</div>
                                )}
                                {isWrongUserAnswer && (
                                  <div className="text-red-400 text-xl font-bold">✗</div>
                                )}
                              </div>
                            </div>
                          )
                        })}
                      </div>

                      {/* Explanation */}
                      {(question.explanation && question.explanation.trim() !== '' && question.explanation !== 'No explanation available for this question.') ? (
                        <div className="mt-6 p-4 bg-blue-800/20 rounded-xl border border-blue-500/30">
                          <div className="flex items-start space-x-3">
                            <div className="w-6 h-6 rounded-full bg-blue-500/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                              <span className="text-blue-400 text-sm">💡</span>
                            </div>
                            <div>
                              <h5 className="text-blue-200 font-semibold mb-2">Explanation</h5>
                              <p className="text-blue-300 text-sm leading-relaxed">
                                {question.explanation}
                              </p>
                            </div>
                          </div>
                        </div>
                      ) : (
                        <div className="mt-6 p-4 bg-gray-800/20 rounded-xl border border-gray-600/30">
                          <div className="flex items-start space-x-3">
                            <div className="w-6 h-6 rounded-full bg-gray-500/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                              <span className="text-gray-400 text-sm">ℹ️</span>
                            </div>
                            <div>
                              <h5 className="text-gray-300 font-semibold mb-2">Explanation</h5>
                              <p className="text-gray-400 text-sm leading-relaxed italic">
                                No explanation available for this question.
                              </p>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  </motion.div>
                ))}
              </div>
            </Card>
          </motion.div>
        )}

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