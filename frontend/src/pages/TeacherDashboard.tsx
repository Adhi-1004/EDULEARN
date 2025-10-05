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
import BatchPerformanceControl from "../components/teacher/BatchPerformanceControl"
import AIStudentReports from "../components/teacher/AIStudentReports"
import SmartAssessmentCreator from "../components/teacher/SmartAssessmentCreator"
import api from "../utils/api"
import { ANIMATION_VARIANTS } from "../utils/constants"

interface Student {
  id: string
  name: string
  email: string
  progress: number
  lastActive: string
  batch?: string
  batchId?: string
}

interface Batch {
  id: string
  name: string
  studentCount: number
  createdAt: string
}

const TeacherDashboard: React.FC = () => {
  const { user } = useAuth()
  const { success, error: showError } = useToast()
  
  const [students, setStudents] = useState<Student[]>([])
  const [batches, setBatches] = useState<Batch[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedBatch, setSelectedBatch] = useState<string>("all")
  const [newBatchName, setNewBatchName] = useState("")
  const [showCreateBatch, setShowCreateBatch] = useState(false)
  const [showAddStudent, setShowAddStudent] = useState<string | null>(null)
  const [studentEmail, setStudentEmail] = useState("")
  const [studentName, setStudentName] = useState("")
  const [addingStudent, setAddingStudent] = useState(false)
  const [showStudentManagement, setShowStudentManagement] = useState(false)
  const [showBatchManagement, setShowBatchManagement] = useState(false)
  const [showAssessmentCreation, setShowAssessmentCreation] = useState(false)
  const [selectedStudent, setSelectedStudent] = useState<Student | null>(null)
  const [showMCQForm, setShowMCQForm] = useState(false)
  const [showChallengeForm, setShowChallengeForm] = useState(false)
  const [showBatchPerformance, setShowBatchPerformance] = useState(false)
  const [showAIReports, setShowAIReports] = useState(false)
  const [showSmartAssessment, setShowSmartAssessment] = useState(false)
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
    explanation: ""
  })
  const [showBatchAssignment, setShowBatchAssignment] = useState(false)
  const [selectedBatches, setSelectedBatches] = useState<string[]>([])
  const [showLeaderboard, setShowLeaderboard] = useState(false)
  const [selectedAssessmentForLeaderboard, setSelectedAssessmentForLeaderboard] = useState<string | null>(null)
  const [showCodingQuestionForm, setShowCodingQuestionForm] = useState(false)
  const [aiQuestionType, setAiQuestionType] = useState<'mcq' | 'coding' | 'both'>('mcq')
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
      
      console.log("📊 [TEACHER] Fetching dashboard data...")
      
      // Fetch students from API
      const studentsResponse = await api.get("/api/teacher/students")
      if (studentsResponse.data.success) {
        console.log("🔍 [TEACHER] Raw students data:", studentsResponse.data.students)
        setStudents(studentsResponse.data.students)
        console.log("✅ [TEACHER] Students loaded:", studentsResponse.data.students.length)
      } else {
        console.warn("⚠️ [TEACHER] No students data received")
        setStudents([])
      }
      
      // Fetch batches from API
      const batchesResponse = await api.get("/api/teacher/batches")
      if (batchesResponse.data && Array.isArray(batchesResponse.data)) {
        // Add "All Students" option
        const allStudentsBatch = {
          id: "all",
          name: "All Students",
          studentCount: studentsResponse.data.students?.length || 0,
          createdAt: new Date().toISOString().split('T')[0]
        }
        
        const formattedBatches = [
          allStudentsBatch,
          ...batchesResponse.data.map((batch: any) => ({
            id: batch.batch_id,
            name: batch.batch_name,
            studentCount: batch.total_students,
            createdAt: new Date().toISOString().split('T')[0]
          }))
        ]
        
        setBatches(formattedBatches)
        console.log("✅ [TEACHER] Batches loaded:", formattedBatches.length)
      } else {
        console.warn("⚠️ [TEACHER] No batches data received")
        setBatches([{
          id: "all",
          name: "All Students",
          studentCount: 0,
          createdAt: new Date().toISOString().split('T')[0]
        }])
      }
      
    } catch (err) {
      console.error("❌ [TEACHER] Failed to fetch dashboard data:", err)
      showError("Error", "Failed to load dashboard data")
      
      // Fallback to empty data
      setStudents([])
      setBatches([{
        id: "all",
        name: "All Students",
        studentCount: 0,
        createdAt: new Date().toISOString().split('T')[0]
      }])
    } finally {
      setLoading(false)
    }
  }

  const handleCreateBatch = async () => {
    if (!newBatchName.trim()) {
      showError("Error", "Please enter a batch name")
      return
    }

    try {
      console.log("📝 [TEACHER] Creating batch:", newBatchName)

      const response = await api.post("/api/teacher/batches", {
        name: newBatchName,
        description: `Batch created by ${user?.name || "Teacher"}`,
      })

      if (response.data.success) {
        const newBatch: Batch = {
          id: response.data.batch_id,
          name: newBatchName,
          studentCount: 0,
          createdAt: new Date().toISOString().split("T")[0],
        }

        setBatches((prev) => [...prev, newBatch])
        setNewBatchName("")
        setShowCreateBatch(false)
        success("Success", `Batch "${newBatchName}" created successfully`)
        console.log("✅ [TEACHER] Batch created successfully")
      } else {
        throw new Error(response.data.message || "Failed to create batch")
      }
    } catch (err: any) {
      console.error("❌ [TEACHER] Failed to create batch:", err)
      const errorMessage = err.response?.data?.detail || err.message || "Failed to create batch"
      showError("Error", errorMessage)
    }
  }

  const handleAddStudentToBatch = async (batchId: string) => {
    if (!studentEmail.trim()) {
      showError("Error", "Please enter student email")
      return
    }
    
    try {
      setAddingStudent(true)
      console.log("👤 [TEACHER] Adding student to batch:", { email: studentEmail, batchId })
      console.log("🔍 [TEACHER] Making API call to: /api/teacher/students/add")
      console.log("🔍 [TEACHER] Request payload:", {
        email: studentEmail.trim(),
        name: studentName.trim() || null,
        batch_id: batchId
      })
      
      const response = await api.post("/api/teacher/students/add", {
        email: studentEmail.trim(),
        name: studentName.trim() || null,
        batch_id: batchId
      })
      
      if (response.data.success) {
        success("Success", response.data.message)
        setStudentEmail("")
        setStudentName("")
        setShowAddStudent(null)
        // Refresh the dashboard data
        await fetchDashboardData()
        console.log("✅ [TEACHER] Student added successfully")
      } else {
        throw new Error(response.data.message || "Failed to add student")
      }
    } catch (err: any) {
      console.error("❌ [TEACHER] Failed to add student to batch:", err)
      const errorMessage = err.response?.data?.detail || err.message || "Failed to add student to batch"
      showError("Error", errorMessage)
    } finally {
      setAddingStudent(false)
    }
  }

  const handleRemoveStudentFromBatch = async (studentId: string, batchId: string, studentName: string) => {
    if (!confirm(`Are you sure you want to remove ${studentName} from this batch?`)) {
      return
    }
    
    try {
      console.log("👤 [TEACHER] Removing student from batch:", { studentId, batchId })
      
      const response = await api.post("/api/teacher/students/remove", {
        student_id: studentId,
        batch_id: batchId
      })
      
      if (response.data.success) {
        success("Success", response.data.message)
        // Refresh the dashboard data
        await fetchDashboardData()
        console.log("✅ [TEACHER] Student removed successfully")
      } else {
        throw new Error(response.data.message || "Failed to remove student")
      }
    } catch (err: any) {
      console.error("❌ [TEACHER] Failed to remove student from batch:", err)
      const errorMessage = err.response?.data?.detail || err.message || "Failed to remove student from batch"
      showError("Error", errorMessage)
    }
  }

  const handleManageStudents = () => {
    setShowStudentManagement(!showStudentManagement)
    setShowBatchManagement(false)
    setShowAssessmentCreation(false)
  }

  const handleManageBatches = () => {
    setShowBatchManagement(!showBatchManagement)
    setShowStudentManagement(false)
    setShowAssessmentCreation(false)
  }

  const handleToggleAssessmentCreation = () => {
    setShowAssessmentCreation(!showAssessmentCreation)
    setShowStudentManagement(false)
    setShowBatchManagement(false)
  }

  const handleViewStudentDetails = (student: Student) => {
    setSelectedStudent(student)
  }

  const handleCloseStudentDetails = () => {
    setSelectedStudent(null)
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
      topicTrimmed: assessmentTopic.trim()
    })
    
    if (!assessmentTitle.trim() || !assessmentTopic.trim()) {
      console.log("❌ [ASSESSMENT] Validation failed - missing required fields")
      showError("Error", "Please fill in all required fields")
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

      console.log("🔍 [ASSESSMENT] User info:", user)

      // Create assessment via API
      const response = await api.post("/api/assessments/", {
        title: assessmentTitle,
        subject: assessmentTopic, // Backend expects 'subject' field
        difficulty: assessmentDifficulty,
        description: `AI-generated ${type} assessment on ${assessmentTopic}`,
        time_limit: type === "challenge" ? 60 : 30, // 60 minutes for coding, 30 for MCQ
        max_attempts: 1,
        type: type, // Send the assessment type to backend
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
      console.error("❌ [ASSESSMENT] Error response:", err.response?.data)
      console.error("❌ [ASSESSMENT] Error status:", err.response?.status)
      console.error("❌ [ASSESSMENT] Error headers:", err.response?.headers)

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
    setShowBatchAssignment(true)
  }

  const handleAssignToBatches = async () => {
    if (selectedBatches.length === 0) {
      showError("Error", "Please select at least one batch")
      return
    }

    try {
      // Assign assessment to batches
      await api.post(`/api/assessments/${currentAssessment.id}/assign-batches`, selectedBatches)

      // Publish assessment
      await api.post(`/api/assessments/${currentAssessment.id}/publish`)

      success("Success", `Assessment assigned to ${selectedBatches.length} batch(es) and published successfully!`)

      // Reset everything
      setShowQuestionForm(false)
      setShowBatchAssignment(false)
      setCurrentAssessment(null)
      setQuestions([])
      setSelectedBatches([])
    } catch (err: any) {
      console.error("Failed to assign assessment:", err)
      showError("Error", "Failed to assign assessment. Please try again.")
    }
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
    }
  }

  const handlePostTest = () => {
    if (!currentAssessment) {
      showError("Error", "No assessment selected")
      return
    }
    setShowAIGeneratedQuestions(false)
    setShowBatchAssignment(true)
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
        title: assessmentTitle,
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
          type: "ai",
          questionCount: response.data.generated_count,
        })
      }
    } catch (err: any) {
      console.error("❌ [AI GENERATION] Failed to generate questions:", err)
      showError("Error", "Failed to generate questions. Please try again.")
    } finally {
      setCreatingAssessment(false)
    }
  }

  const filteredStudents = students.filter(student => {
    const studentName = student.name || '';
    const studentEmail = student.email || '';
    const studentBatchId = student.batchId || '';
    
    const matchesSearch = studentName.toLowerCase().includes(searchTerm.toLowerCase()) || 
                          studentEmail.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesBatch = selectedBatch === "all" || studentBatchId === selectedBatch;
    return matchesSearch && matchesBatch;
  });

  if (loading) {
    return (
      <>
        <AnimatedBackground />
        <div className="min-h-screen pt-20 px-4 flex items-center justify-center relative z-10">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-purple-200 mb-4">Loading Dashboard...</h1>
            <p className="text-purple-300">Please wait while we load your data.</p>
          </div>
        </div>
      </>
    );
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
            <motion.div
              variants={ANIMATION_VARIANTS.slideDown}
              className="text-center mb-8"
            >
              <h1 className="text-4xl font-bold text-purple-200 mb-2">
                Teacher Dashboard
              </h1>
              <p className="text-purple-300 text-lg mb-4">
                Welcome back, {user?.name || user?.email || 'Teacher'}!
              </p>
            </motion.div>

            {/* Action Cards */}
            <motion.div
              variants={ANIMATION_VARIANTS.stagger}
              initial="initial"
              animate="animate"
              className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8"
            >
              <motion.div variants={ANIMATION_VARIANTS.slideUp}>
                <Card className="p-6 h-full">
                  <div className="flex items-center mb-4">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 flex items-center justify-center mr-4">
                      <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"
                        />
                      </svg>
                    </div>
                    <h3 className="text-xl font-semibold text-purple-200">Student Management</h3>
                  </div>
                  <p className="text-purple-300 mb-6 leading-relaxed">
                    View and manage all your students, track their progress, and provide feedback.
                  </p>
                  <Button 
                    variant="primary" 
                    className="w-full"
                    onClick={handleManageStudents}
                  >
                    {showStudentManagement ? "Hide Student Management" : "Manage Students"}
                  </Button>
                </Card>
              </motion.div>

              <motion.div variants={ANIMATION_VARIANTS.slideRight}>
                <Card className="p-6 h-full">
                  <div className="flex items-center mb-4">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center mr-4">
                      <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
                        />
                      </svg>
                    </div>
                    <h3 className="text-xl font-semibold text-purple-200">Batch Management</h3>
                  </div>
                  <p className="text-purple-300 mb-6 leading-relaxed">
                    Organize students into batches, create new batches, and manage batch assignments.
                  </p>
                  <Button 
                    variant="primary" 
                    className="w-full"
                    onClick={handleManageBatches}
                  >
                    {showBatchManagement ? "Hide Batch Management" : "Manage Batches"}
                  </Button>
                </Card>
              </motion.div>

              <motion.div variants={ANIMATION_VARIANTS.slideLeft}>
                <Card className="p-6 h-full">
                  <div className="flex items-center mb-4">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-r from-green-500 to-teal-500 flex items-center justify-center mr-4">
                      <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"
                        />
                      </svg>
                    </div>
                    <h3 className="text-xl font-semibold text-purple-200">Assessment Creation</h3>
                  </div>
                  <p className="text-purple-300 mb-6 leading-relaxed">
                    Create custom assessments and coding challenges for your students.
                  </p>
                  <Button 
                    variant="primary" 
                    className="w-full"
                    onClick={handleToggleAssessmentCreation}
                  >
                    {showAssessmentCreation ? "Hide Assessment Creation" : "Create Assessment"}
                  </Button>
                </Card>
              </motion.div>
            </motion.div>

            {/* Enhanced Dashboard Sections */}
            <motion.div
              variants={ANIMATION_VARIANTS.stagger}
              initial="initial"
              animate="animate"
              className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8"
            >
              <motion.div variants={ANIMATION_VARIANTS.slideUp}>
                <Card className="p-6 h-full">
                  <div className="flex items-center mb-4">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-r from-orange-500 to-red-500 flex items-center justify-center mr-4">
                      <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                        />
                      </svg>
                    </div>
                    <h3 className="text-xl font-semibold text-purple-200">Batch Performance</h3>
                  </div>
                  <p className="text-purple-300 mb-6 leading-relaxed">
                    Monitor batch performance at a glance with AI-powered insights and analytics.
                  </p>
                  <Button 
                    variant="primary" 
                    className="w-full"
                    onClick={() => setShowBatchPerformance(!showBatchPerformance)}
                  >
                    {showBatchPerformance ? "Hide Performance Control" : "View Performance Control"}
                  </Button>
                </Card>
              </motion.div>

              <motion.div variants={ANIMATION_VARIANTS.slideRight}>
                <Card className="p-6 h-full">
                  <div className="flex items-center mb-4">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-r from-cyan-500 to-blue-500 flex items-center justify-center mr-4">
                      <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                        />
                      </svg>
                    </div>
                    <h3 className="text-xl font-semibold text-purple-200">AI Student Reports</h3>
                  </div>
                  <p className="text-purple-300 mb-6 leading-relaxed">
                    Generate AI-powered student performance reports with personalized insights.
                  </p>
                  <Button 
                    variant="primary" 
                    className="w-full"
                    onClick={() => setShowAIReports(!showAIReports)}
                  >
                    {showAIReports ? "Hide AI Reports" : "Generate AI Reports"}
                  </Button>
                </Card>
              </motion.div>

              <motion.div variants={ANIMATION_VARIANTS.slideLeft}>
                <Card className="p-6 h-full">
                  <div className="flex items-center mb-4">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-r from-pink-500 to-purple-500 flex items-center justify-center mr-4">
                      <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M13 10V3L4 14h7v7l9-11h-7z"
                        />
                      </svg>
                    </div>
                    <h3 className="text-xl font-semibold text-purple-200">Smart Assessment Creator</h3>
                  </div>
                  <p className="text-purple-300 mb-6 leading-relaxed">
                    Create AI-powered assessments tailored to your students' weaknesses.
                  </p>
                  <Button 
                    variant="primary" 
                    className="w-full"
                    onClick={() => setShowSmartAssessment(!showSmartAssessment)}
                  >
                    {showSmartAssessment ? "Hide Smart Creator" : "Create Smart Assessment"}
                  </Button>
                </Card>
              </motion.div>
            </motion.div>

            {/* Enhanced Dashboard Content */}
            {showBatchPerformance && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                className="mb-8"
              >
                <BatchPerformanceControl teacherId={user?.id || user?._id || ""} />
              </motion.div>
            )}

            {showAIReports && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                className="mb-8"
              >
                <AIStudentReports teacherId={user?.id || user?._id || ""} students={students} />
              </motion.div>
            )}

            {showSmartAssessment && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                className="mb-8"
              >
                <SmartAssessmentCreator
                  teacherId={user?.id || user?._id || ""}
                  onAssessmentCreated={(assessment) => {
                    console.log("Assessment created:", assessment)
                    setShowSmartAssessment(false)
                  }}
                />
              </motion.div>
            )}

            {/* Batch Management Section */}
            <motion.div variants={ANIMATION_VARIANTS.slideUp} className="mb-8">
              <Card className="p-6">
                <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6">
                  <h2 className="text-2xl font-bold text-purple-200 mb-4 md:mb-0">
                    Student Batches
                  </h2>
                  <div className="flex space-x-3">
                    <Button 
                      variant="primary" 
                      onClick={() => setShowCreateBatch(true)}
                    >
                      Create Batch
                    </Button>
                  </div>
                </div>

                {showCreateBatch && (
                  <div className="mb-6 p-4 bg-purple-900/20 rounded-lg border border-purple-500/30">
                    <h3 className="text-lg font-semibold text-purple-200 mb-3">Create New Batch</h3>
                    <div className="flex flex-col sm:flex-row gap-3">
                      <Input
                        type="text"
                        value={newBatchName}
                        onChange={(e) => setNewBatchName(e.target.value)}
                        placeholder="Enter batch name"
                        className="flex-grow"
                      />
                      <div className="flex space-x-2">
                        <Button onClick={handleCreateBatch} variant="primary">
                          Create
                        </Button>
                        <Button 
                          onClick={() => {
                            setShowCreateBatch(false);
                            setNewBatchName("");
                          }} 
                          variant="primary"
                        >
                          Cancel
                        </Button>
                      </div>
                    </div>
                  </div>
                )}

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  {batches.map((batch) => (
                    <div 
                      key={batch.id}
                      className={`p-4 transition-all duration-300 rounded-lg border ${
                        selectedBatch === batch.id 
                          ? "border-purple-400 bg-purple-900/30" 
                          : "border-purple-500/30 hover:border-purple-400/50 hover:bg-purple-900/20"
                      }`}
                    >
                      <div 
                        className="cursor-pointer"
                        onClick={() => setSelectedBatch(batch.id)}
                      >
                        <h3 className="font-semibold text-purple-200">{batch.name}</h3>
                        <p className="text-purple-300 text-sm">{batch.studentCount} students</p>
                        <p className="text-purple-400 text-xs mt-1">
                          Created: {new Date(batch.createdAt).toLocaleDateString()}
                        </p>
                      </div>

                      {/* Add Student Button */}
                      <div className="mt-3">
                        <Button
                          variant="primary"
                          size="sm"
                          onClick={() => setShowAddStudent(showAddStudent === batch.id ? null : batch.id)}
                          className="w-full"
                        >
                          {showAddStudent === batch.id ? "Cancel" : "Add Student"}
                        </Button>
                      </div>

                      {/* Add Student Form */}
                      {showAddStudent === batch.id && (
                        <div className="mt-4 p-3 bg-purple-900/20 rounded-lg border border-purple-500/30">
                          <h4 className="text-sm font-semibold text-purple-200 mb-3">Add Student to {batch.name}</h4>
                          <div className="space-y-3">
                            <Input
                              type="email"
                              value={studentEmail}
                              onChange={(e) => setStudentEmail(e.target.value)}
                              placeholder="Student email"
                              className="w-full"
                            />
                            <Input
                              type="text"
                              value={studentName}
                              onChange={(e) => setStudentName(e.target.value)}
                              placeholder="Student name"
                              className="w-full"
                            />
                            <div className="flex space-x-2">
                              <Button 
                                onClick={() => handleAddStudentToBatch(batch.id)}
                                disabled={addingStudent}
                                variant="primary"
                                size="sm"
                                className="flex-1"
                              >
                                {addingStudent ? "Adding..." : "Add Student"}
                              </Button>
                              <Button 
                                onClick={() => {
                                  setShowAddStudent(null);
                                  setStudentEmail("");
                                  setStudentName("");
                                }}
                                variant="primary"
                                size="sm"
                              >
                                Cancel
                              </Button>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </Card>
            </motion.div>

            {/* Student Management Section */}
            <motion.div variants={ANIMATION_VARIANTS.slideUp} className="mb-8">
              <Card className="p-6">
                <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6">
                  <h2 className="text-2xl font-bold text-purple-200 mb-4 md:mb-0">
                    Student Management
                  </h2>
                  <div className="flex flex-col sm:flex-row gap-3 w-full md:w-auto">
                    <Input
                      type="text"
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      placeholder="Search students..."
                      className="w-full md:w-64"
                    />
                  </div>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-purple-500/30">
                        <th className="text-left py-3 px-4 text-purple-300 font-semibold">Student</th>
                        <th className="text-left py-3 px-4 text-purple-300 font-semibold">Email</th>
                        <th className="text-left py-3 px-4 text-purple-300 font-semibold">Progress</th>
                        <th className="text-left py-3 px-4 text-purple-300 font-semibold">Last Active</th>
                        <th className="text-left py-3 px-4 text-purple-300 font-semibold">Batch</th>
                        <th className="text-left py-3 px-4 text-purple-300 font-semibold">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredStudents.map((student, index) => (
                        <motion.tr
                          key={student.id}
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: index * 0.05 }}
                          className="border-b border-purple-500/20 hover:bg-purple-900/10"
                        >
                          <td className="py-3 px-4 text-purple-200">{student.name || 'Unknown'}</td>
                          <td className="py-3 px-4 text-purple-300">{student.email || 'No email'}</td>
                          <td className="py-3 px-4">
                            <div className="flex items-center">
                              <div className="w-24 bg-purple-900/50 rounded-full h-2 mr-2">
                                <div 
                                  className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full" 
                                  style={{ width: `${student.progress || 0}%` }}
                                ></div>
                              </div>
                              <span className="text-purple-300 text-sm">{student.progress || 0}%</span>
                            </div>
                          </td>
                          <td className="py-3 px-4 text-purple-300">
                            {student.lastActive ? new Date(student.lastActive).toLocaleDateString() : 'Never'}
                          </td>
                          <td className="py-3 px-4">
                            <span className="px-2 py-1 bg-purple-900/30 text-purple-300 rounded-full text-xs">
                              {student.batch || "Unassigned"}
                            </span>
                          </td>
                          <td className="py-3 px-4">
                            <div className="flex space-x-2">
                              <Button 
                                variant="primary" 
                                size="sm"
                                onClick={() => handleViewStudentDetails(student)}
                              >
                                View Details
                              </Button>
                              {student.batch && student.batchId && (
                                <Button 
                                  variant="primary" 
                                  size="sm"
                                  onClick={() => student.batchId && handleRemoveStudentFromBatch(student.id, student.batchId, student.name)}
                                >
                                  Remove
                                </Button>
                              )}
                            </div>
                          </td>
                        </motion.tr>
                      ))}
                    </tbody>
                  </table>

                  {filteredStudents.length === 0 && (
                    <div className="text-center py-8 text-purple-300">
                      No students found matching your criteria.
                    </div>
                  )}
                </div>
              </Card>
            </motion.div>

            {/* Student Management Section */}
            {showStudentManagement && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                className="mb-8"
              >
                <Card className="p-6">
                  <h2 className="text-2xl font-bold text-purple-200 mb-6">
                    Advanced Student Management
                  </h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    <div className="p-4 bg-purple-900/20 rounded-lg border border-purple-500/30">
                      <h3 className="text-lg font-semibold text-purple-200 mb-2">Student Analytics</h3>
                      <p className="text-purple-300 text-sm mb-4">View detailed performance analytics for all students</p>
                      <Button variant="primary" size="sm" className="w-full">
                        View Analytics
                      </Button>
                    </div>
                    <div className="p-4 bg-purple-900/20 rounded-lg border border-purple-500/30">
                      <h3 className="text-lg font-semibold text-purple-200 mb-2">Bulk Actions</h3>
                      <p className="text-purple-300 text-sm mb-4">Perform bulk operations on multiple students</p>
                      <Button variant="primary" size="sm" className="w-full">
                        Bulk Actions
                      </Button>
                    </div>
                    <div className="p-4 bg-purple-900/20 rounded-lg border border-purple-500/30">
                      <h3 className="text-lg font-semibold text-purple-200 mb-2">Export Data</h3>
                      <p className="text-purple-300 text-sm mb-4">Export student data and progress reports</p>
                      <Button variant="primary" size="sm" className="w-full">
                        Export Data
                      </Button>
                    </div>
                  </div>
                </Card>
              </motion.div>
            )}

            {/* Batch Management Section */}
            {showBatchManagement && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                className="mb-8"
              >
                <Card className="p-6">
                  <h2 className="text-2xl font-bold text-purple-200 mb-6">
                    Advanced Batch Management
                  </h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    <div className="p-4 bg-purple-900/20 rounded-lg border border-purple-500/30">
                      <h3 className="text-lg font-semibold text-purple-200 mb-2">Batch Analytics</h3>
                      <p className="text-purple-300 text-sm mb-4">View performance metrics for each batch</p>
                      <Button variant="primary" size="sm" className="w-full">
                        View Analytics
                      </Button>
                    </div>
                    <div className="p-4 bg-purple-900/20 rounded-lg border border-purple-500/30">
                      <h3 className="text-lg font-semibold text-purple-200 mb-2">Batch Settings</h3>
                      <p className="text-purple-300 text-sm mb-4">Configure batch settings and permissions</p>
                      <Button variant="primary" size="sm" className="w-full">
                        Configure
                      </Button>
                    </div>
                    <div className="p-4 bg-purple-900/20 rounded-lg border border-purple-500/30">
                      <h3 className="text-lg font-semibold text-purple-200 mb-2">Import Students</h3>
                      <p className="text-purple-300 text-sm mb-4">Import students from CSV or Excel files</p>
                      <Button variant="primary" size="sm" className="w-full">
                        Import Students
                      </Button>
                    </div>
                  </div>
                </Card>
              </motion.div>
            )}

            {/* Assessment Creation Section */}
            {showAssessmentCreation && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                className="mb-8"
              >
                <Card className="p-6">
                  <h2 className="text-2xl font-bold text-purple-200 mb-6">
                    Assessment Creation Tools
                  </h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    <div className="p-4 bg-purple-900/20 rounded-lg border border-purple-500/30">
                      <h3 className="text-lg font-semibold text-purple-200 mb-2">MCQ Assessments</h3>
                      <p className="text-purple-300 text-sm mb-4">Create multiple choice question assessments</p>
                      <Button 
                        variant="primary" 
                        size="sm" 
                        className="w-full"
                        onClick={handleCreateMCQ}
                      >
                        Create MCQ
                      </Button>
                    </div>
                    <div className="p-4 bg-purple-900/20 rounded-lg border border-purple-500/30">
                      <h3 className="text-lg font-semibold text-purple-200 mb-2">Coding Challenges</h3>
                      <p className="text-purple-300 text-sm mb-4">Create programming challenges and exercises</p>
                      <Button 
                        variant="primary" 
                        size="sm" 
                        className="w-full"
                        onClick={handleCreateChallenge}
                      >
                        Create Challenge
                      </Button>
                    </div>
                    <div className="p-4 bg-purple-900/20 rounded-lg border border-purple-500/30">
                      <h3 className="text-lg font-semibold text-purple-200 mb-2">AI-Generated</h3>
                      <p className="text-purple-300 text-sm mb-4">Use AI to generate custom assessments</p>
                      <Button 
                        variant="primary" 
                        size="sm" 
                        className="w-full"
                        onClick={handleAIGenerate}
                      >
                        AI Generate
                      </Button>
                    </div>
                  </div>
                </Card>
              </motion.div>
            )}

            {/* Student Details Modal */}
            {selectedStudent && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 bg-black/30 backdrop-blur-sm flex items-center justify-center z-50 p-4"
                onClick={handleCloseStudentDetails}
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
                      Student Details: {selectedStudent.name}
                    </h2>
                    <Button 
                      variant="primary" 
                      size="sm"
                      onClick={handleCloseStudentDetails}
                    >
                      Close
                    </Button>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-4">
                      <div>
                        <h3 className="text-lg font-semibold text-purple-200 mb-2">Basic Information</h3>
                        <div className="space-y-2">
                          <p className="text-purple-300"><span className="font-medium">Name:</span> {selectedStudent.name}</p>
                          <p className="text-purple-300"><span className="font-medium">Email:</span> {selectedStudent.email}</p>
                          <p className="text-purple-300"><span className="font-medium">Batch:</span> {selectedStudent.batch || "Unassigned"}</p>
                          <p className="text-purple-300"><span className="font-medium">Last Active:</span> {new Date(selectedStudent.lastActive).toLocaleDateString()}</p>
                        </div>
                      </div>
                    </div>
                    
                    <div className="space-y-4">
                      <div>
                        <h3 className="text-lg font-semibold text-purple-200 mb-2">Progress Overview</h3>
                        <div className="space-y-2">
                          <div className="flex items-center justify-between">
                            <span className="text-purple-300">Overall Progress</span>
                            <span className="text-purple-200 font-medium">{selectedStudent.progress}%</span>
                          </div>
                          <div className="w-full bg-purple-900/50 rounded-full h-2">
                            <div 
                              className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full" 
                              style={{ width: `${selectedStudent.progress}%` }}
                            ></div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="mt-6 flex space-x-3">
                    <Button variant="primary" size="sm">
                      View Full Profile
                    </Button>
                    <Button variant="primary" size="sm">
                      Send Message
                    </Button>
                    <Button variant="primary" size="sm">
                      View Progress
                    </Button>
                  </div>
                </motion.div>
              </motion.div>
            )}

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
                    <Button 
                      variant="primary" 
                      size="sm"
                      onClick={handleCloseAssessmentForm}
                    >
                      Close
                    </Button>
                  </div>
                  
                  <div className="space-y-4">
                    <div>
                      <label className="block text-purple-200 font-medium mb-2">
                        Assessment Title *
                      </label>
                      <Input
                        type="text"
                        value={assessmentTitle}
                        onChange={(e) => setAssessmentTitle(e.target.value)}
                        placeholder="Enter assessment title"
                        className="w-full"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-purple-200 font-medium mb-2">
                        Topic *
                      </label>
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
                        <label className="block text-purple-200 font-medium mb-2">
                          Difficulty
                        </label>
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
                        <label className="block text-purple-200 font-medium mb-2">
                          Number of Questions
                        </label>
                        <Input
                          type="number"
                          value={questionCount}
                          onChange={(e) => setQuestionCount(parseInt(e.target.value) || 10)}
                          min="1"
                          max="50"
                          className="w-full"
                        />
                      </div>
                    </div>

                    {showAIGenerateForm && (
                      <div className="space-y-4">
                        {/* Question Type Selection */}
                        <div className="p-4 bg-blue-900/20 rounded-lg border border-blue-500/30">
                          <h3 className="text-lg font-semibold text-blue-200 mb-3">Question Type</h3>
                          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                            <button
                              onClick={() => setAiQuestionType('mcq')}
                              className={`p-3 rounded-lg border transition-colors ${
                                aiQuestionType === 'mcq'
                                  ? 'bg-blue-600 border-blue-400 text-white'
                                  : 'bg-blue-800/30 border-blue-500/30 text-blue-300 hover:bg-blue-800/50'
                              }`}
                            >
                              <div className="text-center">
                                <div className="font-medium">MCQ Questions</div>
                                <div className="text-xs mt-1">Multiple choice questions</div>
                              </div>
                            </button>
                            
                            <button
                              onClick={() => setAiQuestionType('coding')}
                              className={`p-3 rounded-lg border transition-colors ${
                                aiQuestionType === 'coding'
                                  ? 'bg-green-600 border-green-400 text-white'
                                  : 'bg-green-800/30 border-green-500/30 text-green-300 hover:bg-green-800/50'
                              }`}
                            >
                              <div className="text-center">
                                <div className="font-medium">Coding Questions</div>
                                <div className="text-xs mt-1">Programming challenges</div>
                              </div>
                            </button>
                            
                            <button
                              onClick={() => setAiQuestionType('both')}
                              className={`p-3 rounded-lg border transition-colors ${
                                aiQuestionType === 'both'
                                  ? 'bg-purple-600 border-purple-400 text-white'
                                  : 'bg-purple-800/30 border-purple-500/30 text-purple-300 hover:bg-purple-800/50'
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
                            {aiQuestionType === 'coding' && (
                              <li>• Generates test cases and constraints</li>
                            )}
                            {aiQuestionType === 'both' && (
                              <li>• Mixes MCQ and coding questions intelligently</li>
                            )}
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
                          assessmentTopic
                        })
                        if (showMCQForm) {
                          console.log("🔍 [BUTTON] Calling handleCreateAssessment('mcq')")
                          handleCreateAssessment('mcq');
                        }
                        if (showChallengeForm) {
                          console.log("🔍 [BUTTON] Calling handleCreateAssessment('challenge')")
                          handleCreateAssessment('challenge');
                        }
                        if (showAIGenerateForm) {
                          console.log("🔍 [BUTTON] Calling handleCreateAssessment('ai')")
                          handleCreateAssessment('ai');
                        }
                      }}
                      disabled={creatingAssessment}
                      className="flex-1"
                    >
                      {creatingAssessment ? "Creating..." : "Create Assessment"}
                    </Button>
                    <Button 
                      variant="primary" 
                      size="sm"
                      onClick={handleCloseAssessmentForm}
                    >
                      Cancel
                    </Button>
                  </div>
                  
                  <div className="mt-4">
                    <Button 
                      variant="primary" 
                      size="sm"
                      onClick={() => setShowLeaderboard(true)}
                      className="w-full"
                    >
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
                    <Button 
                      variant="primary" 
                      size="sm"
                      onClick={() => setShowQuestionForm(false)}
                    >
                      Close
                    </Button>
                  </div>

                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Question Form - Only show for MCQ and AI assessments */}
                    {currentAssessment.type !== "challenge" && (
                      <div className="space-y-4">
                        <h3 className="text-lg font-semibold text-purple-200">Add New Question</h3>
                        
                        <div>
                          <label className="block text-purple-200 font-medium mb-2">
                            Question *
                          </label>
                          <textarea
                            value={currentQuestion.question}
                            onChange={(e) => setCurrentQuestion({...currentQuestion, question: e.target.value})}
                            placeholder="Enter your question here..."
                            className="w-full px-3 py-2 bg-black/20 backdrop-blur-md border border-purple-500/30 rounded-lg text-purple-200 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-400 h-24 resize-none"
                          />
                        </div>
                      
                      <div>
                        <label className="block text-purple-200 font-medium mb-2">
                          Options *
                        </label>
                        {currentQuestion.options.map((option, index) => (
                          <div key={index} className="flex items-center mb-2">
                            <input
                              type="radio"
                              name="correctAnswer"
                              checked={currentQuestion.correct_answer === index}
                              onChange={() => setCurrentQuestion({...currentQuestion, correct_answer: index})}
                              className="mr-3"
                            />
                            <Input
                              type="text"
                              value={option}
                              onChange={(e) => {
                                const newOptions = [...currentQuestion.options];
                                newOptions[index] = e.target.value;
                                setCurrentQuestion({...currentQuestion, options: newOptions});
                              }}
                              placeholder={`Option ${index + 1}`}
                              className="flex-1"
                            />
                          </div>
                        ))}
                      </div>
                      
                      <div>
                        <label className="block text-purple-200 font-medium mb-2">
                          Explanation
                        </label>
                        <textarea
                          value={currentQuestion.explanation}
                          onChange={(e) => setCurrentQuestion({...currentQuestion, explanation: e.target.value})}
                          placeholder="Explain why this is the correct answer..."
                          className="w-full px-3 py-2 bg-black/20 backdrop-blur-md border border-purple-500/30 rounded-lg text-purple-200 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-400 h-20 resize-none"
                        />
                      </div>
                      
                        <Button 
                          variant="primary" 
                          onClick={handleAddQuestion}
                          className="w-full"
                        >
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
                          <div key={q.id} className="p-3 bg-black/20 backdrop-blur-md rounded-lg border border-purple-500/30">
                            <p className="text-purple-200 font-medium mb-2">
                              Q{index + 1}: {q.question}
                            </p>
                            <div className="space-y-1">
                              {q.options.map((option: string, optIndex: number) => (
                                <div key={optIndex} className={`text-sm ${optIndex === q.correct_answer ? 'text-green-300 font-medium' : 'text-purple-300'}`}>
                                  {optIndex === q.correct_answer ? '✓ ' : '  '}{option}
                                </div>
                              ))}
                            </div>
                          </div>
                        ))}
                      </div>
                      
                        {questions.length > 0 && (
                          <div className="flex space-x-3">
                            <Button 
                              variant="primary" 
                              onClick={handleSubmitAssessment}
                              className="flex-1"
                            >
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
                        <p className="text-purple-300">Add coding questions with problem statements, test cases, and constraints.</p>
                        
                        <Button 
                          variant="primary" 
                          onClick={handleAddCodingQuestion}
                          className="w-full"
                        >
                          Add Coding Question
                        </Button>
                        
                        {questions.length > 0 && (
                          <div className="flex space-x-3">
                            <Button 
                              variant="primary" 
                              onClick={handleSubmitAssessment}
                              className="flex-1"
                            >
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

            {/* Batch Assignment Modal */}
            {showBatchAssignment && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 bg-black/30 backdrop-blur-sm flex items-center justify-center z-50 p-4"
                onClick={() => setShowBatchAssignment(false)}
              >
                <motion.div
                  initial={{ scale: 0.9, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  exit={{ scale: 0.9, opacity: 0 }}
                  className="bg-black/20 backdrop-blur-md border border-purple-500/30 rounded-lg p-6 max-w-2xl w-full"
                  onClick={(e) => e.stopPropagation()}
                >
                  <div className="flex justify-between items-center mb-6">
                    <h2 className="text-2xl font-bold text-purple-200">
                      Assign to Batches
                    </h2>
                    <Button 
                      variant="primary" 
                      size="sm"
                      onClick={() => setShowBatchAssignment(false)}
                    >
                      Close
                    </Button>
                  </div>
                  
                  <div className="space-y-4">
                    <p className="text-purple-300">
                      Select which batches should receive this assessment:
                    </p>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {batches.filter(batch => batch.id !== "all").map((batch) => (
                        <label key={batch.id} className="flex items-center p-3 bg-black/20 backdrop-blur-md rounded-lg border border-purple-500/30 cursor-pointer hover:bg-black/30">
                          <input
                            type="checkbox"
                            checked={selectedBatches.includes(batch.id)}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setSelectedBatches([...selectedBatches, batch.id]);
                              } else {
                                setSelectedBatches(selectedBatches.filter(id => id !== batch.id));
                              }
                            }}
                            className="mr-3"
                          />
                          <div>
                            <div className="text-purple-200 font-medium">{batch.name}</div>
                            <div className="text-purple-300 text-sm">{batch.studentCount} students</div>
                          </div>
                        </label>
                      ))}
                    </div>
                    
                    <div className="flex space-x-3">
                      <Button 
                        variant="primary" 
                        onClick={handleAssignToBatches}
                        className="flex-1"
                      >
                        Assign Assessment
                      </Button>
                      <Button 
                        variant="primary" 
                        onClick={() => setShowBatchAssignment(false)}
                      >
                        Cancel
                      </Button>
                    </div>
                  </div>
                </motion.div>
              </motion.div>
            )}

            {/* Leaderboard Modal */}
            {showLeaderboard && (
              <Leaderboard
                assessmentId={selectedAssessmentForLeaderboard || "demo-assessment"}
                onClose={() => {
                  setShowLeaderboard(false)
                  setSelectedAssessmentForLeaderboard(null)
                }}
              />
            )}

            {/* Coding Question Form Modal */}
            {showCodingQuestionForm && currentAssessment && (
              <CodingQuestionForm
                assessmentId={currentAssessment.id}
                onQuestionAdded={handleCodingQuestionAdded}
                onClose={() => setShowCodingQuestionForm(false)}
              />
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
                    <Button 
                      variant="primary" 
                      size="sm"
                      onClick={() => setShowAIGeneratedQuestions(false)}
                    >
                      Close
                    </Button>
                  </div>

                  <div className="space-y-6">
                    {aiGeneratedQuestions.map((question, index) => (
                      <div key={index} className="bg-black/20 backdrop-blur-md rounded-lg p-4 border border-purple-500/30">
                        <div className="flex items-center justify-between mb-3">
                          <h3 className="text-lg font-semibold text-purple-200">
                            Question {index + 1}
                          </h3>
                          <span className={`px-2 py-1 rounded text-xs font-medium ${
                            question.type === 'mcq' 
                              ? 'bg-blue-600 text-white' 
                              : 'bg-green-600 text-white'
                          }`}>
                            {question.type === 'mcq' ? 'MCQ' : 'Coding'}
                          </span>
                        </div>

                        {question.type === 'mcq' ? (
                          <div className="space-y-3">
                            <div>
                              <h4 className="text-purple-200 font-medium mb-2">Question:</h4>
                              <p className="text-purple-300">{question.question}</p>
                            </div>
                            
                            <div>
                              <h4 className="text-purple-200 font-medium mb-2">Options:</h4>
                              <div className="space-y-2">
                                {question.options.map((option: string, optIndex: number) => (
                                  <div key={optIndex} className={`p-2 rounded ${
                                    optIndex === question.correct_answer
                                      ? 'bg-green-600/20 border border-green-500 text-green-300'
                                      : 'bg-black/20 backdrop-blur-md text-purple-300'
                                  }`}>
                                    <span className="font-medium">
                                      {String.fromCharCode(65 + optIndex)}. 
                                    </span>
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

                            <div>
                              <h4 className="text-purple-200 font-medium mb-2">Problem Statement:</h4>
                              <p className="text-purple-300 whitespace-pre-wrap">{question.problem_statement}</p>
                            </div>

                            {question.constraints && question.constraints.length > 0 && (
                              <div>
                                <h4 className="text-purple-200 font-medium mb-2">Constraints:</h4>
                                <ul className="text-purple-300 space-y-1">
                                  {question.constraints.map((constraint: string, idx: number) => (
                                    <li key={idx}>• {constraint}</li>
                                  ))}
                                </ul>
                              </div>
                            )}

                            {question.examples && question.examples.length > 0 && (
                              <div>
                                <h4 className="text-purple-200 font-medium mb-2">Examples:</h4>
                                <div className="space-y-2">
                                  {question.examples.map((example: any, idx: number) => (
                                    <div key={idx} className="bg-black/20 backdrop-blur-md rounded p-3">
                                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                        <div>
                                          <span className="text-purple-200 font-medium">Input:</span>
                                          <pre className="text-purple-300 text-sm mt-1">{example.input}</pre>
                                        </div>
                                        <div>
                                          <span className="text-purple-200 font-medium">Output:</span>
                                          <pre className="text-purple-300 text-sm mt-1">{example.output}</pre>
                                        </div>
                                      </div>
                                      {example.explanation && (
                                        <div className="mt-2">
                                          <span className="text-purple-200 font-medium">Explanation:</span>
                                          <p className="text-purple-300 text-sm mt-1">{example.explanation}</p>
                                        </div>
                                      )}
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}

                            <div className="flex items-center space-x-4 text-sm text-purple-400">
                              <span>Points: {question.points}</span>
                              <span>Time Limit: {question.time_limit}s</span>
                              <span>Memory Limit: {question.memory_limit}MB</span>
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>

                  <div className="flex justify-end space-x-3 mt-6">
                    <Button
                      variant="primary"
                      onClick={() => setShowAIGeneratedQuestions(false)}
                    >
                      Cancel
                    </Button>
                    <Button
                      variant="primary"
                      onClick={handlePostTest}
                    >
                      Post the Test
                    </Button>
                  </div>
                </motion.div>
              </motion.div>
            )}
          </Card>
        </motion.div>
      </div>
    </>
  )
}

export default TeacherDashboard
