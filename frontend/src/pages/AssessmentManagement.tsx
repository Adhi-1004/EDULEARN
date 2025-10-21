"use client"

import type React from "react"
import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { useNavigate } from "react-router-dom"
import { useToast } from "../contexts/ToastContext"
import { useAuth } from "../hooks/useAuth"
import Card from "../components/ui/Card"
import Button from "../components/ui/Button"
import Input from "../components/ui/Input"
import AnimatedBackground from "../components/AnimatedBackground"
import Leaderboard from "../components/Leaderboard"
import CodingQuestionForm from "../components/CodingQuestionForm"
import api from "../utils/api"
import { ANIMATION_VARIANTS } from "../utils/constants"
import {
  AssessmentForm,
  BatchSelector,
  QuestionManager,
  AssessmentHistory,
} from "../components/teacher/assessment-management"

interface Batch {
  id: string
  name: string
  studentCount: number
  createdAt: string
  students?: any[]
}

const AssessmentManagement: React.FC = () => {
  const { user } = useAuth()
  const { success, error: showError } = useToast()
  
  const navigate = useNavigate()
  const [batches, setBatches] = useState<Batch[]>([])
  const [loading, setLoading] = useState(true)
  const [assessmentTitle, setAssessmentTitle] = useState("")
  const [assessmentTopic, setAssessmentTopic] = useState("")
  const [assessmentDifficulty, setAssessmentDifficulty] = useState("medium")
  const [questionCount, setQuestionCount] = useState(10)
  const [creatingAssessment, setCreatingAssessment] = useState(false)
  const [currentAssessment, setCurrentAssessment] = useState<any>(null)
  const [showQuestionForm, setShowQuestionForm] = useState(false)
  const [questions, setQuestions] = useState<any[]>([])
  const [currentQuestion, setCurrentQuestion] = useState({
    question: "",
    options: ["", "", "", ""],
    correct_answer: 0,
    explanation: "",
  })
  const [selectedBatches, setSelectedBatches] = useState<string[]>([])
  const [batchSelectionSearchTerm, setBatchSelectionSearchTerm] = useState("")
  const [showLeaderboard, setShowLeaderboard] = useState(false)
  const [selectedAssessmentForLeaderboard] = useState<string | null>("demo-assessment")
  const [showAssessmentResults, setShowAssessmentResults] = useState(false)
  const [assessmentResults] = useState<any[]>([])
  const [teacherAssessments, setTeacherAssessments] = useState<any[]>([])
  const [upcomingAssessments, setUpcomingAssessments] = useState<any[]>([])
  const [recentAssessments, setRecentAssessments] = useState<any[]>([])
  // Removed aiQuestionType since we're only implementing MCQ
  // Removed showAIGeneratedQuestions since AI generation is now handled directly
  // Removed aiGeneratedQuestions since AI generation is now handled directly

  // Early return if user is not available
  if (!user) {
    return (
      <div className="min-h-screen pt-20 px-4 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-blue-200 mb-4">Loading...</h1>
          <p className="text-blue-300">Please wait while we load your dashboard.</p>
        </div>
      </div>
    )
  }

  useEffect(() => {
    fetchDashboardData()
    fetchTeacherAssessments()
    fetchUpcoming()
  }, [])

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      
      console.log("📊 [ASSESSMENT MANAGEMENT] Fetching dashboard data...")
      
      // Fetch batches from API
      const batchesResponse = await api.get("/api/teacher/batches")
      if (batchesResponse.data && Array.isArray(batchesResponse.data)) {
        const formattedBatches = batchesResponse.data.map((batch: any) => ({
          id: batch.batch_id,
          name: batch.batch_name,
          studentCount: batch.total_students,
          createdAt: new Date().toISOString().split("T")[0],
        }))
        
        setBatches(formattedBatches)
        console.log("✅ [ASSESSMENT MANAGEMENT] Batches loaded:", formattedBatches.length)
      } else {
        console.warn("⚠️ [ASSESSMENT MANAGEMENT] No batches data received")
        setBatches([])
      }
      
    } catch (err) {
      console.error("❌ [ASSESSMENT MANAGEMENT] Failed to fetch dashboard data:", err)
      showError("Error", "Failed to load dashboard data")
      setBatches([])
    } finally {
      setLoading(false)
    }
  }

  const fetchTeacherAssessments = async () => {
    try {
      const res = await api.get("/api/assessments/")
      if (Array.isArray(res.data)) {
        setTeacherAssessments(res.data)
        const recent = [...res.data]
          .sort((a: any, b: any) => new Date(b.created_at || b.createdAt || 0).getTime() - new Date(a.created_at || a.createdAt || 0).getTime())
          .slice(0, 4)
        setRecentAssessments(recent)
      }
    } catch (e) {
      console.warn("⚠️ [ASSESSMENT MANAGEMENT] Unable to fetch teacher assessments", e)
    }
  }

  const fetchUpcoming = async () => {
    try {
      const res = await api.get("/api/assessments/teacher/upcoming")
      if (Array.isArray(res.data)) setUpcomingAssessments(res.data)
    } catch (e) {
      console.warn("⚠️ [ASSESSMENT MANAGEMENT] Unable to fetch upcoming assessments", e)
      setUpcomingAssessments([])
    }
  }

  const handleCreateMCQ = () => {
    navigate("/teacher/create-assessment?type=mcq")
  }

  const handleCreateChallenge = () => {
    navigate("/teacher/create-assessment?type=challenge")
  }

  const handleAIGenerate = () => {
    navigate("/teacher/create-assessment?type=ai")
  }


  const handleAddQuestion = async () => {
    if (!currentQuestion.question.trim() || currentQuestion.options.some((opt) => !opt.trim())) {
      showError("Error", "Please fill in the question and all options")
      return
    }

    try {
      // Add question via API
      const response = await api.post(`/api/assessments/${currentAssessment.id}/questions`, {
        question: currentQuestion.question,
        options: currentQuestion.options,
        correct_answer: currentQuestion.correct_answer,
        explanation: currentQuestion.explanation,
        points: 1,
      })

      if (response.data) {
        setQuestions([...questions, { ...currentQuestion, id: questions.length + 1 }])
        setCurrentQuestion({
          question: "",
          options: ["", "", "", ""],
          correct_answer: 0,
          explanation: "",
        })
        success("Success", "Question added successfully!")
      }
    } catch (err: any) {
      console.error("Failed to add question:", err)
      showError("Error", "Failed to add question. Please try again.")
    }
  }

  const handleSubmitAssessment = async () => {
    if (questions.length === 0) {
      showError("Error", "Please add at least one question")
      return
    }
    if (!currentAssessment) {
      showError("Error", "No assessment selected")
      return
    }
    try {
      // Publish the assessment so it is assigned to selected batches and visible to students
      const publishUrl = `/api/assessments/${currentAssessment.id}/publish`
      await api.post(publishUrl)
      success("Published", "Assessment published to selected batches. Students will see it in Upcoming Tests.")
      setShowQuestionForm(false)
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message || "Failed to publish assessment"
      showError("Error", msg)
    }
  }


  // Removed fetchAIGeneratedQuestions since AI generation is now handled directly

  // Removed handlePostTest since AI generation is now handled directly

  // Removed handleAIGenerateQuestions since AI generation is now handled directly in handleCreateAssessment

  if (loading) {
    return (
      <>
        <AnimatedBackground />
        <div className="min-h-screen pt-20 px-4 flex items-center justify-center relative z-10">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-blue-200 mb-4">Loading Assessment Management...</h1>
            <p className="text-blue-300">Please wait while we load your data.</p>
          </div>
        </div>
      </>
    )
  }

  return (
    <>
      <AnimatedBackground />
      <div className="min-h-screen pt-20 px-4 relative z-10">
        <motion.div
          variants={ANIMATION_VARIANTS.fadeIn}
          initial="initial"
          animate="animate"
          className="max-w-7xl mx-auto"
        >
          <Card className="p-8 mb-8">
            <motion.div variants={ANIMATION_VARIANTS.slideDown} className="text-center mb-8">
              <h1 className="text-4xl font-bold text-blue-200 mb-2">Assessment Management</h1>
              <p className="text-blue-300 text-lg mb-4">
                Create, manage, and analyze assessments
              </p>
            </motion.div>

            {/* Assessment History */}
            <AssessmentHistory 
              recentAssessments={recentAssessments}
              upcomingAssessments={upcomingAssessments}
            />


            {/* Assessment Creation Form */}
            <AssessmentForm
              batches={batches}
              onCreateMCQ={handleCreateMCQ}
              onCreateChallenge={handleCreateChallenge}
              onAIGenerate={handleAIGenerate}
              onCreateCoding={() => navigate("/teacher/create-assessment?type=coding")}
            />

            {/* Assessment Creation Forms - Removed, now handled in separate page */}
            {false && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-[100] p-4"
                onClick={handleCloseAssessmentForm}
              >
                <motion.div
                  initial={{ scale: 0.9, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  exit={{ scale: 0.9, opacity: 0 }}
                  className="bg-black/20 backdrop-blur-md border border-blue-500/30 rounded-lg p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto"
                  onClick={(e) => e.stopPropagation()}
                >
                  <div className="flex justify-between items-center mb-6">
                    <h2 className="text-2xl font-bold text-blue-200">
                      {showMCQForm && "Create MCQ Assessment"}
                      {showChallengeForm && "Create Coding Challenge"}
                      {showAIGenerateForm && "AI-Generate Assessment"}
                    </h2>
                    <Button variant="primary" size="sm" onClick={handleCloseAssessmentForm}>
                      Close
                    </Button>
                  </div>
                  
                  <div className="space-y-4">
                    <div>
                      <label className="block text-blue-200 font-medium mb-2">Assessment Title *</label>
                      <Input
                        type="text"
                        value={assessmentTitle}
                        onChange={(e) => setAssessmentTitle(e.target.value)}
                        placeholder="Enter assessment title"
                        className="w-full"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-blue-200 font-medium mb-2">Topic *</label>
                      <Input
                        type="text"
                        value={assessmentTopic}
                        onChange={(e) => setAssessmentTopic(e.target.value)}
                        placeholder="Enter topic (e.g., JavaScript, Data Structures)"
                        className="w-full"
                      />
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-blue-200 font-medium mb-2">Difficulty</label>
                        <select
                          value={assessmentDifficulty}
                          onChange={(e) => setAssessmentDifficulty(e.target.value)}
                          className="w-full px-3 py-2 bg-black/20 backdrop-blur-md border border-blue-500/30 rounded-lg text-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-400"
                        >
                          <option value="easy" className="bg-black text-blue-200">Easy</option>
                          <option value="medium" className="bg-black text-blue-200">Medium</option>
                          <option value="hard" className="bg-black text-blue-200">Hard</option>
                        </select>
                      </div>
                      
                      <div>
                        <label className="block text-blue-200 font-medium mb-2">Number of Questions</label>
                        <Input
                          type="number"
                          value={questionCount}
                          onChange={(e) => setQuestionCount(Number.parseInt(e.target.value) || 10)}
                          min="1"
                          max="50"
                          className="w-full"
                        />
                      </div>
                    </div>

                    {/* Batch Selection Section */}
                    <div className="p-3 bg-green-900/20 rounded-lg border border-green-500/30">
                      <h3 className="text-base font-semibold text-green-200 mb-2">Select Batches</h3>
                      <p className="text-green-300 text-xs mb-3">
                        Choose which batches this assessment will be assigned to
                      </p>
                      
                      {/* Search and Controls */}
                      <div className="flex flex-col sm:flex-row gap-2 mb-3">
                        <div className="flex-1">
                          <Input
                            type="text"
                            value={batchSelectionSearchTerm}
                            onChange={(e) => setBatchSelectionSearchTerm(e.target.value)}
                            placeholder="Search batches..."
                            className="w-full text-sm"
                          />
                        </div>
                        <div className="flex gap-1">
                          <Button
                            variant="primary"
                            size="sm"
                            onClick={() => setSelectedBatches(batches.map((b) => b.id))}
                            className="text-xs px-2 py-1"
                          >
                            Select All
                          </Button>
                          <Button variant="primary" size="sm" onClick={() => setSelectedBatches([])} className="text-xs px-2 py-1">
                            Clear All
                          </Button>
                        </div>
                      </div>

                      {/* Batch List */}
                      <div className="max-h-32 overflow-y-auto space-y-1">
                        {batches
                          .filter((batch) => batch.name.toLowerCase().includes(batchSelectionSearchTerm.toLowerCase()))
                          .map((batch) => (
                            <div
                              key={batch.id}
                              className={`p-2 rounded border transition-colors cursor-pointer ${
                                selectedBatches.includes(batch.id)
                                  ? "bg-green-600 border-green-400 text-white"
                                  : "bg-green-800/30 border-green-500/30 text-green-300 hover:bg-green-800/50"
                              }`}
                              onClick={() => {
                                if (selectedBatches.includes(batch.id)) {
                                  setSelectedBatches(selectedBatches.filter((id) => id !== batch.id))
                                } else {
                                  setSelectedBatches([...selectedBatches, batch.id])
                                }
                              }}
                            >
                              <div className="flex items-center justify-between">
                                <div>
                                  <div className="font-medium text-sm">{batch.name}</div>
                                  <div className="text-xs opacity-75">{batch.studentCount} students</div>
                                </div>
                                <div className="text-xs">{selectedBatches.includes(batch.id) ? "✓" : ""}</div>
                              </div>
                            </div>
                          ))}
                      </div>

                      {/* Selected Batches Summary */}
                      {selectedBatches.length > 0 && (
                        <div className="mt-3 p-2 bg-green-600/20 rounded border border-green-500/30">
                          <div className="text-green-200 font-medium text-sm mb-1">
                            Selected Batches ({selectedBatches.length})
                          </div>
                          <div className="text-green-300 text-xs">
                            Total Students:{" "}
                            {selectedBatches.reduce((total, batchId) => {
                              const batch = batches.find((b) => b.id === batchId)
                              return total + (batch?.studentCount || 0)
                            }, 0)}
                          </div>
                        </div>
                      )}
                    </div>

                    {showAIGenerateForm && (
                      <div className="p-3 bg-blue-900/20 rounded-lg border border-blue-500/30">
                        <h3 className="text-base font-semibold text-blue-200 mb-2">AI Generation Features</h3>
                        <ul className="text-blue-300 text-xs space-y-1">
                          <li>• Automatically generates MCQ questions based on topic</li>
                          <li>• Adapts difficulty level automatically</li>
                          <li>• Creates varied question formats</li>
                          <li>• Includes detailed explanations for each answer</li>
                        </ul>
                      </div>
                    )}

                    {showChallengeForm && (
                      <div className="p-4 bg-green-900/20 rounded-lg border border-green-500/30">
                        <h3 className="text-lg font-semibold text-green-200 mb-2">Coding Challenge Features</h3>
                        <ul className="text-green-300 text-sm space-y-1">
                          <li>• Real-time code execution and testing</li>
                          <li>• Multiple programming languages supported</li>
                          <li>• Automated test case generation</li>
                          <li>• Performance and complexity analysis</li>
                        </ul>
                      </div>
                    )}
                    
                    {showMCQForm && (
                      <div className="p-4 bg-blue-900/20 rounded-lg border border-blue-500/30">
                        <h3 className="text-lg font-semibold text-blue-200 mb-2">MCQ Assessment Features</h3>
                        <ul className="text-blue-300 text-sm space-y-1">
                          <li>• Multiple choice questions with 4 options</li>
                          <li>• Automatic grading and scoring</li>
                          <li>• Detailed explanations for each answer</li>
                          <li>• Progress tracking and analytics</li>
                        </ul>
                      </div>
                    )}
                  </div>

                  <div className="mt-6 flex space-x-3">
                    <Button
                      variant="primary"
                      size="sm"
                      onClick={() => {
                        console.log("🔍 [BUTTON] Create Assessment button clicked")
                        console.log("🔍 [BUTTON] Form states:", {
                          showMCQForm,
                          showChallengeForm,
                          showAIGenerateForm,
                          assessmentTitle,
                          assessmentTopic,
                        })
                        if (showMCQForm) {
                          console.log("🔍 [BUTTON] Calling handleCreateAssessment('mcq')")
                          handleCreateAssessment("mcq")
                        }
                        if (showChallengeForm) {
                          console.log("🔍 [BUTTON] Calling handleCreateAssessment('challenge')")
                          handleCreateAssessment("challenge")
                        }
                        if (showAIGenerateForm) {
                          console.log("🔍 [BUTTON] Calling handleCreateAssessment('ai')")
                          handleCreateAssessment("ai")
                        }
                      }}
                      disabled={creatingAssessment}
                      className="flex-1"
                    >
                      {creatingAssessment ? "Creating..." : "Create Assessment"}
                    </Button>
                    <Button variant="primary" size="sm" onClick={handleCloseAssessmentForm}>
                      Cancel
                    </Button>
                  </div>
                  
                  <div className="mt-4">
                    <Button variant="primary" size="sm" onClick={() => setShowLeaderboard(true)} className="w-full">
                      View Leaderboard
                    </Button>
                  </div>
                </motion.div>
              </motion.div>
            )}

            {/* Removed "Your Assessments" section as requested */}

            {/* Question Addition Form */}
            {showQuestionForm && currentAssessment && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 bg-black/30 backdrop-blur-sm flex items-center justify-center z-50 p-4"
                onClick={() => setShowQuestionForm(false)}
              >
                <motion.div
                  initial={{ scale: 0.9, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  exit={{ scale: 0.9, opacity: 0 }}
                  className="bg-black/20 backdrop-blur-md border border-blue-500/30 rounded-lg p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto"
                  onClick={(e) => e.stopPropagation()}
                >
                  <div className="flex justify-between items-center mb-6">
                    <div>
                      <h2 className="text-2xl font-bold text-blue-200">
                        Add Questions to "{currentAssessment.title}"
                      </h2>
                      <p className="text-blue-300">
                        {questions.length} of {currentAssessment.questionCount} questions added
                      </p>
                    </div>
                    <Button variant="primary" size="sm" onClick={() => setShowQuestionForm(false)}>
                      Close
                    </Button>
                  </div>

                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Question Form - Only show for MCQ and AI assessments */}
                    {currentAssessment.type !== "challenge" && (
                      <div className="space-y-4">
                        <h3 className="text-lg font-semibold text-blue-200">Add New Question</h3>

                        <div>
                          <label className="block text-blue-200 font-medium mb-2">Question *</label>
                          <textarea
                            value={currentQuestion.question}
                            onChange={(e) => setCurrentQuestion({ ...currentQuestion, question: e.target.value })}
                            placeholder="Enter your question here..."
                            className="w-full px-3 py-2 bg-black/20 backdrop-blur-md border border-blue-500/30 rounded-lg text-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-400 h-24 resize-none"
                          />
                        </div>

                        <div>
                          <label className="block text-blue-200 font-medium mb-2">Options *</label>
                          {currentQuestion.options.map((option, index) => (
                            <div key={index} className="flex items-center mb-2">
                              <input
                                type="radio"
                                name="correctAnswer"
                                checked={currentQuestion.correct_answer === index}
                                onChange={() => setCurrentQuestion({ ...currentQuestion, correct_answer: index })}
                                className="mr-3"
                              />
                              <Input
                                type="text"
                                value={option}
                                onChange={(e) => {
                                  const newOptions = [...currentQuestion.options]
                                  newOptions[index] = e.target.value
                                  setCurrentQuestion({ ...currentQuestion, options: newOptions })
                                }}
                                placeholder={`Option ${index + 1}`}
                                className="flex-1"
                              />
                            </div>
                          ))}
                        </div>

                        <div>
                          <label className="block text-blue-200 font-medium mb-2">Explanation</label>
                          <textarea
                            value={currentQuestion.explanation}
                            onChange={(e) => setCurrentQuestion({ ...currentQuestion, explanation: e.target.value })}
                            placeholder="Explain why this is the correct answer..."
                            className="w-full px-3 py-2 bg-black/20 backdrop-blur-md border border-blue-500/30 rounded-lg text-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-400 h-20 resize-none"
                          />
                        </div>

                        <Button variant="primary" onClick={handleAddQuestion} className="w-full">
                          Add Question
                        </Button>
                      </div>
                    )}

                    {/* Questions List - Only show for MCQ and AI assessments */}
                    {currentAssessment.type !== "challenge" && (
                      <div className="space-y-4">
                        <h3 className="text-lg font-semibold text-blue-200">Added Questions ({questions.length})</h3>

                        <div className="max-h-96 overflow-y-auto space-y-3">
                          {questions.map((q, index) => (
                            <div
                              key={q.id}
                              className="p-3 bg-black/20 backdrop-blur-md rounded-lg border border-blue-500/30"
                            >
                              <p className="text-blue-200 font-medium mb-2">
                                Q{index + 1}: {q.question}
                              </p>
                              <div className="space-y-1">
                                {q.options.map((option: string, optIndex: number) => (
                                  <div
                                    key={optIndex}
                                    className={`text-sm ${optIndex === q.correct_answer ? "text-green-300 font-medium" : "text-blue-300"}`}
                                  >
                                    {optIndex === q.correct_answer ? "✓ " : "  "}
                                    {option}
                                  </div>
                                ))}
                              </div>
                            </div>
                          ))}
                        </div>

                        {questions.length > 0 && (
                          <div className="flex space-x-3">
                            <Button variant="primary" onClick={handleSubmitAssessment} className="flex-1">
                              Submit Assessment
                            </Button>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Coding Challenge Section - Only show for coding challenges */}
                    {currentAssessment?.type === "challenge" && (
                      <div className="space-y-4">
                        <h3 className="text-lg font-semibold text-blue-200">Coding Challenge Questions</h3>
                        <p className="text-blue-300">
                          Add coding questions with problem statements, test cases, and constraints.
                        </p>

                        <Button variant="primary" onClick={handleAddCodingQuestion} className="w-full">
                          Add Coding Question
                        </Button>

                        {questions.length > 0 && (
                          <div className="flex space-x-3">
                            <Button variant="primary" onClick={handleSubmitAssessment} className="flex-1">
                              Submit Assessment
                            </Button>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </motion.div>
              </motion.div>
            )}

            {/* AI Generated Questions Review Modal - Removed since AI generation is now handled directly */}

            {/* Assessment Results Modal */}
            {showAssessmentResults && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 bg-black/30 backdrop-blur-sm flex items-center justify-center z-50 p-4"
                onClick={() => setShowAssessmentResults(false)}
              >
                <motion.div
                  initial={{ scale: 0.9, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  exit={{ scale: 0.9, opacity: 0 }}
                  className="bg-black/20 backdrop-blur-md border border-green-500/30 rounded-lg p-6 max-w-4xl w-full max-h-[80vh] overflow-y-auto"
                  onClick={(e) => e.stopPropagation()}
                >
                  <div className="flex justify-between items-center mb-6">
                    <h2 className="text-2xl font-bold text-green-200">Assessment Results</h2>
                    <Button variant="primary" size="sm" onClick={() => setShowAssessmentResults(false)}>
                      Close
                    </Button>
                  </div>

                  <div className="space-y-4">
                    {assessmentResults.length > 0 ? (
                      <div className="space-y-3">
                        {assessmentResults.map((result, index) => (
                          <div key={index} className="p-4 bg-green-900/20 rounded-lg border border-green-500/30">
                            <div className="flex justify-between items-center">
                              <div>
                                <h3 className="text-lg font-semibold text-green-200">{result.student_name}</h3>
                                <p className="text-green-300 text-sm">
                                  Score: {result.score}/{result.total_questions} ({result.percentage}%)
                                </p>
                                <p className="text-green-300 text-sm">
                                  Time Taken: {Math.floor(result.time_taken / 60)}:
                                  {(result.time_taken % 60).toString().padStart(2, "0")}
                                </p>
                              </div>
                              <div
                                className={`text-2xl font-bold ${
                                  result.percentage >= 80
                                    ? "text-green-400"
                                    : result.percentage >= 60
                                      ? "text-yellow-400"
                                      : "text-red-400"
                                }`}
                              >
                                {result.percentage}%
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-8">
                        <p className="text-green-300">No results available yet.</p>
                        <p className="text-green-400 text-sm mt-2">
                          Students need to complete the assessment to see results.
                        </p>
                      </div>
                    )}
                  </div>
                </motion.div>
              </motion.div>
            )}

            {/* Coding Question Form Modal - Removed, now handled in separate page */}
            {false && (<div></div>)}

            {/* Leaderboard Modal */}
            {showLeaderboard && (
              <Leaderboard
                assessmentId={selectedAssessmentForLeaderboard || "demo-assessment"}
                onClose={() => setShowLeaderboard(false)}
              />
            )}

            {/* Batch Selector Modal */}
            <BatchSelector
              batches={batches}
              selectedBatches={selectedBatches}
              onBatchSelectionChange={setSelectedBatches}
              searchTerm={batchSelectionSearchTerm}
              onSearchChange={setBatchSelectionSearchTerm}
              onConfirm={() => {
                // Handle batch selection confirmation
                console.log("Selected batches:", selectedBatches)
              }}
              onCancel={() => {
                setSelectedBatches([])
                setBatchSelectionSearchTerm("")
              }}
              isOpen={false} // This will be controlled by the parent component
            />

            {/* Question Manager Modal */}
            <QuestionManager
              questions={questions}
              onQuestionsChange={setQuestions}
              onSaveAssessment={() => {
                // Handle saving assessment with questions
                console.log("Saving assessment with questions:", questions)
              }}
              onCancel={() => {
                setQuestions([])
                setShowQuestionForm(false)
              }}
              isOpen={showQuestionForm}
              assessmentTitle={assessmentTitle}
              assessmentTopic={assessmentTopic}
              assessmentDifficulty={assessmentDifficulty}
            />

            {/* Smart Assessment Creator - Commented Out */}
            {/* 
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="mb-8"
            >
              <SmartAssessmentCreator teacherId={user?.id || user?._id || ""} />
            </motion.div>
            */}
          </Card>
        </motion.div>
      </div>
    </>
  )
}

export default AssessmentManagement