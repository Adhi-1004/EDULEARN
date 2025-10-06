"use client"

import type React from "react"
import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { useToast } from "../contexts/ToastContext"
import { useAuth } from "../hooks/useAuth"
import Card from "../components/ui/Card"
import Button from "../components/ui/Button"
import Input from "../components/ui/Input"
import AnimatedBackground from "../components/AnimatedBackground"
import Leaderboard from "../components/Leaderboard"
import CodingQuestionForm from "../components/CodingQuestionForm"
// import SmartAssessmentCreator from "../components/teacher/SmartAssessmentCreator"
import api from "../utils/api"
import { ANIMATION_VARIANTS } from "../utils/constants"

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
  
  const [batches, setBatches] = useState<Batch[]>([])
  const [loading, setLoading] = useState(true)
  const [showMCQForm, setShowMCQForm] = useState(false)
  const [showChallengeForm, setShowChallengeForm] = useState(false)
  const [showAIGenerateForm, setShowAIGenerateForm] = useState(false)
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
  const [showCodingQuestionForm, setShowCodingQuestionForm] = useState(false)
  const [aiQuestionType, setAiQuestionType] = useState<"mcq" | "coding" | "both">("mcq")
  const [showAIGeneratedQuestions, setShowAIGeneratedQuestions] = useState(false)
  const [aiGeneratedQuestions, setAiGeneratedQuestions] = useState<any[]>([])

  // Early return if user is not available
  if (!user) {
    return (
      <div className="min-h-screen pt-20 px-4 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-purple-200 mb-4">Loading...</h1>
          <p className="text-purple-300">Please wait while we load your dashboard.</p>
        </div>
      </div>
    )
  }

  useEffect(() => {
    fetchDashboardData()
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

  const handleCreateMCQ = () => {
    setShowMCQForm(true)
    setShowChallengeForm(false)
    setShowAIGenerateForm(false)
  }

  const handleCreateChallenge = () => {
    setShowChallengeForm(true)
    setShowMCQForm(false)
    setShowAIGenerateForm(false)
  }

  const handleAIGenerate = () => {
    setShowAIGenerateForm(true)
    setShowMCQForm(false)
    setShowChallengeForm(false)
  }

  const handleCreateAssessment = async (type: "mcq" | "challenge" | "ai") => {
    console.log("🔍 [ASSESSMENT] Form validation check:", {
      title: assessmentTitle,
      topic: assessmentTopic,
      titleTrimmed: assessmentTitle.trim(),
      topicTrimmed: assessmentTopic.trim(),
    })
    
    if (!assessmentTitle.trim() || !assessmentTopic.trim()) {
      console.log("❌ [ASSESSMENT] Validation failed - missing required fields")
      showError("Error", "Please fill in all required fields")
      return
    }

    if (selectedBatches.length === 0) {
      console.log("❌ [ASSESSMENT] Validation failed - no batches selected")
      showError("Error", "Please select at least one batch for this assessment")
      return
    }

    try {
      setCreatingAssessment(true)

      console.log("🔍 [ASSESSMENT] Creating assessment with data:", {
        title: assessmentTitle,
        topic: assessmentTopic,
        difficulty: assessmentDifficulty,
        type: type,
      })

      // Create assessment via API
      const response = await api.post("/api/assessments/", {
        title: assessmentTitle,
        subject: assessmentTopic, // Backend expects 'subject' field
        difficulty: assessmentDifficulty,
        description: `AI-generated ${type} assessment on ${assessmentTopic}`,
        time_limit: type === "challenge" ? 60 : 30, // 60 minutes for coding, 30 for MCQ
        max_attempts: 1,
        type: type, // Send the assessment type to backend
        batches: selectedBatches, // Include selected batches
        questions: [], // Empty questions array for now
      })

      if (response.data) {
        // Set up for question addition
        setCurrentAssessment({
          id: response.data.id,
          title: assessmentTitle,
          topic: assessmentTopic,
          difficulty: assessmentDifficulty,
          type: type,
          questionCount: questionCount,
        })

        success(
          "Success",
          `${type.toUpperCase()} assessment "${assessmentTitle}" created successfully! Now add questions.`,
        )

        // Reset form
        setAssessmentTitle("")
        setAssessmentTopic("")
        setAssessmentDifficulty("medium")
        setQuestionCount(10)
        setSelectedBatches([])
        setBatchSelectionSearchTerm("")
        setShowMCQForm(false)
        setShowChallengeForm(false)
        setShowAIGenerateForm(false)

        // Handle different assessment types
        if (type === "challenge") {
          // For coding challenges, go directly to coding question form
          setShowCodingQuestionForm(true)
        } else if (type === "ai") {
          // For AI-generated assessments, generate questions automatically
          await handleAIGenerateQuestions(response.data.id, aiQuestionType)
        } else {
          // For MCQ assessments, show regular question form
          setShowQuestionForm(true)
        }
      }
    } catch (err: any) {
      console.error("❌ [ASSESSMENT] Failed to create assessment:", err)
      const errorMessage = err.response?.data?.detail || err.message || "Failed to create assessment. Please try again."
      showError("Error", errorMessage)
    } finally {
      setCreatingAssessment(false)
    }
  }

  const handleCloseAssessmentForm = () => {
    setShowMCQForm(false)
    setShowChallengeForm(false)
    setShowAIGenerateForm(false)
    setAssessmentTitle("")
    setAssessmentTopic("")
    setAssessmentDifficulty("medium")
    setQuestionCount(10)
    setSelectedBatches([])
    setBatchSelectionSearchTerm("")
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

  const handleSubmitAssessment = () => {
    if (questions.length === 0) {
      showError("Error", "Please add at least one question")
      return
    }
    // Redirect to batch assignment or next step
    setShowQuestionForm(false)
  }

  const handleAddCodingQuestion = () => {
    if (!currentAssessment) {
      showError("Error", "No assessment selected")
      return
    }
    setShowCodingQuestionForm(true)
  }

  const handleCodingQuestionAdded = () => {
    setShowCodingQuestionForm(false)
    // Show success message and allow adding more questions or submitting
    success("Success", "Coding question added successfully! You can add more questions or submit the assessment.")
  }

  const fetchAIGeneratedQuestions = async (assessmentId: string) => {
    try {
      const response = await api.get(`/api/assessments/${assessmentId}/details`)
      if (response.data && response.data.questions) {
        setAiGeneratedQuestions(response.data.questions)
      }
    } catch (err: any) {
      console.error("Failed to fetch AI generated questions:", err)
      showError("Error", "Failed to fetch AI generated questions.")
    }
  }

  const handlePostTest = () => {
    if (!currentAssessment) {
      showError("Error", "No assessment selected")
      return
    }
    // This should likely lead to assigning the assessment to batches
    setShowAIGeneratedQuestions(false) // Close the review modal
    setShowQuestionForm(false)
  }

  const handleAIGenerateQuestions = async (assessmentId: string, questionType: "mcq" | "coding" | "both") => {
    try {
      setCreatingAssessment(true)

      console.log("🤖 [AI GENERATION] Generating questions for assessment:", assessmentId)
      console.log("🤖 [AI GENERATION] Question type:", questionType)
      console.log("🤖 [AI GENERATION] Topic:", assessmentTopic)
      console.log("🤖 [AI GENERATION] Difficulty:", assessmentDifficulty)
      console.log("🤖 [AI GENERATION] Question count:", questionCount)

      // Call AI generation endpoint
      const response = await api.post(`/api/assessments/${assessmentId}/ai-generate-questions`, {
        question_type: questionType,
        topic: assessmentTopic,
        difficulty: assessmentDifficulty,
        question_count: questionCount,
        title: assessmentTitle, // Passing title for context if needed by AI
      })

      if (response.data) {
        success("Success", `AI generated ${response.data.generated_count} questions successfully!`)

        // Fetch the generated questions to show for review
        await fetchAIGeneratedQuestions(assessmentId)

        // Show the generated questions for review
        setShowAIGeneratedQuestions(true)
        setCurrentAssessment({
          id: assessmentId,
          title: assessmentTitle,
          topic: assessmentTopic,
          difficulty: assessmentDifficulty,
          type: "ai", // This type might need refinement based on actual generation
          questionCount: response.data.generated_count,
        })
      }
    } catch (err: any) {
      console.error("❌ [AI GENERATION] Failed to generate questions:", err)
      console.error("❌ [AI GENERATION] Error response:", err.response?.data)
      showError("Error", "Failed to generate questions. Please try again.")
    } finally {
      setCreatingAssessment(false)
    }
  }

  if (loading) {
    return (
      <>
        <AnimatedBackground />
        <div className="min-h-screen pt-20 px-4 flex items-center justify-center relative z-10">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-purple-200 mb-4">Loading Assessment Management...</h1>
            <p className="text-purple-300">Please wait while we load your data.</p>
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
              <h1 className="text-4xl font-bold text-purple-200 mb-2">Assessment Management</h1>
              <p className="text-purple-300 text-lg mb-4">
                Create, manage, and analyze assessments
              </p>
            </motion.div>


            {/* Assessment Creation Tools */}
            <motion.div variants={ANIMATION_VARIANTS.slideUp} className="mb-8">
              <Card className="p-6">
                <h2 className="text-2xl font-bold text-purple-200 mb-6">Assessment Creation Tools</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  <div className="p-4 bg-purple-900/20 rounded-lg border border-purple-500/30">
                    <h3 className="text-lg font-semibold text-purple-200 mb-2">MCQ Assessments</h3>
                    <p className="text-purple-300 text-sm mb-4">Create multiple choice question assessments</p>
                    <Button variant="primary" size="sm" className="w-full" onClick={handleCreateMCQ}>
                      Create MCQ
                    </Button>
                  </div>
                  <div className="p-4 bg-purple-900/20 rounded-lg border border-purple-500/30">
                    <h3 className="text-lg font-semibold text-purple-200 mb-2">Coding Challenges</h3>
                    <p className="text-purple-300 text-sm mb-4">Create programming challenges and exercises</p>
                    <Button variant="primary" size="sm" className="w-full" onClick={handleCreateChallenge}>
                      Create Challenge
                    </Button>
                  </div>
                  <div className="p-4 bg-purple-900/20 rounded-lg border border-purple-500/30">
                    <h3 className="text-lg font-semibold text-purple-200 mb-2">AI-Generated</h3>
                    <p className="text-purple-300 text-sm mb-4">Use AI to generate custom assessments</p>
                    <Button variant="primary" size="sm" className="w-full" onClick={handleAIGenerate}>
                      AI Generate
                    </Button>
                  </div>
                  <div className="p-4 bg-green-900/20 rounded-lg border border-green-500/30">
                    <h3 className="text-lg font-semibold text-green-200 mb-2">Assessment Results</h3>
                    <p className="text-green-300 text-sm mb-4">View and analyze student performance</p>
                    <Button
                      variant="primary"
                      size="sm"
                      className="w-full"
                      onClick={() => setShowAssessmentResults(true)}
                    >
                      View Results
                    </Button>
                  </div>
                </div>
              </Card>
            </motion.div>

            {/* Assessment Creation Forms */}
            {(showMCQForm || showChallengeForm || showAIGenerateForm) && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 bg-black/30 backdrop-blur-sm flex items-center justify-center z-50 p-4"
                onClick={handleCloseAssessmentForm}
              >
                <motion.div
                  initial={{ scale: 0.9, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  exit={{ scale: 0.9, opacity: 0 }}
                  className="bg-black/20 backdrop-blur-md border border-purple-500/30 rounded-lg p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto"
                  onClick={(e) => e.stopPropagation()}
                >
                  <div className="flex justify-between items-center mb-6">
                    <h2 className="text-2xl font-bold text-purple-200">
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
                      <label className="block text-purple-200 font-medium mb-2">Assessment Title *</label>
                      <Input
                        type="text"
                        value={assessmentTitle}
                        onChange={(e) => setAssessmentTitle(e.target.value)}
                        placeholder="Enter assessment title"
                        className="w-full"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-purple-200 font-medium mb-2">Topic *</label>
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
                        <label className="block text-purple-200 font-medium mb-2">Difficulty</label>
                        <select
                          value={assessmentDifficulty}
                          onChange={(e) => setAssessmentDifficulty(e.target.value)}
                          className="w-full px-3 py-2 bg-black/20 backdrop-blur-md border border-purple-500/30 rounded-lg text-purple-200 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-400"
                        >
                          <option value="easy" className="bg-black text-purple-200">Easy</option>
                          <option value="medium" className="bg-black text-purple-200">Medium</option>
                          <option value="hard" className="bg-black text-purple-200">Hard</option>
                        </select>
                      </div>
                      
                      <div>
                        <label className="block text-purple-200 font-medium mb-2">Number of Questions</label>
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
                    <div className="p-4 bg-green-900/20 rounded-lg border border-green-500/30">
                      <h3 className="text-lg font-semibold text-green-200 mb-3">Select Batches</h3>
                      <p className="text-green-300 text-sm mb-4">
                        Choose which batches this assessment will be assigned to
                      </p>
                      
                      {/* Search and Controls */}
                      <div className="flex flex-col sm:flex-row gap-3 mb-4">
                        <div className="flex-1">
                          <Input
                            type="text"
                            value={batchSelectionSearchTerm}
                            onChange={(e) => setBatchSelectionSearchTerm(e.target.value)}
                            placeholder="Search batches..."
                            className="w-full"
                          />
                        </div>
                        <div className="flex gap-2">
                          <Button
                            variant="primary"
                            size="sm"
                            onClick={() => setSelectedBatches(batches.map((b) => b.id))}
                          >
                            Select All
                          </Button>
                          <Button variant="primary" size="sm" onClick={() => setSelectedBatches([])}>
                            Clear All
                          </Button>
                        </div>
                      </div>

                      {/* Batch List */}
                      <div className="max-h-48 overflow-y-auto space-y-2">
                        {batches
                          .filter((batch) => batch.name.toLowerCase().includes(batchSelectionSearchTerm.toLowerCase()))
                          .map((batch) => (
                            <div
                              key={batch.id}
                              className={`p-3 rounded-lg border transition-colors cursor-pointer ${
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
                                  <div className="font-medium">{batch.name}</div>
                                  <div className="text-sm opacity-75">{batch.students?.length || 0} students</div>
                                </div>
                                <div className="text-sm">{selectedBatches.includes(batch.id) ? "✓" : ""}</div>
                              </div>
                            </div>
                          ))}
                      </div>

                      {/* Selected Batches Summary */}
                      {selectedBatches.length > 0 && (
                        <div className="mt-4 p-3 bg-green-600/20 rounded-lg border border-green-500/30">
                          <div className="text-green-200 font-medium mb-2">
                            Selected Batches ({selectedBatches.length})
                          </div>
                          <div className="text-green-300 text-sm">
                            Total Students:{" "}
                            {selectedBatches.reduce((total, batchId) => {
                              const batch = batches.find((b) => b.id === batchId)
                              return total + (batch?.students?.length || 0)
                            }, 0)}
                          </div>
                        </div>
                      )}
                    </div>

                    {showAIGenerateForm && (
                      <div className="space-y-4">
                        {/* Question Type Selection */}
                        <div className="p-4 bg-blue-900/20 rounded-lg border border-blue-500/30">
                          <h3 className="text-lg font-semibold text-blue-200 mb-3">Question Type</h3>
                          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                            <button
                              onClick={() => setAiQuestionType("mcq")}
                              className={`p-3 rounded-lg border transition-colors ${
                                aiQuestionType === "mcq"
                                  ? "bg-blue-600 border-blue-400 text-white"
                                  : "bg-blue-800/30 border-blue-500/30 text-blue-300 hover:bg-blue-800/50"
                              }`}
                            >
                              <div className="text-center">
                                <div className="font-medium">MCQ Questions</div>
                                <div className="text-xs mt-1">Multiple choice questions</div>
                              </div>
                            </button>
                            
                            <button
                              onClick={() => setAiQuestionType("coding")}
                              className={`p-3 rounded-lg border transition-colors ${
                                aiQuestionType === "coding"
                                  ? "bg-green-600 border-green-400 text-white"
                                  : "bg-green-800/30 border-green-500/30 text-green-300 hover:bg-green-800/50"
                              }`}
                            >
                              <div className="text-center">
                                <div className="font-medium">Coding Questions</div>
                                <div className="text-xs mt-1">Programming challenges</div>
                              </div>
                            </button>
                            
                            <button
                              onClick={() => setAiQuestionType("both")}
                              className={`p-3 rounded-lg border transition-colors ${
                                aiQuestionType === "both"
                                  ? "bg-purple-600 border-purple-400 text-white"
                                  : "bg-purple-800/30 border-purple-500/30 text-purple-300 hover:bg-purple-800/50"
                              }`}
                            >
                              <div className="text-center">
                                <div className="font-medium">Mixed Questions</div>
                                <div className="text-xs mt-1">Both MCQ and coding</div>
                              </div>
                            </button>
                          </div>
                        </div>

                        {/* AI Generation Features */}
                        <div className="p-4 bg-blue-900/20 rounded-lg border border-blue-500/30">
                          <h3 className="text-lg font-semibold text-blue-200 mb-2">AI Generation Features</h3>
                          <ul className="text-blue-300 text-sm space-y-1">
                            <li>• Automatically generates questions based on topic</li>
                            <li>• Adapts difficulty based on student performance</li>
                            <li>• Creates varied question types and formats</li>
                            <li>• Includes explanations and hints</li>
                            {aiQuestionType === "coding" && <li>• Generates test cases and constraints</li>}
                            {aiQuestionType === "both" && <li>• Mixes MCQ and coding questions intelligently</li>}
                          </ul>
                        </div>
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
                      <div className="p-4 bg-purple-900/20 rounded-lg border border-purple-500/30">
                        <h3 className="text-lg font-semibold text-purple-200 mb-2">MCQ Assessment Features</h3>
                        <ul className="text-purple-300 text-sm space-y-1">
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
                  className="bg-black/20 backdrop-blur-md border border-purple-500/30 rounded-lg p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto"
                  onClick={(e) => e.stopPropagation()}
                >
                  <div className="flex justify-between items-center mb-6">
                    <div>
                      <h2 className="text-2xl font-bold text-purple-200">
                        Add Questions to "{currentAssessment.title}"
                      </h2>
                      <p className="text-purple-300">
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
                        <h3 className="text-lg font-semibold text-purple-200">Add New Question</h3>

                        <div>
                          <label className="block text-purple-200 font-medium mb-2">Question *</label>
                          <textarea
                            value={currentQuestion.question}
                            onChange={(e) => setCurrentQuestion({ ...currentQuestion, question: e.target.value })}
                            placeholder="Enter your question here..."
                            className="w-full px-3 py-2 bg-black/20 backdrop-blur-md border border-purple-500/30 rounded-lg text-purple-200 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-400 h-24 resize-none"
                          />
                        </div>

                        <div>
                          <label className="block text-purple-200 font-medium mb-2">Options *</label>
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
                          <label className="block text-purple-200 font-medium mb-2">Explanation</label>
                          <textarea
                            value={currentQuestion.explanation}
                            onChange={(e) => setCurrentQuestion({ ...currentQuestion, explanation: e.target.value })}
                            placeholder="Explain why this is the correct answer..."
                            className="w-full px-3 py-2 bg-black/20 backdrop-blur-md border border-purple-500/30 rounded-lg text-purple-200 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-400 h-20 resize-none"
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
                        <h3 className="text-lg font-semibold text-purple-200">Added Questions ({questions.length})</h3>

                        <div className="max-h-96 overflow-y-auto space-y-3">
                          {questions.map((q, index) => (
                            <div
                              key={q.id}
                              className="p-3 bg-black/20 backdrop-blur-md rounded-lg border border-purple-500/30"
                            >
                              <p className="text-purple-200 font-medium mb-2">
                                Q{index + 1}: {q.question}
                              </p>
                              <div className="space-y-1">
                                {q.options.map((option: string, optIndex: number) => (
                                  <div
                                    key={optIndex}
                                    className={`text-sm ${optIndex === q.correct_answer ? "text-green-300 font-medium" : "text-purple-300"}`}
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
                        <h3 className="text-lg font-semibold text-purple-200">Coding Challenge Questions</h3>
                        <p className="text-purple-300">
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

            {/* AI Generated Questions Review Modal */}
            {showAIGeneratedQuestions && currentAssessment && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 bg-black/30 backdrop-blur-sm flex items-center justify-center z-50 p-4"
                onClick={() => setShowAIGeneratedQuestions(false)}
              >
                <motion.div
                  initial={{ scale: 0.9, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  exit={{ scale: 0.9, opacity: 0 }}
                  className="bg-black/20 backdrop-blur-md border border-purple-500/30 rounded-lg p-6 max-w-6xl w-full max-h-[90vh] overflow-y-auto"
                  onClick={(e) => e.stopPropagation()}
                >
                  <div className="flex justify-between items-center mb-6">
                    <div>
                      <h2 className="text-2xl font-bold text-purple-200">
                        AI Generated Questions - "{currentAssessment.title}"
                      </h2>
                      <p className="text-purple-300">
                        Review the {aiGeneratedQuestions.length} AI-generated questions before posting
                      </p>
                    </div>
                    <Button variant="primary" size="sm" onClick={() => setShowAIGeneratedQuestions(false)}>
                      Close
                    </Button>
                  </div>

                  <div className="space-y-6">
                    {aiGeneratedQuestions.map((question, index) => (
                      <div
                        key={index}
                        className="bg-black/20 backdrop-blur-md rounded-lg p-4 border border-purple-500/30"
                      >
                        <div className="flex items-center justify-between mb-3">
                          <h3 className="text-lg font-semibold text-purple-200">Question {index + 1}</h3>
                          <span
                            className={`px-2 py-1 rounded text-xs font-medium ${
                              question.type === "mcq" ? "bg-blue-600 text-white" : "bg-green-600 text-white"
                            }`}
                          >
                            {question.type === "mcq" ? "MCQ" : "Coding"}
                          </span>
                        </div>

                        {question.type === "mcq" ? (
                          <div className="space-y-3">
                            <div>
                              <h4 className="text-purple-200 font-medium mb-2">Question:</h4>
                              <p className="text-purple-300">{question.question}</p>
                            </div>

                            <div>
                              <h4 className="text-purple-200 font-medium mb-2">Options:</h4>
                              <div className="space-y-2">
                                {question.options.map((option: string, optIndex: number) => (
                                  <div
                                    key={optIndex}
                                    className={`p-2 rounded ${
                                      optIndex === question.correct_answer
                                        ? "bg-green-600/20 border border-green-500 text-green-300"
                                        : "bg-black/20 backdrop-blur-md text-purple-300"
                                    }`}
                                  >
                                    <span className="font-medium">{String.fromCharCode(65 + optIndex)}.</span>
                                    {option}
                                    {optIndex === question.correct_answer && (
                                      <span className="ml-2 text-green-400">✓ Correct Answer</span>
                                    )}
                                  </div>
                                ))}
                              </div>
                            </div>

                            {question.explanation && (
                              <div>
                                <h4 className="text-purple-200 font-medium mb-2">Explanation:</h4>
                                <p className="text-purple-300">{question.explanation}</p>
                              </div>
                            )}

                            <div className="flex items-center space-x-4 text-sm text-purple-400">
                              <span>Points: {question.points}</span>
                            </div>
                          </div>
                        ) : (
                          <div className="space-y-3">
                            <div>
                              <h4 className="text-purple-200 font-medium mb-2">Title:</h4>
                              <p className="text-purple-300">{question.title}</p>
                            </div>

                            <div>
                              <h4 className="text-purple-200 font-medium mb-2">Description:</h4>
                              <p className="text-purple-300">{question.description}</p>
                            </div>

                            {question.test_cases && question.test_cases.length > 0 && (
                              <div>
                                <h4 className="text-purple-200 font-medium mb-2">Test Cases:</h4>
                                <div className="space-y-2">
                                  {question.test_cases.map((testCase: any, tcIndex: number) => (
                                    <div key={tcIndex} className="p-2 bg-black/20 rounded border border-purple-500/30">
                                      <div className="text-sm text-purple-300">
                                        <strong>Input:</strong> {testCase.input}
                                      </div>
                                      <div className="text-sm text-purple-300">
                                        <strong>Expected Output:</strong> {testCase.expected_output}
                                      </div>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}

                            <div className="flex items-center space-x-4 text-sm text-purple-400">
                              <span>Points: {question.points}</span>
                              <span>Difficulty: {question.difficulty}</span>
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>

                  <div className="flex justify-end space-x-3 mt-6">
                    <Button variant="primary" onClick={() => setShowAIGeneratedQuestions(false)}>
                      Cancel
                    </Button>
                    <Button variant="primary" onClick={handlePostTest}>
                      Post the Test
                    </Button>
                  </div>
                </motion.div>
              </motion.div>
            )}

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

            {/* Coding Question Form Modal */}
            {showCodingQuestionForm && currentAssessment && (
              <CodingQuestionForm
                assessmentId={currentAssessment.id}
                onQuestionAdded={handleCodingQuestionAdded}
                onClose={() => setShowCodingQuestionForm(false)}
              />
            )}

            {/* Leaderboard Modal */}
            {showLeaderboard && (
              <Leaderboard
                assessmentId={selectedAssessmentForLeaderboard || "demo-assessment"}
                onClose={() => setShowLeaderboard(false)}
              />
            )}

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