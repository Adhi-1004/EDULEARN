"use client"

import type React from "react"
import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { useNavigate } from "react-router-dom"
import { useToast } from "../contexts/ToastContext"
import { useAuth } from "../hooks/useAuth"
import Card from "../components/ui/Card"
import Button from "../components/ui/Button"
import AnimatedBackground from "../components/AnimatedBackground"
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

const TeacherDashboard: React.FC = () => {
  const { user } = useAuth()
  const { error: showError } = useToast()
  const navigate = useNavigate()
  
  const [students, setStudents] = useState<Student[]>([])
  const [batches, setBatches] = useState<Batch[]>([])
  const [loading, setLoading] = useState(true)
  // Notifications moved to Navbar

  // Fetch dashboard data when the component mounts
  useEffect(() => {
    fetchDashboardData()
    // notifications handled globally in Navbar
    return () => {}
  }, [])

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

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      console.log("📊 [TEACHER] Fetching dashboard data...")
      
      // Fetch students from API
      const studentsResponse = await api.get("/api/teacher/students")
      if (studentsResponse.data.success) {
        setStudents(studentsResponse.data.students)
        console.log("✅ [TEACHER] Students loaded:", studentsResponse.data.students.length)
      } else {
        setStudents([])
      }
      
      // Fetch batches from API
      const batchesResponse = await api.get("/api/teacher/batches")
      if (batchesResponse.data && Array.isArray(batchesResponse.data)) {
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
        console.log("✅ [TEACHER] Batches loaded:", formattedBatches.length)
      } else {
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
      console.error("❌ [TEACHER] Failed to fetch dashboard data:", err)
      showError("Error", "Failed to load dashboard data")
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

  // Navigation functions
  const handleNavigateToStudentManagement = () => {
    navigate('/teacher/student-management')
  }

  const handleNavigateToAssessmentManagement = () => {
    navigate('/teacher/assessment-management')
  }

  // results navigation moved into Assessment Management and History

  if (loading) {
    return (
      <>
        <AnimatedBackground />
        <div className="min-h-screen pt-20 px-4 flex items-center justify-center relative z-10">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-foreground mb-4">Loading Teacher Dashboard...</h1>
            <p className="text-muted-foreground">Please wait while we load your data.</p>
          </div>
        </div>
      </>
    )
  }

  return (
    <>
      <AnimatedBackground />
      <div className="min-h-screen pt-16 px-4 relative z-10">
        <motion.div
          variants={ANIMATION_VARIANTS.fadeIn}
          initial="initial"
          animate="animate"
          className="max-w-6xl mx-auto"
        >
          <Card className="p-6 mb-6">
            <motion.div variants={ANIMATION_VARIANTS.slideDown} className="text-center mb-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex-1">
                  <h1 className="text-3xl font-bold text-foreground mb-2">Teacher Dashboard</h1>
                  <p className="text-muted-foreground text-base">
                    Welcome back, {user?.name || user?.email || "Teacher"}!
                  </p>
                </div>
                {/* Notifications are handled in Navbar */}
              </div>
            </motion.div>

            {/* Quick Stats */}
            <motion.div
              variants={ANIMATION_VARIANTS.slideUp}
              initial="initial"
              animate="animate"
              className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6"
            >
              <div className="bg-gradient-to-r from-blue-500/10 to-blue-600/10 dark:from-blue-500/20 dark:to-blue-600/20 border border-blue-500/30 rounded-lg p-3">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-muted-foreground text-xs font-medium">Total Students</p>
                    <p className="text-xl font-bold text-foreground">{students.length}</p>
                  </div>
                  <div className="w-6 h-6 bg-blue-500/20 rounded-full flex items-center justify-center">
                    <svg className="w-3 h-3 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
                      </svg>
                    </div>
                  </div>
              </div>

              <div className="bg-gradient-to-r from-purple-500/10 to-purple-600/10 dark:from-purple-500/20 dark:to-purple-600/20 border border-purple-500/30 rounded-lg p-3">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-muted-foreground text-xs font-medium">Active Batches</p>
                    <p className="text-xl font-bold text-foreground">{batches.filter((b) => b.id !== "all").length}</p>
                  </div>
                  <div className="w-6 h-6 bg-purple-500/20 rounded-full flex items-center justify-center">
                    <svg className="w-3 h-3 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                      </svg>
                    </div>
                  </div>
              </div>

              <div className="bg-gradient-to-r from-green-500/10 to-green-600/10 dark:from-green-500/20 dark:to-green-600/20 border border-green-500/30 rounded-lg p-3">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-muted-foreground text-xs font-medium">Assessments</p>
                    <p className="text-xl font-bold text-foreground">12</p>
                  </div>
                  <div className="w-6 h-6 bg-green-500/20 rounded-full flex items-center justify-center">
                    <svg className="w-3 h-3 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    </div>
                  </div>
              </div>

              <div className="bg-gradient-to-r from-orange-500/10 to-orange-600/10 dark:from-orange-500/20 dark:to-orange-600/20 border border-orange-500/30 rounded-lg p-3">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-muted-foreground text-xs font-medium">Avg. Progress</p>
                    <p className="text-xl font-bold text-foreground">
                      {students.length > 0
                        ? Math.round(students.reduce((acc, student) => acc + student.progress, 0) / students.length)
                        : 0}
                      %
                    </p>
                  </div>
                  <div className="w-6 h-6 bg-orange-500/20 rounded-full flex items-center justify-center">
                    <svg className="w-3 h-3 text-orange-600 dark:text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                      </svg>
                  </div>
                </div>
              </div>
            </motion.div>

            {/* Main Management Sections - Only two cards */}
            <motion.div
              variants={ANIMATION_VARIANTS.slideUp}
              initial="initial"
              animate="animate"
              className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6"
            >
              {/* Student Management */}
              <motion.div variants={ANIMATION_VARIANTS.slideLeft}>
                <Card className="p-5 h-full">
                  <div className="flex items-center mb-3">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-r from-blue-500 to-blue-600 flex items-center justify-center mr-3">
                      <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
                      </svg>
                    </div>
                    <h3 className="text-lg font-semibold text-foreground">Student Management</h3>
                  </div>
                  <p className="text-muted-foreground mb-4 text-sm leading-relaxed">
                    View and manage all your students, track their progress, and provide feedback.
                  </p>
                  <Button variant="primary" size="sm" className="w-full" onClick={handleNavigateToStudentManagement}>
                    Manage Students
                  </Button>
                </Card>
              </motion.div>

              {/* Assessment Management */}
              <motion.div variants={ANIMATION_VARIANTS.slideUp}>
                <Card className="p-5 h-full">
                  <div className="flex items-center mb-3">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-r from-green-500 to-teal-500 flex items-center justify-center mr-3">
                      <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    </div>
                    <h3 className="text-lg font-semibold text-foreground">Assessment Management</h3>
                  </div>
                  <p className="text-muted-foreground mb-4 text-sm leading-relaxed">
                    Create custom assessments and coding challenges for your students.
                  </p>
                  <Button variant="primary" size="sm" className="w-full" onClick={handleNavigateToAssessmentManagement}>
                    Manage Assessments
                  </Button>
                </Card>
              </motion.div>

              {/* Results card removed per requirements */}
            </motion.div>

          </Card>
        </motion.div>
      </div>

      {/* Notifications overlay removed; handled in Navbar */}
    </>
  )
}

export default TeacherDashboard