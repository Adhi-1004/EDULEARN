/**
 * StudentStats Component
 * Displays statistics and analytics for students
 */
import React from "react"
import { motion } from "framer-motion"
import Card from "../../ui/Card"
import Button from "../../ui/Button"
import { ANIMATION_VARIANTS } from "../../../utils/constants"

interface StudentStatsProps {
  students: Array<{
    id: string
    name: string
    email: string
    progress: number
    lastActive: string
    batch?: string
    batchId?: string
    level?: number
    xp?: number
    badges?: string[]
    completedAssessments?: number
    averageScore?: number
  }>
  batches: Array<{
    id: string
    name: string
    studentCount: number
    createdAt: string
  }>
  onShowBatchPerformance: () => void
  onShowAIReports: () => void
}

const StudentStats: React.FC<StudentStatsProps> = ({
  students,
  batches,
  onShowBatchPerformance,
  onShowAIReports
}) => {
  // Calculate statistics
  const totalStudents = students.length
  const totalBatches = batches.length
  const averageProgress = totalStudents > 0 
    ? Math.round(students.reduce((sum, student) => sum + student.progress, 0) / totalStudents)
    : 0
  
  const highPerformers = students.filter(student => student.progress >= 80).length
  const activeStudents = students.filter(student => {
    const lastActive = new Date(student.lastActive)
    const weekAgo = new Date()
    weekAgo.setDate(weekAgo.getDate() - 7)
    return lastActive > weekAgo
  }).length

  const totalXP = students.reduce((sum, student) => sum + (student.xp || 0), 0)
  const totalAssessments = students.reduce((sum, student) => sum + (student.completedAssessments || 0), 0)
  const averageScore = totalAssessments > 0
    ? Math.round(students.reduce((sum, student) => sum + (student.averageScore || 0), 0) / totalStudents)
    : 0

  return (
    <motion.div variants={ANIMATION_VARIANTS.slideUp}>
      <Card className="p-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6">
          <h2 className="text-2xl font-bold text-blue-200 mb-4 md:mb-0">Student Analytics</h2>
          
          <div className="flex space-x-3">
            <Button variant="secondary" onClick={onShowBatchPerformance}>
              Batch Performance
            </Button>
            <Button variant="secondary" onClick={onShowAIReports}>
              AI Reports
            </Button>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div className="bg-gradient-to-r from-blue-500/20 to-blue-600/20 border border-blue-500/30 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-300 text-sm">Total Students</p>
                <p className="text-2xl font-bold text-blue-200">{totalStudents}</p>
              </div>
              <div className="w-8 h-8 bg-blue-500/30 rounded-full flex items-center justify-center">
                <span className="text-blue-200 text-sm">👥</span>
              </div>
            </div>
          </div>

          <div className="bg-gradient-to-r from-green-500/20 to-green-600/20 border border-green-500/30 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-300 text-sm">High Performers</p>
                <p className="text-2xl font-bold text-green-200">{highPerformers}</p>
              </div>
              <div className="w-8 h-8 bg-green-500/30 rounded-full flex items-center justify-center">
                <span className="text-green-200 text-sm">⭐</span>
              </div>
            </div>
          </div>

          <div className="bg-gradient-to-r from-purple-500/20 to-purple-600/20 border border-purple-500/30 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-300 text-sm">Active (7 days)</p>
                <p className="text-2xl font-bold text-purple-200">{activeStudents}</p>
              </div>
              <div className="w-8 h-8 bg-purple-500/30 rounded-full flex items-center justify-center">
                <span className="text-purple-200 text-sm">🔥</span>
              </div>
            </div>
          </div>

          <div className="bg-gradient-to-r from-orange-500/20 to-orange-600/20 border border-orange-500/30 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-orange-300 text-sm">Avg. Progress</p>
                <p className="text-2xl font-bold text-orange-200">{averageProgress}%</p>
              </div>
              <div className="w-8 h-8 bg-orange-500/30 rounded-full flex items-center justify-center">
                <span className="text-orange-200 text-sm">📊</span>
              </div>
            </div>
          </div>
        </div>

        {/* Detailed Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Performance Overview */}
          <div className="bg-blue-800/20 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-blue-200 mb-3">Performance Overview</h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-blue-300">Average Score</span>
                <span className="text-blue-200 font-medium">{averageScore}%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-blue-300">Total Assessments</span>
                <span className="text-blue-200 font-medium">{totalAssessments}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-blue-300">Total XP Earned</span>
                <span className="text-blue-200 font-medium">{totalXP.toLocaleString()}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-blue-300">Avg. Assessments/Student</span>
                <span className="text-blue-200 font-medium">
                  {totalStudents > 0 ? Math.round(totalAssessments / totalStudents) : 0}
                </span>
              </div>
            </div>
          </div>

          {/* Batch Distribution */}
          <div className="bg-blue-800/20 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-blue-200 mb-3">Batch Distribution</h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-blue-300">Total Batches</span>
                <span className="text-blue-200 font-medium">{totalBatches}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-blue-300">Avg. Students/Batch</span>
                <span className="text-blue-200 font-medium">
                  {totalBatches > 0 ? Math.round(totalStudents / totalBatches) : 0}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-blue-300">Largest Batch</span>
                <span className="text-blue-200 font-medium">
                  {batches.length > 0 ? Math.max(...batches.map(b => b.studentCount)) : 0}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-blue-300">Unassigned Students</span>
                <span className="text-blue-200 font-medium">
                  {students.filter(s => !s.batchId).length}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Progress Distribution */}
        <div className="mt-6 bg-blue-800/20 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-blue-200 mb-3">Progress Distribution</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-red-200">
                {students.filter(s => s.progress < 25).length}
              </div>
              <div className="text-red-300 text-sm">0-25%</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-yellow-200">
                {students.filter(s => s.progress >= 25 && s.progress < 50).length}
              </div>
              <div className="text-yellow-300 text-sm">25-50%</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-200">
                {students.filter(s => s.progress >= 50 && s.progress < 75).length}
              </div>
              <div className="text-blue-300 text-sm">50-75%</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-200">
                {students.filter(s => s.progress >= 75).length}
              </div>
              <div className="text-green-300 text-sm">75-100%</div>
            </div>
          </div>
        </div>
      </Card>
    </motion.div>
  )
}

export default StudentStats
