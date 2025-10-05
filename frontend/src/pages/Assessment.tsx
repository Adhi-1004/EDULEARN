"use client"

import React, { useState, useEffect } from "react"
import { useParams, useNavigate, useLocation } from "react-router-dom"
import { motion } from "framer-motion"
import { useAuth } from "../hooks/useAuth"
import { useToast } from "../contexts/ToastContext"
import Card from "../components/ui/Card"
import Button from "../components/ui/Button"
import LoadingState from "../components/LoadingState"
import ErrorState from "../components/ErrorState"
import api from "../utils/api"

interface Question {
  id: string
  question: string
  options: string[]
  correct_answer: number
  explanation?: string
  difficulty: string
  topic: string
}

interface Assessment {
  id: string
  title: string
  subject: string
  difficulty: string
  description: string
  time_limit: number
  question_count: number
  questions: Question[]
  type: string
}

const Assessment: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const location = useLocation()
  const { user } = useAuth()
  const { success, error: showError } = useToast()
  
  const [assessment, setAssessment] = useState<Assessment | null>(null)
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [answers, setAnswers] = useState<number[]>([])
  const [timeLeft, setTimeLeft] = useState(0)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [testStarted, setTestStarted] = useState(false)
  const [testCompleted, setTestCompleted] = useState(false)
  const [assessmentType, setAssessmentType] = useState<'teacher' | 'student'>('teacher')

  useEffect(() => {
    fetchAssessment()
  }, [id])

  useEffect(() => {
    if (testStarted && timeLeft > 0) {
      const timer = setInterval(() => {
        setTimeLeft(prev => {
          if (prev <= 1) {
            handleSubmitTest()
            return 0
          }
          return prev - 1
        })
      }, 1000)
      return () => clearInterval(timer)
    }
  }, [testStarted, timeLeft])

  const fetchAssessment = async () => {
    try {
      setLoading(true)
      
      // Check if configuration was passed from AssessConfig
      const state = location.state as any
      console.log("🔍 [ASSESSMENT] Location state:", state)
      
      if (state?.isStudentGenerated && state?.assessmentConfig) {
        console.log("📋 [ASSESSMENT] Using passed configuration from AssessConfig...")
        console.log("📋 [ASSESSMENT] Config:", state.assessmentConfig)
        
        const { topic, qnCount, difficulty } = state.assessmentConfig
        const totalTime = getDifficultyTime(difficulty, qnCount)
        
        console.log("🤖 [ASSESSMENT] Fetching questions from Gemini AI...")
        console.log("🤖 [ASSESSMENT] Params:", { topic, difficulty, count: qnCount })
        
        // Fetch questions from Gemini AI
        const geminiResponse = await api.get("/db/questions", {
          params: { topic, difficulty, count: qnCount }
        })
        
        console.log("✅ [ASSESSMENT] Gemini response:", geminiResponse.data)
        
        if (!Array.isArray(geminiResponse.data) || geminiResponse.data.length === 0) {
          throw new Error("No questions were generated. Please try again.")
        }
        
        // Create assessment object for student-generated assessment
        const studentAssessment: Assessment = {
          id: 'student-generated',
          title: `${topic} Assessment`,
          subject: topic,
          difficulty: difficulty,
          description: `AI-generated ${difficulty} assessment on ${topic}`,
          time_limit: Math.ceil(totalTime / 60), // Convert to minutes
          question_count: qnCount,
          questions: geminiResponse.data,
          type: 'mcq'
        }
        
        setAssessment(studentAssessment)
        setTimeLeft(totalTime)
        setAnswers(new Array(qnCount).fill(-1))
        setAssessmentType('student')
        console.log("✅ [ASSESSMENT] Loaded student-generated assessment from passed config")
        return
      }
      
      // If no ID is provided and no state, try to get configuration from API
      if (!id) {
        console.log("📋 [ASSESSMENT] No ID provided, loading student-generated assessment...")
        
        // Get assessment configuration
        const configResponse = await api.get("/api/topics/")
        if (!configResponse.data.success) {
          throw new Error(configResponse.data.error || "Failed to get assessment configuration")
        }
        
        const { topic, qnCount, difficulty } = configResponse.data
        const totalTime = getDifficultyTime(difficulty, qnCount)
        
        // Fetch questions from Gemini AI
        const geminiResponse = await api.get("/db/questions", {
          params: { topic, difficulty, count: qnCount }
        })
        
        if (!Array.isArray(geminiResponse.data) || geminiResponse.data.length === 0) {
          throw new Error("No questions were generated. Please try again.")
        }
        
        // Create assessment object for student-generated assessment
        const studentAssessment: Assessment = {
          id: 'student-generated',
          title: `${topic} Assessment`,
          subject: topic,
          difficulty: difficulty,
          description: `AI-generated ${difficulty} assessment on ${topic}`,
          time_limit: Math.ceil(totalTime / 60), // Convert to minutes
          question_count: qnCount,
          questions: geminiResponse.data,
          type: 'mcq'
        }
        
        setAssessment(studentAssessment)
        setTimeLeft(totalTime)
        setAnswers(new Array(qnCount).fill(-1))
        setAssessmentType('student')
        console.log("✅ [ASSESSMENT] Loaded student-generated assessment")
        return
      }
      
      // If ID is provided, try to fetch as teacher-created assessment
      try {
        const response = await api.get(`/api/assessments/${id}/questions`)
        setAssessment(response.data)
        setTimeLeft(response.data.time_limit * 60) // Convert minutes to seconds
        setAnswers(new Array(response.data.question_count).fill(-1))
        setAssessmentType('teacher')
        console.log("✅ [ASSESSMENT] Loaded teacher-created assessment")
      } catch (teacherError) {
        console.log("⚠️ [ASSESSMENT] Not a teacher-created assessment, trying student-generated...")
        
        // If teacher assessment fails, try student-generated assessment
        const configResponse = await api.get("/api/topics/")
        if (!configResponse.data.success) {
          throw new Error(configResponse.data.error || "Failed to get assessment configuration")
        }
        
        const { topic, qnCount, difficulty } = configResponse.data
        const totalTime = getDifficultyTime(difficulty, qnCount)
        
        // Fetch questions from Gemini AI
        const geminiResponse = await api.get("/db/questions", {
          params: { topic, difficulty, count: qnCount }
        })
        
        if (!Array.isArray(geminiResponse.data) || geminiResponse.data.length === 0) {
          throw new Error("No questions were generated. Please try again.")
        }
        
        // Create assessment object for student-generated assessment
        const studentAssessment: Assessment = {
          id: id || 'student-generated',
          title: `${topic} Assessment`,
          subject: topic,
          difficulty: difficulty,
          description: `AI-generated ${difficulty} assessment on ${topic}`,
          time_limit: Math.ceil(totalTime / 60), // Convert to minutes
          question_count: qnCount,
          questions: geminiResponse.data,
          type: 'mcq'
        }
        
        setAssessment(studentAssessment)
        setTimeLeft(totalTime)
        setAnswers(new Array(qnCount).fill(-1))
        setAssessmentType('student')
        console.log("✅ [ASSESSMENT] Loaded student-generated assessment")
      }
      
    } catch (err: any) {
      console.error("❌ [ASSESSMENT] Error fetching assessment:", err)
      showError("Error", "Failed to load assessment. Please try again.")
      navigate("/dashboard")
    } finally {
      setLoading(false)
    }
  }

  const getDifficultyTime = (difficulty: string, questionCount: number) => {
    const timePerQuestion = {
      easy: 60, // 1 minute per question
      medium: 90, // 1.5 minutes per question
      hard: 120, // 2 minutes per question
    }
    return (timePerQuestion[difficulty as keyof typeof timePerQuestion] || 90) * questionCount
  }

  const startTest = () => {
    setTestStarted(true)
  }

  const handleAnswerSelect = (questionIndex: number, answerIndex: number) => {
    const newAnswers = [...answers]
    newAnswers[questionIndex] = answerIndex
    setAnswers(newAnswers)
  }

  const handleSubmitTest = async () => {
    if (submitting) return
    
    try {
      setSubmitting(true)
      
      // Calculate score
      let score = 0
      assessment?.questions.forEach((question, index) => {
        if (answers[index] === question.correct_answer) {
          score++
        }
      })
      
      const percentage = Math.round((score / (assessment?.question_count || 1)) * 100)
      
      if (assessmentType === 'teacher') {
        // Submit to teacher-created assessment endpoint
        const submission = {
          answers: answers,
          time_taken: assessment?.time_limit ? (assessment.time_limit * 60) - timeLeft : 0
        }
        
        await api.post(`/api/assessments/${id}/submit`, submission)
        
        success("Success", `Test completed! Your score: ${score}/${assessment?.question_count} (${percentage}%)`)
        
        setTestCompleted(true)
        
        // Navigate to results after a delay
        setTimeout(() => {
          navigate(`/test-result/${id}`)
        }, 2000)
        
      } else {
        // Submit to student-generated assessment endpoint (existing system)
        const result = {
          user_id: user?.id,
          score: score,
          total_questions: assessment?.question_count || 0,
          questions: assessment?.questions.map((q) => ({
            question: q.question,
            options: q.options,
            answer: q.options[q.correct_answer],
            explanation: q.explanation,
          })) || [],
          user_answers: answers.map(i => i >= 0 ? assessment?.questions[i]?.options[i] || '' : ''),
          topic: assessment?.subject || '',
          difficulty: assessment?.difficulty || '',
          time_taken: assessment?.time_limit ? (assessment.time_limit * 60) - timeLeft : 0,
          explanations: assessment?.questions.map((q, idx) => ({
            questionIndex: idx,
            explanation: q.explanation || "",
          })) || []
        }
        
        await api.post("/api/results", result)
        
        success("Assessment Complete!", `You scored ${score}/${assessment?.question_count}`)

        const resultState = {
          score: score,
          totalQuestions: assessment?.question_count || 0,
          topic: assessment?.subject || '',
          difficulty: assessment?.difficulty || '',
          questions: assessment?.questions || [],
          userAnswers: answers.map(i => i >= 0 ? assessment?.questions[i]?.options[i] || '' : ''),
          timeTaken: assessment?.time_limit ? (assessment.time_limit * 60) - timeLeft : 0,
          explanations: assessment?.questions.map((q, idx) => ({
            questionIndex: idx,
            explanation: q.explanation || "",
          })) || []
        }
        
        navigate("/results", { state: resultState })
      }
      
    } catch (err: any) {
      console.error("❌ [ASSESSMENT] Error submitting test:", err)
      showError("Error", "Failed to submit test. Please try again.")
    } finally {
      setSubmitting(false)
    }
  }

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingState size="lg" />
        </div>
    )
  }

  if (!assessment) {
  return (
      <div className="min-h-screen flex items-center justify-center">
        <Card className="p-8 text-center">
            <ErrorState
            title="Assessment Not Found"
            message="The assessment you're looking for doesn't exist or you don't have access to it."
            onBack={() => navigate("/dashboard")}
            backText="Return to Dashboard"
              showCard={true}
            />
        </Card>
      </div>
    )
  }

  if (testCompleted) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Card className="p-8 text-center">
          <h2 className="text-2xl font-bold text-green-400 mb-4">Test Completed!</h2>
          <p className="text-gray-300 mb-6">Your test has been submitted successfully. Redirecting to results...</p>
          <LoadingState size="md" />
        </Card>
      </div>
    )
  }

  if (!testStarted) {
    return (
      <div className="min-h-screen pt-20 px-4">
        <div className="max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-8"
          >
            <h1 className="text-4xl font-bold text-white mb-4">{assessment.title}</h1>
            <p className="text-gray-300 text-lg">{assessment.description}</p>
            {assessmentType === 'teacher' && (
              <p className="text-blue-300 text-sm mt-2">Created by Teacher</p>
            )}
            {assessmentType === 'student' && (
              <p className="text-purple-300 text-sm mt-2">AI-Generated Assessment</p>
            )}
          </motion.div>

          <Card className="p-8 mb-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-400 mb-2">{assessment.question_count}</div>
                <div className="text-gray-300">Questions</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-green-400 mb-2">{assessment.time_limit}</div>
                <div className="text-gray-300">Minutes</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-purple-400 mb-2">{assessment.difficulty}</div>
                <div className="text-gray-300">Difficulty</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-yellow-400 mb-2">{assessment.subject}</div>
                <div className="text-gray-300">Subject</div>
              </div>
            </div>

            <div className="text-center">
              <Button
                onClick={startTest}
                className="px-8 py-3 text-lg"
                variant="primary"
              >
                Start Test
              </Button>
            </div>
                  </Card>
        </div>
                            </div>
    )
  }

  const currentQuestion = assessment.questions[currentQuestionIndex]
  const progress = ((currentQuestionIndex + 1) / assessment.question_count) * 100

  return (
    <div className="min-h-screen pt-20 px-4 bg-gray-900">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6"
        >
          <div className="flex justify-between items-center mb-4">
            <h1 className="text-2xl font-bold text-white">{assessment.title}</h1>
            <div className="text-right">
              <div className="text-2xl font-bold text-red-400">{formatTime(timeLeft)}</div>
              <div className="text-sm text-gray-400">Time Remaining</div>
                            </div>
                        </div>

          <div className="w-full bg-gray-700 rounded-full h-2 mb-4">
            <div
              className="bg-blue-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
                      </div>
          
          <div className="flex justify-between text-sm text-gray-400">
            <span>Question {currentQuestionIndex + 1} of {assessment.question_count}</span>
            <span>{Math.round(progress)}% Complete</span>
          </div>
        </motion.div>

                      {/* Question */}
                      <motion.div
          key={currentQuestionIndex}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          transition={{ duration: 0.3 }}
        >
          <Card className="p-8 mb-6">
            <h2 className="text-xl font-semibold text-white mb-6">
              {currentQuestion.question}
            </h2>
            
            <div className="space-y-3">
              {currentQuestion.options.map((option, index) => (
                <button
                  key={index}
                  onClick={() => handleAnswerSelect(currentQuestionIndex, index)}
                  className={`w-full p-4 text-left rounded-lg border transition-all duration-200 ${
                    answers[currentQuestionIndex] === index
                      ? 'bg-blue-600 border-blue-400 text-white'
                      : 'bg-gray-800 border-gray-600 text-gray-300 hover:bg-gray-700 hover:border-gray-500'
                  }`}
                >
                  <div className="flex items-center">
                    <div className={`w-6 h-6 rounded-full border-2 mr-3 flex items-center justify-center ${
                      answers[currentQuestionIndex] === index
                        ? 'border-white bg-white text-blue-600'
                        : 'border-gray-400'
                    }`}>
                      {answers[currentQuestionIndex] === index && '✓'}
                    </div>
                    <span>{String.fromCharCode(65 + index)}. {option}</span>
                  </div>
                </button>
              ))}
            </div>
          </Card>
                      </motion.div>

        {/* Navigation */}
        <div className="flex justify-between items-center">
          <Button
            onClick={() => setCurrentQuestionIndex(Math.max(0, currentQuestionIndex - 1))}
            disabled={currentQuestionIndex === 0}
            variant="secondary"
          >
            Previous
          </Button>
          
          <div className="flex space-x-2">
            {assessment.questions.map((_, index) => (
              <button
                            key={index}
                onClick={() => setCurrentQuestionIndex(index)}
                className={`w-8 h-8 rounded-full text-sm font-medium transition-colors ${
                  index === currentQuestionIndex
                    ? 'bg-blue-600 text-white'
                    : answers[index] !== -1
                      ? 'bg-green-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                {index + 1}
              </button>
            ))}
          </div>
          
          {currentQuestionIndex === assessment.questions.length - 1 ? (
                            <Button
              onClick={handleSubmitTest}
              disabled={submitting}
              variant="primary"
            >
              {submitting ? 'Submitting...' : 'Submit Test'}
            </Button>
          ) : (
            <Button
              onClick={() => setCurrentQuestionIndex(Math.min(assessment.questions.length - 1, currentQuestionIndex + 1))}
              variant="primary"
            >
              Next
            </Button>
          )}
                                </div>
                              </div>
                    </div>
  )
}

export default Assessment