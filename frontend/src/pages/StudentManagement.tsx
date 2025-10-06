"use client"

import React from "react"
import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { useToast } from "../contexts/ToastContext"
import { useAuth } from "../hooks/useAuth"
import Card from "../components/ui/Card"
import Button from "../components/ui/Button"
import Input from "../components/ui/Input"
import AnimatedBackground from "../components/AnimatedBackground"
import BatchPerformanceControl from "../components/teacher/BatchPerformanceControl"
import AIStudentReports from "../components/teacher/AIStudentReports"
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
  students?: Student[]
}

const StudentManagement: React.FC = () => {
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
  const [showBatchAssignmentModal, setShowBatchAssignmentModal] = useState(false)
  const [selectedStudentsForBatch, setSelectedStudentsForBatch] = useState<string[]>([])
  const [targetBatchId, setTargetBatchId] = useState<string>("")
  const [batchAssignmentSearchTerm, setBatchAssignmentSearchTerm] = useState("")
  const [showBatchChangeModal, setShowBatchChangeModal] = useState(false)
  const [selectedStudentForBatchChange, setSelectedStudentForBatchChange] = useState<Student | null>(null)
  const [newBatchId, setNewBatchId] = useState<string>("")
  const [expandedStudentId, setExpandedStudentId] = useState<string | null>(null)
  const [showStudentDetailsModal, setShowStudentDetailsModal] = useState(false)
  const [selectedStudentForDetails, setSelectedStudentForDetails] = useState<Student | null>(null)
  const [showBatchPerformance, setShowBatchPerformance] = useState(false)
  const [showAIReports, setShowAIReports] = useState(false)

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
      
      
      // Fetch students from API
      const studentsResponse = await api.get("/api/teacher/students")
      if (studentsResponse.data.success) {
        setStudents(studentsResponse.data.students)
      } else {
        console.warn("⚠️ [STUDENT MANAGEMENT] No students data received")
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
          createdAt: new Date().toISOString().split("T")[0],
        }
        
        const formattedBatches = [
          allStudentsBatch,
          ...batchesResponse.data.map((batch: any) => ({
            id: batch.batch_id,
            name: batch.batch_name,
            studentCount: batch.total_students,
            createdAt: new Date().toISOString().split("T")[0],
          })),
        ]
        
        setBatches(formattedBatches)
      } else {
        console.warn("⚠️ [STUDENT MANAGEMENT] No batches data received")
        setBatches([
          {
            id: "all",
            name: "All Students",
            studentCount: 0,
            createdAt: new Date().toISOString().split("T")[0],
          },
        ])
      }
      
    } catch (err) {
      console.error("❌ [STUDENT MANAGEMENT] Failed to fetch dashboard data:", err)
      showError("Error", "Failed to load dashboard data")
      
      // Fallback to empty data
      setStudents([])
      setBatches([
        {
          id: "all",
          name: "All Students",
          studentCount: 0,
          createdAt: new Date().toISOString().split("T")[0],
        },
      ])
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
      } else {
        throw new Error(response.data.message || "Failed to create batch")
      }
    } catch (err: any) {
      console.error("❌ [STUDENT MANAGEMENT] Failed to create batch:", err)
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
      
      const response = await api.post("/api/teacher/students/add", {
        email: studentEmail.trim(),
        name: studentName.trim() || null,
        batch_id: batchId,
      })
      
      if (response.data.success) {
        success("Success", response.data.message)
        setStudentEmail("")
        setStudentName("")
        setShowAddStudent(null)
        // Refresh the dashboard data
        await fetchDashboardData()
      } else {
        throw new Error(response.data.message || "Failed to add student")
      }
    } catch (err: any) {
      console.error("❌ [STUDENT MANAGEMENT] Failed to add student to batch:", err)
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
      
      const response = await api.post("/api/teacher/students/remove", {
        student_id: studentId,
        batch_id: batchId,
      })
      
      if (response.data.success) {
        success("Success", response.data.message)
        // Refresh the dashboard data
        await fetchDashboardData()
      } else {
        throw new Error(response.data.message || "Failed to remove student")
      }
    } catch (err: any) {
      console.error("❌ [STUDENT MANAGEMENT] Failed to remove student from batch:", err)
      const errorMessage = err.response?.data?.detail || err.message || "Failed to remove student from batch"
      showError("Error", errorMessage)
    }
  }

  // Batch Assignment Functions
  const handleOpenBatchAssignment = () => {
    setShowBatchAssignmentModal(true)
    setSelectedStudentsForBatch([])
    setTargetBatchId("")
    setBatchAssignmentSearchTerm("")
  }

  const handleCloseBatchAssignment = () => {
    setShowBatchAssignmentModal(false)
    setSelectedStudentsForBatch([])
    setTargetBatchId("")
    setBatchAssignmentSearchTerm("")
  }

  const handleStudentSelection = (studentId: string) => {
    setSelectedStudentsForBatch((prev) =>
      prev.includes(studentId) ? prev.filter((id) => id !== studentId) : [...prev, studentId],
    )
  }

  const handleSelectAllStudents = () => {
    const allStudentIds = students.map((student) => student.id)
    setSelectedStudentsForBatch(allStudentIds)
  }

  const handleClearAllStudents = () => {
    setSelectedStudentsForBatch([])
  }

  const handleBulkAssignToBatch = async () => {
    if (!targetBatchId) {
      showError("Error", "Please select a batch")
      return
    }

    if (selectedStudentsForBatch.length === 0) {
      showError("Error", "Please select at least one student")
      return
    }

    try {
      const batch = batches.find((b) => b.id === targetBatchId)
      if (!batch) {
        showError("Error", "Selected batch not found")
        return
      }

      // Add students to batch
      for (const studentId of selectedStudentsForBatch) {
        const student = students.find((s) => s.id === studentId)
        if (student) {
          await api.post("/api/teacher/students/add", {
            email: student.email,
            name: student.name,
            batch_id: targetBatchId,
          })
        }
      }

      success("Success", `Added ${selectedStudentsForBatch.length} students to ${batch.name}`)
      handleCloseBatchAssignment()
      await fetchDashboardData()
    } catch (err: any) {
      console.error("❌ [BATCH] Failed to assign students:", err)
      const errorMessage = err.response?.data?.detail || err.message || "Failed to assign students to batch"
      showError("Error", errorMessage)
    }
  }

  const handleOpenBatchChangeModal = (student: Student) => {
    setSelectedStudentForBatchChange(student)
    setNewBatchId(student.batchId || "")
    setShowBatchChangeModal(true)
  }

  const handleCloseBatchChangeModal = () => {
    setShowBatchChangeModal(false)
    setSelectedStudentForBatchChange(null)
    setNewBatchId("")
  }

  const handleChangeStudentBatch = async () => {
    if (!selectedStudentForBatchChange || !newBatchId) {
      showError("Error", "Please select a student and new batch")
      return
    }

    if (String(selectedStudentForBatchChange.batchId) === String(newBatchId)) {
      showError("Error", "Student is already in this batch")
      return
    }

    try {
      // Remove from current batch if exists
      if (selectedStudentForBatchChange.batchId) {
        try {
          await api.post("/api/teacher/students/remove", {
            student_id: selectedStudentForBatchChange.id,
            batch_id: selectedStudentForBatchChange.batchId,
          })
        } catch (err: any) {
          console.error("❌ [BATCH] Failed to remove from current batch:", err)
        }
      }

      // Add to new batch
      await api.post("/api/teacher/students/add", {
        email: selectedStudentForBatchChange.email,
        name: selectedStudentForBatchChange.name,
        batch_id: newBatchId,
      })

      const newBatch = batches.find((b) => b.id === newBatchId)
      success("Success", `Moved ${selectedStudentForBatchChange.name} to ${newBatch?.name || "new batch"}`)
      handleCloseBatchChangeModal()
      await fetchDashboardData()
    } catch (err: any) {
      console.error("❌ [BATCH] Failed to change student batch:", err)
      const errorMessage = err.response?.data?.detail || err.message || "Failed to change student batch"
      showError("Error", errorMessage)
    }
  }

  const handleBatchChangeFromDropdown = async (studentId: string, newBatchId: string) => {
    const student = students.find((s) => s.id === studentId)
    if (!student) {
      showError("Error", "Student not found")
      return
    }

    if (String(student.batchId) === String(newBatchId)) {
      return // No change needed
    }

    try {
      // Remove from current batch if exists
      if (student.batchId) {
        try {
          await api.post("/api/teacher/students/remove", {
            student_id: studentId,
            batch_id: student.batchId,
          })
        } catch (err: any) {
          console.error("❌ [BATCH] Failed to remove from current batch:", err)
        }
      }

      // Add to new batch
      if (newBatchId) {
        await api.post("/api/teacher/students/add", {
          email: student.email,
          name: student.name,
          batch_id: newBatchId,
        })
      }

      const newBatch = batches.find((b) => b.id === newBatchId)
      success("Success", `Moved ${student.name} to ${newBatch?.name || "unassigned"}`)
      await fetchDashboardData()
    } catch (err: any) {
      console.error("❌ [BATCH] Failed to change student batch:", err)
      const errorMessage = err.response?.data?.detail || err.message || "Failed to change student batch"
      showError("Error", errorMessage)
    }
  }

  const handleToggleStudentExpansion = (studentId: string) => {
    setExpandedStudentId(expandedStudentId === studentId ? null : studentId)
  }

  const handleOpenStudentDetails = (student: Student) => {
    setSelectedStudentForDetails(student)
    setShowStudentDetailsModal(true)
  }

  const filteredStudents = students.filter((student) => {
    const studentName = student.name || ""
    const studentEmail = student.email || ""
    const studentBatchId = student.batchId || ""

    const matchesSearch =
      studentName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      studentEmail.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesBatch = selectedBatch === "all" || studentBatchId === selectedBatch
    return matchesSearch && matchesBatch
  })

  if (loading) {
    return (
      <>
        <AnimatedBackground />
        <div className="min-h-screen pt-20 px-4 flex items-center justify-center relative z-10">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-purple-200 mb-4">Loading Student Management...</h1>
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
              <h1 className="text-4xl font-bold text-purple-200 mb-2">Student Management</h1>
              <p className="text-purple-300 text-lg mb-4">
                Manage students, batches, and assignments
              </p>
            </motion.div>

            {/* Quick Stats */}
            <motion.div
              variants={ANIMATION_VARIANTS.slideUp}
              initial="initial"
              animate="animate"
              className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8"
            >
              <div className="bg-gradient-to-r from-blue-500/20 to-blue-600/20 border border-blue-500/30 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-blue-300 text-sm font-medium">Total Students</p>
                    <p className="text-2xl font-bold text-blue-200">{students.length}</p>
                  </div>
                  <div className="w-8 h-8 bg-blue-500/30 rounded-full flex items-center justify-center">
                    <svg className="w-4 h-4 text-blue-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
                    </svg>
                  </div>
                </div>
              </div>

              <div className="bg-gradient-to-r from-purple-500/20 to-purple-600/20 border border-purple-500/30 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-purple-300 text-sm font-medium">Active Batches</p>
                    <p className="text-2xl font-bold text-purple-200">{batches.filter((b) => b.id !== "all").length}</p>
                  </div>
                  <div className="w-8 h-8 bg-purple-500/30 rounded-full flex items-center justify-center">
                    <svg className="w-4 h-4 text-purple-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                    </svg>
                  </div>
                </div>
              </div>

              <div className="bg-gradient-to-r from-orange-500/20 to-orange-600/20 border border-orange-500/30 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-orange-300 text-sm font-medium">Avg. Progress</p>
                    <p className="text-2xl font-bold text-orange-200">
                      {students.length > 0
                        ? Math.round(students.reduce((acc, student) => acc + student.progress, 0) / students.length)
                        : 0}
                      %
                    </p>
                  </div>
                  <div className="w-8 h-8 bg-orange-500/30 rounded-full flex items-center justify-center">
                    <svg className="w-4 h-4 text-orange-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                    </svg>
                  </div>
                </div>
              </div>
            </motion.div>

            {/* Student Batches Section */}
            <motion.div variants={ANIMATION_VARIANTS.slideUp} className="mb-8">
              <Card className="p-6">
                <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6">
                  <h2 className="text-2xl font-bold text-purple-200 mb-4 md:mb-0">Student Batches</h2>
                  <div className="flex space-x-3">
                    <Button variant="primary" onClick={() => setShowCreateBatch(true)}>
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
                            setShowCreateBatch(false)
                            setNewBatchName("")
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
                      <div className="cursor-pointer" onClick={() => setSelectedBatch(batch.id)}>
                        <h3 className="font-semibold text-purple-200">{batch.name}</h3>
                        <p className="text-purple-300 text-sm">{batch.studentCount} students</p>
                        <p className="text-purple-400 text-xs mt-1">
                          Created: {new Date(batch.createdAt).toLocaleDateString()}
                        </p>
                      </div>

                      {/* Add Student Buttons */}
                      <div className="mt-3 space-y-2">
                        <Button
                          variant="primary"
                          size="sm"
                          onClick={() => setShowAddStudent(showAddStudent === batch.id ? null : batch.id)}
                          className="w-full"
                        >
                          {showAddStudent === batch.id ? "Cancel" : "Add Student"}
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => {
                            setTargetBatchId(batch.id)
                            setShowBatchAssignmentModal(true)
                          }}
                          className="w-full"
                        >
                          Bulk Add Students
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
                                  setShowAddStudent(null)
                                  setStudentEmail("")
                                  setStudentName("")
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
                  <h2 className="text-2xl font-bold text-purple-200 mb-4 md:mb-0">Student Management</h2>
                  <div className="flex flex-col sm:flex-row gap-3 w-full md:w-auto">
                    <Input
                      type="text"
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      placeholder="Search students..."
                      className="w-full md:w-64"
                    />
                    <Button
                      variant="outline"
                      onClick={handleOpenBatchAssignment}
                      className="w-full sm:w-auto bg-transparent"
                    >
                      Assign to Batch
                    </Button>
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
                        <th className="text-center py-3 px-4 text-purple-300 font-semibold">Details</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredStudents.map((student, index) => (
                        <React.Fragment key={student.id}>
                          <motion.tr
                            key={student.id}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: index * 0.05 }}
                            className="border-b border-purple-500/20 hover:bg-purple-900/10"
                          >
                            <td className="py-3 px-4 text-purple-200">{student.name || "Unknown"}</td>
                            <td className="py-3 px-4 text-purple-300">{student.email || "No email"}</td>
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
                              {student.lastActive ? new Date(student.lastActive).toLocaleDateString() : "Never"}
                            </td>
                            <td className="py-3 px-4">
                              <select
                                value={student.batchId || ""}
                                onChange={(e) => handleBatchChangeFromDropdown(student.id, e.target.value)}
                                className="px-3 py-2 bg-purple-900/30 backdrop-blur-md border border-purple-500/50 rounded-lg text-purple-200 focus:border-purple-400 focus:outline-none focus:ring-2 focus:ring-purple-500/30 text-sm hover:bg-purple-800/40 transition-colors"
                              >
                                <option value="">Unassigned</option>
                                {batches
                                  .filter((batch) => batch.id !== "all")
                                  .map((batch) => (
                                    <option key={batch.id} value={batch.id}>
                                      {batch.name}
                                    </option>
                                  ))}
                              </select>
                            </td>
                            <td className="py-3 px-4 text-center">
                              <button
                                onClick={() => handleToggleStudentExpansion(student.id)}
                                className="p-2 hover:bg-purple-800/30 rounded-lg transition-colors"
                                aria-expanded={expandedStudentId === student.id}
                                aria-label="Toggle student details"
                              >
                                <svg
                                  className={`w-5 h-5 text-purple-400 transition-transform ${
                                    expandedStudentId === student.id ? "rotate-180" : ""
                                  }`}
                                  fill="none"
                                  stroke="currentColor"
                                  viewBox="0 0 24 24"
                                  aria-hidden="true"
                                >
                                  <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={2}
                                    d="M19 9l-7 7-7-7"
                                  />
                                </svg>
                              </button>
                            </td>
                          </motion.tr>

                          {expandedStudentId === student.id && (
                            <tr key={`${student.id}-details`} className="border-b border-purple-500/20">
                              <td colSpan={6} className="p-0">
                                <motion.div
                                  initial={{ opacity: 0, y: -20 }}
                                  animate={{ opacity: 1, y: 0 }}
                                  exit={{ opacity: 0, y: -20 }}
                                  transition={{ duration: 0.4, ease: "easeInOut" }}
                                  className="bg-gradient-to-r from-purple-800/20 to-blue-800/20 border-t border-purple-500/30 shadow-lg"
                                >
                                  <div className="p-6">
                                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                      {/* Student Information */}
                                      <div className="space-y-3">
                                        <h4 className="text-lg font-semibold text-purple-200 mb-4 flex items-center">
                                          <svg
                                            className="w-5 h-5 mr-2 text-purple-400"
                                            fill="none"
                                            stroke="currentColor"
                                            viewBox="0 0 24 24"
                                          >
                                            <path
                                              strokeLinecap="round"
                                              strokeLinejoin="round"
                                              strokeWidth={2}
                                              d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                                            />
                                          </svg>
                                          Student Information
                                        </h4>
                                        <div className="space-y-2">
                                          <div className="flex justify-between items-center py-2 px-3 bg-purple-900/30 rounded-lg">
                                            <span className="text-purple-300 font-medium">Name:</span>
                                            <span className="text-purple-200">{student.name || "Unknown"}</span>
                                          </div>
                                          <div className="flex justify-between items-center py-2 px-3 bg-purple-900/30 rounded-lg">
                                            <span className="text-purple-300 font-medium">Email:</span>
                                            <span className="text-purple-200">{student.email || "No email"}</span>
                                          </div>
                                          <div className="flex justify-between items-center py-2 px-3 bg-purple-900/30 rounded-lg">
                                            <span className="text-purple-300 font-medium">Current Batch:</span>
                                            <span className="text-purple-200">{student.batch || "Unassigned"}</span>
                                          </div>
                                          <div className="flex justify-between items-center py-2 px-3 bg-purple-900/30 rounded-lg">
                                            <span className="text-purple-300 font-medium">Progress:</span>
                                            <span className="text-purple-200">{student.progress || 0}%</span>
                                          </div>
                                          <div className="flex justify-between items-center py-2 px-3 bg-purple-900/30 rounded-lg">
                                            <span className="text-purple-300 font-medium">Last Active:</span>
                                            <span className="text-purple-200">
                                              {student.lastActive
                                                ? new Date(student.lastActive).toLocaleDateString()
                                                : "Never"}
                                            </span>
                                          </div>
                                        </div>
                                      </div>

                                      {/* Performance Metrics */}
                                      <div className="space-y-3">
                                        <h4 className="text-lg font-semibold text-purple-200 mb-4 flex items-center">
                                          <svg
                                            className="w-5 h-5 mr-2 text-blue-400"
                                            fill="none"
                                            stroke="currentColor"
                                            viewBox="0 0 24 24"
                                          >
                                            <path
                                              strokeLinecap="round"
                                              strokeLinejoin="round"
                                              strokeWidth={2}
                                              d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                                            />
                                          </svg>
                                          Performance Overview
                                        </h4>
                                        <div className="space-y-3">
                                          <div className="bg-purple-900/30 rounded-lg p-3">
                                            <div className="flex justify-between items-center mb-2">
                                              <span className="text-purple-300 text-sm font-medium">
                                                Overall Progress
                                              </span>
                                              <span className="text-purple-200 font-bold">
                                                {student.progress || 0}%
                                              </span>
                                            </div>
                                            <div className="w-full bg-purple-900/50 rounded-full h-3">
                                              <motion.div
                                                className="bg-gradient-to-r from-blue-500 to-purple-500 h-3 rounded-full"
                                                initial={{ width: 0 }}
                                                animate={{ width: `${student.progress || 0}%` }}
                                                transition={{ duration: 0.8, ease: "easeOut" }}
                                              ></motion.div>
                                            </div>
                                          </div>

                                          <div className="grid grid-cols-2 gap-3">
                                            <div className="bg-blue-900/30 rounded-lg p-3 text-center">
                                              <div className="text-2xl font-bold text-blue-200">0</div>
                                              <div className="text-blue-300 text-sm">Assessments</div>
                                            </div>
                                            <div className="bg-green-900/30 rounded-lg p-3 text-center">
                                              <div className="text-2xl font-bold text-green-200">N/A</div>
                                              <div className="text-green-300 text-sm">Avg Score</div>
                                            </div>
                                          </div>
                                        </div>
                                      </div>

                                      {/* Actions */}
                                      <div className="space-y-3">
                                        <h4 className="text-lg font-semibold text-purple-200 mb-4 flex items-center">
                                          <svg
                                            className="w-5 h-5 mr-2 text-green-400"
                                            fill="none"
                                            stroke="currentColor"
                                            viewBox="0 0 24 24"
                                          >
                                            <path
                                              strokeLinecap="round"
                                              strokeLinejoin="round"
                                              strokeWidth={2}
                                              d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                                            />
                                            <path
                                              strokeLinecap="round"
                                              strokeLinejoin="round"
                                              strokeWidth={2}
                                              d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                                            />
                                          </svg>
                                          Quick Actions
                                        </h4>
                                        <div className="space-y-2">
                                          <Button
                                            variant="primary"
                                            size="sm"
                                            onClick={() => handleOpenStudentDetails(student)}
                                            className="w-full bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600"
                                          >
                                            <svg
                                              className="w-4 h-4 mr-2"
                                              fill="none"
                                              stroke="currentColor"
                                              viewBox="0 0 24 24"
                                            >
                                              <path
                                                strokeLinecap="round"
                                                strokeLinejoin="round"
                                                strokeWidth={2}
                                                d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                                              />
                                              <path
                                                strokeLinecap="round"
                                                strokeLinejoin="round"
                                                strokeWidth={2}
                                                d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                                              />
                                            </svg>
                                            View Full Details
                                          </Button>
                                          <Button
                                            variant="outline"
                                            size="sm"
                                            onClick={() => handleOpenBatchChangeModal(student)}
                                            className="w-full border-purple-500/50 text-purple-200 hover:bg-purple-800/30"
                                          >
                                            <svg
                                              className="w-4 h-4 mr-2"
                                              fill="none"
                                              stroke="currentColor"
                                              viewBox="0 0 24 24"
                                            >
                                              <path
                                                strokeLinecap="round"
                                                strokeLinejoin="round"
                                                strokeWidth={2}
                                                d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"
                                              />
                                            </svg>
                                            Change Batch
                                          </Button>
                                          {student.batch && student.batchId && (
                                            <Button
                                              variant="primary"
                                              size="sm"
                                              onClick={() =>
                                                student.batchId &&
                                                handleRemoveStudentFromBatch(student.id, student.batchId, student.name)
                                              }
                                              className="w-full bg-gradient-to-r from-red-500 to-pink-500 hover:from-red-600 hover:to-pink-600"
                                            >
                                              <svg
                                                className="w-4 h-4 mr-2"
                                                fill="none"
                                                stroke="currentColor"
                                                viewBox="0 0 24 24"
                                              >
                                                <path
                                                  strokeLinecap="round"
                                                  strokeLinejoin="round"
                                                  strokeWidth={2}
                                                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                                                />
                                              </svg>
                                              Remove from Batch
                                            </Button>
                                          )}
                                        </div>
                                      </div>
                                    </div>
                                  </div>
                                </motion.div>
                              </td>
                            </tr>
                          )}
                        </React.Fragment>
                      ))}
                    </tbody>
                  </table>

                  {filteredStudents.length === 0 && (
                    <div className="text-center py-8 text-purple-300">No students found matching your criteria.</div>
                  )}
                </div>
              </Card>
            </motion.div>

            {/* Batch Performance and AI Reports Section */}
            <motion.div
              variants={ANIMATION_VARIANTS.slideUp}
              initial="initial"
              animate="animate"
              className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8"
            >
              <motion.div variants={ANIMATION_VARIANTS.slideLeft}>
                <Card className="p-6 h-full">
                  <div className="flex items-center mb-4">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-r from-orange-500 to-red-500 flex items-center justify-center mr-4">
                      <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
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
                    <div className="w-10 h-10 rounded-full bg-gradient-to-r from-pink-500 to-purple-500 flex items-center justify-center mr-4">
                      <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                      </svg>
                    </div>
                    <h3 className="text-xl font-semibold text-purple-200">AI Student Reports</h3>
                  </div>
                  <p className="text-purple-300 mb-6 leading-relaxed">
                    Generate AI-powered student performance reports with personalized insights.
                  </p>
                  <Button variant="primary" className="w-full" onClick={() => setShowAIReports(!showAIReports)}>
                    {showAIReports ? "Hide AI Reports" : "Generate AI Reports"}
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
          </Card>
        </motion.div>
      </div>

      {/* Batch Assignment Modal */}
      {showBatchAssignmentModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="bg-purple-900/95 backdrop-blur-md border border-purple-500/30 rounded-xl p-6 w-full max-w-2xl mx-4"
          >
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-2xl font-bold text-purple-200">Bulk Student Assignment</h3>
              <button
                onClick={handleCloseBatchAssignment}
                className="text-purple-400 hover:text-purple-200 transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="space-y-6">
              <div>
                <label className="block text-purple-300 font-medium mb-2">Select Target Batch</label>
                <select
                  value={targetBatchId}
                  onChange={(e) => setTargetBatchId(e.target.value)}
                  className="w-full px-4 py-3 bg-purple-800/30 border border-purple-500/50 rounded-lg text-purple-200 focus:border-purple-400 focus:outline-none focus:ring-2 focus:ring-purple-500/30"
                >
                  <option value="">Select a batch</option>
                  {batches
                    .filter((batch) => batch.id !== "all")
                    .map((batch) => (
                      <option key={batch.id} value={batch.id}>
                        {batch.name} ({batch.studentCount} students)
                      </option>
                    ))}
                </select>
              </div>

              <div>
                <div className="flex items-center justify-between mb-3">
                  <label className="text-purple-300 font-medium">Select Students</label>
                  <div className="flex space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleSelectAllStudents}
                      className="text-purple-200 border-purple-500/50 hover:bg-purple-800/30"
                    >
                      Select All
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleClearAllStudents}
                      className="text-purple-200 border-purple-500/50 hover:bg-purple-800/30"
                    >
                      Clear All
                    </Button>
                  </div>
                </div>
                
                <Input
                  type="text"
                  value={batchAssignmentSearchTerm}
                  onChange={(e) => setBatchAssignmentSearchTerm(e.target.value)}
                  placeholder="Search students..."
                  className="mb-4"
                />

                <div className="max-h-64 overflow-y-auto space-y-2">
                  {students
                    .filter((student) =>
                      student.name.toLowerCase().includes(batchAssignmentSearchTerm.toLowerCase()) ||
                      student.email.toLowerCase().includes(batchAssignmentSearchTerm.toLowerCase())
                    )
                    .map((student) => (
                      <div
                        key={student.id}
                        className={`p-3 rounded-lg border transition-colors cursor-pointer ${
                          selectedStudentsForBatch.includes(student.id)
                            ? "border-purple-400 bg-purple-800/30"
                            : "border-purple-500/30 hover:border-purple-400/50 hover:bg-purple-900/20"
                        }`}
                        onClick={() => handleStudentSelection(student.id)}
                      >
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-purple-200 font-medium">{student.name}</p>
                            <p className="text-purple-300 text-sm">{student.email}</p>
                          </div>
                          <div className="flex items-center">
                            <input
                              type="checkbox"
                              checked={selectedStudentsForBatch.includes(student.id)}
                              onChange={() => handleStudentSelection(student.id)}
                              className="w-4 h-4 text-purple-500 bg-purple-800 border-purple-500 rounded focus:ring-purple-400"
                            />
                          </div>
                        </div>
                      </div>
                    ))}
                </div>
              </div>

              <div className="flex justify-end space-x-3">
                <Button
                  variant="outline"
                  onClick={handleCloseBatchAssignment}
                  className="border-purple-500/50 text-purple-200 hover:bg-purple-800/30"
                >
                  Cancel
                </Button>
                <Button
                  variant="primary"
                  onClick={handleBulkAssignToBatch}
                  disabled={!targetBatchId || selectedStudentsForBatch.length === 0}
                  className="bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600"
                >
                  Assign {selectedStudentsForBatch.length} Students
                </Button>
              </div>
            </div>
          </motion.div>
        </div>
      )}

      {/* Batch Change Modal */}
      {showBatchChangeModal && selectedStudentForBatchChange && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="bg-purple-900/95 backdrop-blur-md border border-purple-500/30 rounded-xl p-6 w-full max-w-md mx-4"
          >
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-purple-200">Change Student Batch</h3>
              <button
                onClick={handleCloseBatchChangeModal}
                className="text-purple-400 hover:text-purple-200 transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <p className="text-purple-300 mb-2">Student: <span className="text-purple-200 font-medium">{selectedStudentForBatchChange.name}</span></p>
                <p className="text-purple-300 mb-4">Email: <span className="text-purple-200">{selectedStudentForBatchChange.email}</span></p>
              </div>

              <div>
                <label className="block text-purple-300 font-medium mb-2">New Batch</label>
                <select
                  value={newBatchId}
                  onChange={(e) => setNewBatchId(e.target.value)}
                  className="w-full px-4 py-3 bg-purple-800/30 border border-purple-500/50 rounded-lg text-purple-200 focus:border-purple-400 focus:outline-none focus:ring-2 focus:ring-purple-500/30"
                >
                  <option value="">Unassigned</option>
                  {batches
                    .filter((batch) => batch.id !== "all")
                    .map((batch) => (
                      <option key={batch.id} value={batch.id}>
                        {batch.name}
                      </option>
                    ))}
                </select>
              </div>

              <div className="flex justify-end space-x-3">
                <Button
                  variant="outline"
                  onClick={handleCloseBatchChangeModal}
                  className="border-purple-500/50 text-purple-200 hover:bg-purple-800/30"
                >
                  Cancel
                </Button>
                <Button
                  variant="primary"
                  onClick={handleChangeStudentBatch}
                  className="bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600"
                >
                  Change Batch
                </Button>
              </div>
            </div>
          </motion.div>
        </div>
      )}

      {/* Student Details Modal */}
      {showStudentDetailsModal && selectedStudentForDetails && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="bg-purple-900/95 backdrop-blur-md border border-purple-500/30 rounded-xl p-6 w-full max-w-4xl mx-4 max-h-[90vh] overflow-y-auto"
          >
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-2xl font-bold text-purple-200">Student Details</h3>
              <button
                onClick={() => setShowStudentDetailsModal(false)}
                className="text-purple-400 hover:text-purple-200 transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div className="bg-purple-800/30 rounded-lg p-4">
                  <h4 className="text-lg font-semibold text-purple-200 mb-3">Basic Information</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-purple-300">Name:</span>
                      <span className="text-purple-200">{selectedStudentForDetails.name}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-purple-300">Email:</span>
                      <span className="text-purple-200">{selectedStudentForDetails.email}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-purple-300">Current Batch:</span>
                      <span className="text-purple-200">{selectedStudentForDetails.batch || "Unassigned"}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-purple-300">Progress:</span>
                      <span className="text-purple-200">{selectedStudentForDetails.progress || 0}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-purple-300">Last Active:</span>
                      <span className="text-purple-200">
                        {selectedStudentForDetails.lastActive
                          ? new Date(selectedStudentForDetails.lastActive).toLocaleDateString()
                          : "Never"}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <div className="bg-purple-800/30 rounded-lg p-4">
                  <h4 className="text-lg font-semibold text-purple-200 mb-3">Performance Overview</h4>
                  <div className="space-y-3">
                    <div>
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-purple-300">Overall Progress</span>
                        <span className="text-purple-200 font-bold">{selectedStudentForDetails.progress || 0}%</span>
                      </div>
                      <div className="w-full bg-purple-900/50 rounded-full h-3">
                        <div
                          className="bg-gradient-to-r from-blue-500 to-purple-500 h-3 rounded-full"
                          style={{ width: `${selectedStudentForDetails.progress || 0}%` }}
                        ></div>
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                      <div className="bg-blue-900/30 rounded-lg p-3 text-center">
                        <div className="text-2xl font-bold text-blue-200">0</div>
                        <div className="text-blue-300 text-sm">Assessments</div>
                      </div>
                      <div className="bg-green-900/30 rounded-lg p-3 text-center">
                        <div className="text-2xl font-bold text-green-200">N/A</div>
                        <div className="text-green-300 text-sm">Avg Score</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-6 flex justify-end space-x-3">
              <Button
                variant="outline"
                onClick={() => setShowStudentDetailsModal(false)}
                className="border-purple-500/50 text-purple-200 hover:bg-purple-800/30"
              >
                Close
              </Button>
              <Button
                variant="primary"
                onClick={() => {
                  setShowStudentDetailsModal(false)
                  handleOpenBatchChangeModal(selectedStudentForDetails)
                }}
                className="bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600"
              >
                Change Batch
              </Button>
            </div>
          </motion.div>
        </div>
      )}
    </>
  )
}

export default StudentManagement
