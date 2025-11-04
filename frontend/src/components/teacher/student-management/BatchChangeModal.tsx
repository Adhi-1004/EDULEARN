/**
 * BatchChangeModal Component
 * Allows changing a student's batch assignment
 */
import React, { useState, useEffect } from "react"
import { motion } from "framer-motion"
import Card from "../../ui/Card"
import Button from "../../ui/Button"
import api from "../../../utils/api"
import { useToast } from "../../../contexts/ToastContext"

interface Student {
  id: string
  name: string
  email: string
  batch?: string
  batchId?: string
  batchIds?: string[]
}

interface Batch {
  id: string
  name: string
  studentCount: number
}

interface BatchChangeModalProps {
  student: Student | null
  batches: Batch[]
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
}

const BatchChangeModal: React.FC<BatchChangeModalProps> = ({
  student,
  batches,
  isOpen,
  onClose,
  onSuccess
}) => {
  const { success, error: showError } = useToast()
  const [selectedBatchId, setSelectedBatchId] = useState<string>("")
  const [changing, setChanging] = useState(false)

  useEffect(() => {
    if (isOpen && student) {
      // Set current batch ID if available, otherwise empty
      setSelectedBatchId(student.batchId || "")
    }
  }, [isOpen, student])

  if (!isOpen || !student) return null

  const handleChangeBatch = async () => {
    if (!selectedBatchId) {
      showError("Please select a batch")
      return
    }

    // If student is already in this batch, no need to change
    const currentBatchIds = student.batchIds || (student.batchId ? [student.batchId] : [])
    if (currentBatchIds.includes(selectedBatchId)) {
      showError("Student is already in this batch")
      return
    }

    setChanging(true)
    try {
      // Only remove from batches that the current teacher owns
      // batches prop contains only batches owned by current teacher
      const teacherOwnedBatchIds = batches.map(b => b.id)
      const batchesToRemoveFrom = currentBatchIds.filter(bid => teacherOwnedBatchIds.includes(bid))

      // Remove from batches owned by current teacher (if any)
      if (batchesToRemoveFrom.length > 0) {
        // Remove from the first batch owned by current teacher
        // In multi-batch scenario, we typically remove from one batch when changing
        try {
          await api.post("/api/teacher/students/remove", {
            student_id: student.id,
            batch_id: batchesToRemoveFrom[0]
          })
        } catch (removeError: any) {
          // If removal fails (e.g., student not in batch), continue anyway
          // This handles edge cases where batch assignment might have changed
          console.warn("⚠️ [BATCH CHANGE] Could not remove from old batch:", removeError.response?.data?.detail)
        }
      }

      // Add to new batch
      const response = await api.post("/api/teacher/students/add", {
        email: student.email,
        name: student.name,
        batch_id: selectedBatchId
      })

      if (response.data.success) {
        success("Batch changed successfully", `Student has been moved to the selected batch`)
        onSuccess()
        onClose()
      } else {
        showError("Failed to change batch", response.data.message || "An error occurred")
      }
    } catch (error: any) {
      console.error("❌ [BATCH CHANGE] Error changing batch:", error)
      showError("Failed to change batch", error.response?.data?.detail || "An error occurred")
    } finally {
      setChanging(false)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/50 dark:bg-black/70 flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        className="bg-background border border-border rounded-lg shadow-xl max-w-md w-full"
        onClick={(e) => e.stopPropagation()}
      >
        <Card className="p-6">
          {/* Header */}
          <div className="flex items-center justify-between mb-6 pb-4 border-b border-border">
            <h2 className="text-2xl font-bold text-foreground">Change Batch</h2>
            <Button variant="ghost" onClick={onClose} className="text-muted-foreground hover:text-foreground">
              ✕
            </Button>
          </div>

          {/* Student Info */}
          <div className="mb-6">
            <p className="text-sm text-muted-foreground mb-2">Student:</p>
            <p className="text-lg font-semibold text-foreground">{student.name}</p>
            <p className="text-sm text-muted-foreground">{student.email}</p>
            {student.batch && (
              <p className="text-sm text-muted-foreground mt-2">
                Current Batch: <span className="font-medium text-foreground">{student.batch}</span>
              </p>
            )}
          </div>

          {/* Batch Selection */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-foreground mb-2">
              Select New Batch
            </label>
            <select
              value={selectedBatchId}
              onChange={(e) => setSelectedBatchId(e.target.value)}
              className="w-full px-4 py-2 bg-background border border-border rounded-lg text-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
              disabled={changing}
            >
              <option value="">-- Select a batch --</option>
              {batches.map((batch) => (
                <option key={batch.id} value={batch.id}>
                  {batch.name} ({batch.studentCount} students)
                </option>
              ))}
            </select>
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-4 border-t border-border">
            <Button
              variant="primary"
              onClick={handleChangeBatch}
              disabled={changing || !selectedBatchId}
              className="flex-1"
            >
              {changing ? "Changing..." : "Change Batch"}
            </Button>
            <Button
              variant="ghost"
              onClick={onClose}
              disabled={changing}
              className="flex-1"
            >
              Cancel
            </Button>
          </div>
        </Card>
      </motion.div>
    </motion.div>
  )
}

export default BatchChangeModal

