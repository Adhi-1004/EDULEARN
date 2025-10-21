/**
 * BatchAssignmentModal Component
 * Handles batch assignment for students
 */
import React, { useState, useEffect } from "react"
import { motion } from "framer-motion"
import Card from "../../ui/Card"
import Button from "../../ui/Button"
import Input from "../../ui/Input"
import { ANIMATION_VARIANTS } from "../../../utils/constants"

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

interface BatchAssignmentModalProps {
  isOpen: boolean
  onClose: () => void
  students: Student[]
  batches: Batch[]
  onAssignStudents: (studentIds: string[], batchId: string) => void
}

const BatchAssignmentModal: React.FC<BatchAssignmentModalProps> = ({
  isOpen,
  onClose,
  students,
  batches,
  onAssignStudents
}) => {
  const [selectedStudents, setSelectedStudents] = useState<string[]>([])
  const [targetBatchId, setTargetBatchId] = useState<string>("")
  const [searchTerm, setSearchTerm] = useState("")

  useEffect(() => {
    if (!isOpen) {
      setSelectedStudents([])
      setTargetBatchId("")
      setSearchTerm("")
    }
  }, [isOpen])

  const filteredStudents = students.filter(student =>
    student.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    student.email.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const handleStudentToggle = (studentId: string) => {
    setSelectedStudents(prev =>
      prev.includes(studentId)
        ? prev.filter(id => id !== studentId)
        : [...prev, studentId]
    )
  }

  const handleSelectAll = () => {
    if (selectedStudents.length === filteredStudents.length) {
      setSelectedStudents([])
    } else {
      setSelectedStudents(filteredStudents.map(student => student.id))
    }
  }

  const handleAssign = () => {
    if (selectedStudents.length > 0 && targetBatchId) {
      onAssignStudents(selectedStudents, targetBatchId)
      onClose()
    }
  }

  if (!isOpen) return null

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
        className="bg-blue-900/95 backdrop-blur-sm border border-blue-500/30 rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <Card className="p-6">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-blue-200">Assign Students to Batch</h2>
            <Button variant="ghost" onClick={onClose} className="text-blue-300 hover:text-blue-200">
              ✕
            </Button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Student Selection */}
            <div>
              <h3 className="text-lg font-semibold text-blue-200 mb-4">Select Students</h3>
              
              {/* Search */}
              <div className="mb-4">
                <Input
                  type="text"
                  placeholder="Search students..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full"
                />
              </div>

              {/* Select All */}
              <div className="mb-4">
                <Button
                  variant="ghost"
                  onClick={handleSelectAll}
                  className="text-blue-300 hover:text-blue-200"
                >
                  {selectedStudents.length === filteredStudents.length ? "Deselect All" : "Select All"}
                </Button>
                <span className="text-blue-300 text-sm ml-2">
                  ({selectedStudents.length} selected)
                </span>
              </div>

              {/* Student List */}
              <div className="max-h-96 overflow-y-auto space-y-2">
                {filteredStudents.map((student) => (
                  <div
                    key={student.id}
                    className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                      selectedStudents.includes(student.id)
                        ? "bg-blue-500/20 border-blue-400/50"
                        : "bg-blue-900/20 border-blue-500/30 hover:border-blue-400/50"
                    }`}
                    onClick={() => handleStudentToggle(student.id)}
                  >
                    <div className="flex items-center space-x-3">
                      <input
                        type="checkbox"
                        checked={selectedStudents.includes(student.id)}
                        onChange={() => handleStudentToggle(student.id)}
                        className="w-4 h-4 text-blue-500 bg-blue-900 border-blue-500 rounded focus:ring-blue-500"
                      />
                      <div className="flex-1">
                        <h4 className="text-blue-200 font-medium">{student.name}</h4>
                        <p className="text-blue-300 text-sm">{student.email}</p>
                        {student.batch && (
                          <span className="inline-block px-2 py-1 bg-blue-500/20 text-blue-300 text-xs rounded-full mt-1">
                            {student.batch}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Batch Selection */}
            <div>
              <h3 className="text-lg font-semibold text-blue-200 mb-4">Select Target Batch</h3>
              
              <div className="space-y-3">
                {batches.map((batch) => (
                  <div
                    key={batch.id}
                    className={`p-4 rounded-lg border cursor-pointer transition-colors ${
                      targetBatchId === batch.id
                        ? "bg-blue-500/20 border-blue-400/50"
                        : "bg-blue-900/20 border-blue-500/30 hover:border-blue-400/50"
                    }`}
                    onClick={() => setTargetBatchId(batch.id)}
                  >
                    <div className="flex items-center space-x-3">
                      <input
                        type="radio"
                        name="targetBatch"
                        checked={targetBatchId === batch.id}
                        onChange={() => setTargetBatchId(batch.id)}
                        className="w-4 h-4 text-blue-500 bg-blue-900 border-blue-500 focus:ring-blue-500"
                      />
                      <div className="flex-1">
                        <h4 className="text-blue-200 font-medium">{batch.name}</h4>
                        <p className="text-blue-300 text-sm">
                          {batch.studentCount} students • Created {new Date(batch.createdAt).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Assignment Summary */}
              {selectedStudents.length > 0 && targetBatchId && (
                <div className="mt-6 p-4 bg-blue-800/20 rounded-lg border border-blue-500/30">
                  <h4 className="text-blue-200 font-medium mb-2">Assignment Summary</h4>
                  <p className="text-blue-300 text-sm">
                    Assigning {selectedStudents.length} student{selectedStudents.length !== 1 ? 's' : ''} to{" "}
                    {batches.find(b => b.id === targetBatchId)?.name}
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Actions */}
          <div className="flex justify-end space-x-3 mt-6 pt-4 border-t border-blue-500/30">
            <Button variant="ghost" onClick={onClose}>
              Cancel
            </Button>
            <Button
              variant="primary"
              onClick={handleAssign}
              disabled={selectedStudents.length === 0 || !targetBatchId}
            >
              Assign Students
            </Button>
          </div>
        </Card>
      </motion.div>
    </motion.div>
  )
}

export default BatchAssignmentModal
