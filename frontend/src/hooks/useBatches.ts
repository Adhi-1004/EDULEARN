/**
 * useBatches Hook
 * Custom hook for managing batch-related operations
 */
import { useState, useEffect, useCallback } from "react"
import { useToast } from "../contexts/ToastContext"
import api from "../utils/api"

interface Batch {
  id: string
  name: string
  studentCount: number
  createdAt: string
  students?: any[]
  weaknesses?: string[]
}

interface BatchCreateData {
  name: string
  description?: string
}

interface UseBatchesReturn {
  batches: Batch[]
  loading: boolean
  error: string | null
  createBatch: (data: BatchCreateData) => Promise<Batch | null>
  updateBatch: (id: string, data: Partial<BatchCreateData>) => Promise<boolean>
  deleteBatch: (id: string) => Promise<boolean>
  addStudentToBatch: (batchId: string, studentEmail: string, studentName: string) => Promise<boolean>
  removeStudentFromBatch: (batchId: string, studentId: string) => Promise<boolean>
  assignStudentsToBatch: (batchId: string, studentIds: string[]) => Promise<boolean>
  changeStudentBatch: (studentId: string, oldBatchId: string, newBatchId: string) => Promise<boolean>
  refreshBatches: () => Promise<void>
}

export const useBatches = (): UseBatchesReturn => {
  const { success, error: showError } = useToast()
  const [batches, setBatches] = useState<Batch[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchBatches = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await api.get("/api/teacher/batches")
      if (response.data && Array.isArray(response.data)) {
        const formattedBatches = response.data.map((batch: any) => ({
          id: batch.batch_id,
          name: batch.batch_name,
          studentCount: batch.total_students,
          createdAt: new Date().toISOString().split("T")[0],
          students: batch.students,
          weaknesses: batch.weaknesses
        }))
        setBatches(formattedBatches)
      } else {
        setBatches([])
      }
    } catch (err) {
      console.error("Failed to fetch batches:", err)
      setError("Failed to fetch batches")
      setBatches([])
    } finally {
      setLoading(false)
    }
  }, [])

  const createBatch = useCallback(async (data: BatchCreateData): Promise<Batch | null> => {
    try {
      setLoading(true)
      setError(null)

      const response = await api.post("/api/teacher/batches", data)
      if (response.data.success) {
        const newBatch: Batch = {
          id: response.data.batch_id,
          name: data.name,
          studentCount: 0,
          createdAt: new Date().toISOString().split("T")[0]
        }
        setBatches(prev => [newBatch, ...prev])
        success("Batch created successfully!")
        return newBatch
      }
      return null
    } catch (err) {
      console.error("Failed to create batch:", err)
      setError("Failed to create batch")
      showError("Failed to create batch")
      return null
    } finally {
      setLoading(false)
    }
  }, [success, showError])

  const updateBatch = useCallback(async (id: string, data: Partial<BatchCreateData>): Promise<boolean> => {
    try {
      setLoading(true)
      setError(null)

      const response = await api.put(`/api/teacher/batches/${id}`, data)
      if (response.data) {
        setBatches(prev => 
          prev.map(batch => 
            batch.id === id ? { ...batch, ...data } : batch
          )
        )
        success("Batch updated successfully!")
        return true
      }
      return false
    } catch (err) {
      console.error("Failed to update batch:", err)
      setError("Failed to update batch")
      showError("Failed to update batch")
      return false
    } finally {
      setLoading(false)
    }
  }, [success, showError])

  const deleteBatch = useCallback(async (id: string): Promise<boolean> => {
    try {
      setLoading(true)
      setError(null)

      const response = await api.delete(`/api/teacher/batches/${id}`)
      if (response.status === 200) {
        setBatches(prev => prev.filter(batch => batch.id !== id))
        success("Batch deleted successfully!")
        return true
      }
      return false
    } catch (err) {
      console.error("Failed to delete batch:", err)
      setError("Failed to delete batch")
      showError("Failed to delete batch")
      return false
    } finally {
      setLoading(false)
    }
  }, [success, showError])

  const addStudentToBatch = useCallback(async (batchId: string, studentEmail: string, studentName: string): Promise<boolean> => {
    try {
      setLoading(true)
      setError(null)

      const response = await api.post("/api/teacher/students/add", {
        batch_id: batchId,
        student_email: studentEmail,
        student_name: studentName
      })
      if (response.data.success) {
        // Update the batch's student count
        setBatches(prev => 
          prev.map(batch => 
            batch.id === batchId 
              ? { ...batch, studentCount: batch.studentCount + 1 }
              : batch
          )
        )
        success("Student added to batch successfully!")
        return true
      }
      return false
    } catch (err) {
      console.error("Failed to add student to batch:", err)
      setError("Failed to add student to batch")
      showError("Failed to add student to batch")
      return false
    } finally {
      setLoading(false)
    }
  }, [success, showError])

  const removeStudentFromBatch = useCallback(async (batchId: string, studentId: string): Promise<boolean> => {
    try {
      setLoading(true)
      setError(null)

      const response = await api.post("/api/teacher/students/remove", {
        batch_id: batchId,
        student_id: studentId
      })
      if (response.data.success) {
        // Update the batch's student count
        setBatches(prev => 
          prev.map(batch => 
            batch.id === batchId 
              ? { ...batch, studentCount: Math.max(0, batch.studentCount - 1) }
              : batch
          )
        )
        success("Student removed from batch successfully!")
        return true
      }
      return false
    } catch (err) {
      console.error("Failed to remove student from batch:", err)
      setError("Failed to remove student from batch")
      showError("Failed to remove student from batch")
      return false
    } finally {
      setLoading(false)
    }
  }, [success, showError])

  const assignStudentsToBatch = useCallback(async (batchId: string, studentIds: string[]): Promise<boolean> => {
    try {
      setLoading(true)
      setError(null)

      const response = await api.post("/api/teacher/batches/assign-students", {
        batch_id: batchId,
        student_ids: studentIds
      })
      if (response.data.success) {
        // Update the batch's student count
        setBatches(prev => 
          prev.map(batch => 
            batch.id === batchId 
              ? { ...batch, studentCount: batch.studentCount + studentIds.length }
              : batch
          )
        )
        success("Students assigned to batch successfully!")
        return true
      }
      return false
    } catch (err) {
      console.error("Failed to assign students to batch:", err)
      setError("Failed to assign students to batch")
      showError("Failed to assign students to batch")
      return false
    } finally {
      setLoading(false)
    }
  }, [success, showError])

  const changeStudentBatch = useCallback(async (studentId: string, oldBatchId: string, newBatchId: string): Promise<boolean> => {
    try {
      setLoading(true)
      setError(null)

      const response = await api.post("/api/teacher/students/change-batch", {
        student_id: studentId,
        old_batch_id: oldBatchId,
        new_batch_id: newBatchId
      })
      if (response.data.success) {
        // Update both batches' student counts
        setBatches(prev => 
          prev.map(batch => {
            if (batch.id === oldBatchId) {
              return { ...batch, studentCount: Math.max(0, batch.studentCount - 1) }
            } else if (batch.id === newBatchId) {
              return { ...batch, studentCount: batch.studentCount + 1 }
            }
            return batch
          })
        )
        success("Student's batch changed successfully!")
        return true
      }
      return false
    } catch (err) {
      console.error("Failed to change student's batch:", err)
      setError("Failed to change student's batch")
      showError("Failed to change student's batch")
      return false
    } finally {
      setLoading(false)
    }
  }, [success, showError])

  const refreshBatches = useCallback(async () => {
    await fetchBatches()
  }, [fetchBatches])

  // Initial data fetch
  useEffect(() => {
    fetchBatches()
  }, [fetchBatches])

  return {
    batches,
    loading,
    error,
    createBatch,
    updateBatch,
    deleteBatch,
    addStudentToBatch,
    removeStudentFromBatch,
    assignStudentsToBatch,
    changeStudentBatch,
    refreshBatches
  }
}
