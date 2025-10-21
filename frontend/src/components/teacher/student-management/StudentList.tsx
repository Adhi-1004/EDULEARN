/**
 * StudentList Component
 * Displays a list of students with search and filtering capabilities
 */
import React from "react"
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

interface StudentListProps {
  students: Student[]
  searchTerm: string
  onSearchChange: (term: string) => void
  selectedBatch: string
  onBatchChange: (batchId: string) => void
  batches: Array<{ id: string; name: string; studentCount: number }>
  onStudentClick: (student: Student) => void
  onAddStudent: (batchId: string) => void
  onRemoveStudent: (studentId: string, batchId: string) => void
  onBulkUpload: (batchId: string, batchName: string) => void
}

const StudentList: React.FC<StudentListProps> = ({
  students,
  searchTerm,
  onSearchChange,
  selectedBatch,
  onBatchChange,
  batches,
  onStudentClick,
  onAddStudent,
  onBulkUpload
}) => {
  // Filter students based on search term and selected batch
  const filteredStudents = students.filter(student => {
    const matchesSearch = student.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         student.email.toLowerCase().includes(searchTerm.toLowerCase())
    
    const matchesBatch = selectedBatch === "all" || student.batchId === selectedBatch
    
    return matchesSearch && matchesBatch
  })

  return (
    <motion.div variants={ANIMATION_VARIANTS.slideUp}>
      <Card className="p-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6">
          <h2 className="text-2xl font-bold text-blue-200 mb-4 md:mb-0">Students</h2>
          
          <div className="flex space-x-3">
            <Button 
              variant="primary" 
              onClick={() => onAddStudent(selectedBatch)}
              className="text-sm"
            >
              Add Student
            </Button>
            {selectedBatch !== "all" && (
              <Button 
                variant="secondary" 
                onClick={() => {
                  const batch = batches.find(b => b.id === selectedBatch)
                  if (batch) {
                    onBulkUpload(selectedBatch, batch.name)
                  }
                }}
                className="text-sm"
              >
                Bulk Upload
              </Button>
            )}
          </div>
        </div>

        {/* Search and Filter Controls */}
        <div className="mb-6 p-4 bg-blue-900/20 rounded-lg border border-blue-500/30">
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="flex-1">
              <Input
                type="text"
                placeholder="Search students by name or email..."
                value={searchTerm}
                onChange={(e) => onSearchChange(e.target.value)}
                className="w-full"
              />
            </div>
            
            <div className="flex space-x-2">
              <select
                value={selectedBatch}
                onChange={(e) => onBatchChange(e.target.value)}
                className="px-3 py-2 bg-blue-900/50 border border-blue-500/30 rounded-lg text-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Students</option>
                {batches.map(batch => (
                  <option key={batch.id} value={batch.id}>
                    {batch.name} ({batch.studentCount})
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Students Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredStudents.map((student) => (
            <motion.div
              key={student.id}
              variants={ANIMATION_VARIANTS.fadeIn}
              whileHover={{ scale: 1.02 }}
              className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-4 cursor-pointer hover:border-blue-400/50 transition-colors"
              onClick={() => onStudentClick(student)}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-blue-200 mb-1">
                    {student.name}
                  </h3>
                  <p className="text-blue-300 text-sm mb-2">{student.email}</p>
                  {student.batch && (
                    <span className="inline-block px-2 py-1 bg-blue-500/20 text-blue-300 text-xs rounded-full">
                      {student.batch}
                    </span>
                  )}
                </div>
                
                <div className="text-right">
                  <div className="text-sm text-blue-300 mb-1">
                    Progress: {student.progress}%
                  </div>
                  <div className="text-xs text-blue-400">
                    Last active: {new Date(student.lastActive).toLocaleDateString()}
                  </div>
                </div>
              </div>
              
              {/* Progress Bar */}
              <div className="w-full bg-blue-900/50 rounded-full h-2 mb-3">
                <div
                  className="bg-gradient-to-r from-blue-500 to-blue-400 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${student.progress}%` }}
                />
              </div>
              
              <div className="flex justify-between items-center">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation()
                    onStudentClick(student)
                  }}
                  className="text-blue-300 hover:text-blue-200"
                >
                  View Details
                </Button>
                
                <div className="flex space-x-1">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation()
                      // Handle edit action
                    }}
                    className="text-blue-300 hover:text-blue-200"
                  >
                    Edit
                  </Button>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Empty State */}
        {filteredStudents.length === 0 && (
          <div className="text-center py-12">
            <div className="text-blue-300 text-lg mb-2">
              {searchTerm || selectedBatch !== "all" 
                ? "No students found matching your criteria" 
                : "No students found"
              }
            </div>
            <p className="text-blue-400 text-sm">
              {searchTerm || selectedBatch !== "all"
                ? "Try adjusting your search or filter criteria"
                : "Add students to get started"
              }
            </p>
          </div>
        )}
      </Card>
    </motion.div>
  )
}

export default StudentList
