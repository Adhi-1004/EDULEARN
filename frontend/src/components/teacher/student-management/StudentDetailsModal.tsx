/**
 * StudentDetailsModal Component
 * Displays detailed information about a student
 */
import React from "react"
import { motion } from "framer-motion"
import Card from "../../ui/Card"
import Button from "../../ui/Button"
import { ANIMATION_VARIANTS } from "../../../utils/constants"

interface Student {
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
}

interface StudentDetailsModalProps {
  student: Student | null
  isOpen: boolean
  onClose: () => void
  onEditStudent: (student: Student) => void
  onChangeBatch: (student: Student) => void
  onRemoveStudent: (studentId: string) => void
}

const StudentDetailsModal: React.FC<StudentDetailsModalProps> = ({
  student,
  isOpen,
  onClose,
  onEditStudent,
  onChangeBatch,
  onRemoveStudent
}) => {
  if (!isOpen || !student) return null

  const getBadgeIcon = (badge: string) => {
    const badgeIcons: { [key: string]: string } = {
      "first_assessment": "🎯",
      "high_scorer": "⭐",
      "consistent_learner": "🔥",
      "level_up": "📈",
      "perfect_score": "💯",
      "streak_master": "⚡"
    }
    return badgeIcons[badge] || "🏆"
  }

  const getBadgeName = (badge: string) => {
    const badgeNames: { [key: string]: string } = {
      "first_assessment": "First Assessment",
      "high_scorer": "High Scorer",
      "consistent_learner": "Consistent Learner",
      "level_up": "Level Up",
      "perfect_score": "Perfect Score",
      "streak_master": "Streak Master"
    }
    return badgeNames[badge] || badge.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase())
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        className="bg-blue-900/95 backdrop-blur-sm border border-blue-500/30 rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <Card className="p-6">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-blue-200">Student Details</h2>
            <Button variant="ghost" onClick={onClose} className="text-blue-300 hover:text-blue-200">
              ✕
            </Button>
          </div>

          {/* Student Information */}
          <div className="space-y-6">
            {/* Basic Info */}
            <div className="bg-blue-800/20 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-blue-200 mb-3">Basic Information</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-blue-300 text-sm">Name</label>
                  <p className="text-blue-200 font-medium">{student.name}</p>
                </div>
                <div>
                  <label className="text-blue-300 text-sm">Email</label>
                  <p className="text-blue-200 font-medium">{student.email}</p>
                </div>
                <div>
                  <label className="text-blue-300 text-sm">Batch</label>
                  <p className="text-blue-200 font-medium">{student.batch || "Unassigned"}</p>
                </div>
                <div>
                  <label className="text-blue-300 text-sm">Last Active</label>
                  <p className="text-blue-200 font-medium">
                    {new Date(student.lastActive).toLocaleDateString()}
                  </p>
                </div>
              </div>
            </div>

            {/* Progress & Stats */}
            <div className="bg-blue-800/20 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-blue-200 mb-3">Progress & Statistics</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-blue-300 text-sm">Overall Progress</label>
                  <div className="flex items-center space-x-2 mt-1">
                    <div className="flex-1 bg-blue-900/50 rounded-full h-2">
                      <div
                        className="bg-gradient-to-r from-blue-500 to-blue-400 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${student.progress}%` }}
                      />
                    </div>
                    <span className="text-blue-200 font-medium">{student.progress}%</span>
                  </div>
                </div>
                <div>
                  <label className="text-blue-300 text-sm">Level</label>
                  <p className="text-blue-200 font-medium">{student.level || 1}</p>
                </div>
                <div>
                  <label className="text-blue-300 text-sm">XP Points</label>
                  <p className="text-blue-200 font-medium">{student.xp || 0}</p>
                </div>
                <div>
                  <label className="text-blue-300 text-sm">Completed Assessments</label>
                  <p className="text-blue-200 font-medium">{student.completedAssessments || 0}</p>
                </div>
                <div>
                  <label className="text-blue-300 text-sm">Average Score</label>
                  <p className="text-blue-200 font-medium">{student.averageScore || 0}%</p>
                </div>
              </div>
            </div>

            {/* Badges */}
            {student.badges && student.badges.length > 0 && (
              <div className="bg-blue-800/20 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-blue-200 mb-3">Achievements</h3>
                <div className="flex flex-wrap gap-2">
                  {student.badges.map((badge, index) => (
                    <div
                      key={index}
                      className="flex items-center space-x-2 bg-blue-500/20 border border-blue-500/30 rounded-lg px-3 py-2"
                    >
                      <span className="text-lg">{getBadgeIcon(badge)}</span>
                      <span className="text-blue-200 text-sm">{getBadgeName(badge)}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Actions */}
            <div className="flex flex-wrap gap-3 pt-4 border-t border-blue-500/30">
              <Button
                variant="primary"
                onClick={() => onEditStudent(student)}
                className="flex-1"
              >
                Edit Student
              </Button>
              <Button
                variant="secondary"
                onClick={() => onChangeBatch(student)}
                className="flex-1"
              >
                Change Batch
              </Button>
              <Button
                variant="danger"
                onClick={() => onRemoveStudent(student.id)}
                className="flex-1"
              >
                Remove Student
              </Button>
            </div>
          </div>
        </Card>
      </motion.div>
    </motion.div>
  )
}

export default StudentDetailsModal
