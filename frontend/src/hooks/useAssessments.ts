/**
 * useAssessments Hook
 * Custom hook for managing assessment-related operations
 */
import { useState, useEffect, useCallback } from "react"
import { useToast } from "../contexts/ToastContext"
import api from "../utils/api"

interface Assessment {
  id: string
  title: string
  topic?: string
  subject?: string
  difficulty: string
  created_at?: string
  total_questions?: number
  total_students?: number
  type?: string
  is_active?: boolean
}

interface AssessmentCreateData {
  title: string
  topic: string
  difficulty: string
  question_count?: number
  batches: string[]
  type?: string
  description?: string
}

interface UseAssessmentsReturn {
  assessments: Assessment[]
  recentAssessments: Assessment[]
  loading: boolean
  error: string | null
  createAssessment: (data: AssessmentCreateData) => Promise<Assessment | null>
  updateAssessment: (id: string, data: Partial<AssessmentCreateData>) => Promise<boolean>
  deleteAssessment: (id: string) => Promise<boolean>
  publishAssessment: (id: string) => Promise<boolean>
  assignToBatches: (id: string, batchIds: string[]) => Promise<boolean>
  refreshAssessments: () => Promise<void>
  refreshRecent: () => Promise<void>
}

export const useAssessments = (): UseAssessmentsReturn => {
  const { success, error: showError } = useToast()
  const [assessments, setAssessments] = useState<Assessment[]>([])
  const [recentAssessments, setRecentAssessments] = useState<Assessment[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchAssessments = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await api.get("/api/assessments/")
      if (Array.isArray(response.data)) {
        setAssessments(response.data)
      }
    } catch (err) {
      console.error("Failed to fetch assessments:", err)
      setError("Failed to fetch assessments")
    } finally {
      setLoading(false)
    }
  }, [])

  const fetchRecentAssessments = useCallback(async () => {
    try {
      const response = await api.get("/api/assessments/")
      if (Array.isArray(response.data)) {
        const recent = [...response.data]
          .sort((a: any, b: any) => 
            new Date(b.created_at || b.createdAt || 0).getTime() - 
            new Date(a.created_at || a.createdAt || 0).getTime()
          )
          .slice(0, 4)
        setRecentAssessments(recent)
      }
    } catch (err) {
      console.warn("Failed to fetch recent assessments:", err)
    }
  }, [])


  const createAssessment = useCallback(async (data: AssessmentCreateData): Promise<Assessment | null> => {
    try {
      setLoading(true)
      setError(null)

      let response
      if (data.type === "ai_generated") {
        response = await api.post("/api/teacher/assessments/create", data)
      } else {
        response = await api.post("/api/assessments/", data)
      }

      if (response.data) {
        const newAssessment = response.data.assessment || response.data
        setAssessments(prev => [newAssessment, ...prev])
        success("Assessment created successfully!")
        return newAssessment
      }
      return null
    } catch (err) {
      console.error("Failed to create assessment:", err)
      setError("Failed to create assessment")
      showError("Failed to create assessment")
      return null
    } finally {
      setLoading(false)
    }
  }, [success, showError])

  const updateAssessment = useCallback(async (id: string, data: Partial<AssessmentCreateData>): Promise<boolean> => {
    try {
      setLoading(true)
      setError(null)

      const response = await api.put(`/api/assessments/${id}`, data)
      if (response.data) {
        setAssessments(prev => 
          prev.map(assessment => 
            assessment.id === id ? { ...assessment, ...data } : assessment
          )
        )
        success("Assessment updated successfully!")
        return true
      }
      return false
    } catch (err) {
      console.error("Failed to update assessment:", err)
      setError("Failed to update assessment")
      showError("Failed to update assessment")
      return false
    } finally {
      setLoading(false)
    }
  }, [success, showError])

  const deleteAssessment = useCallback(async (id: string): Promise<boolean> => {
    try {
      setLoading(true)
      setError(null)

      const response = await api.delete(`/api/assessments/${id}`)
      if (response.status === 200) {
        setAssessments(prev => prev.filter(assessment => assessment.id !== id))
        success("Assessment deleted successfully!")
        return true
      }
      return false
    } catch (err) {
      console.error("Failed to delete assessment:", err)
      setError("Failed to delete assessment")
      showError("Failed to delete assessment")
      return false
    } finally {
      setLoading(false)
    }
  }, [success, showError])

  const publishAssessment = useCallback(async (id: string): Promise<boolean> => {
    try {
      setLoading(true)
      setError(null)

      const response = await api.post(`/api/assessments/${id}/publish`)
      if (response.data) {
        setAssessments(prev => 
          prev.map(assessment => 
            assessment.id === id ? { ...assessment, is_active: true } : assessment
          )
        )
        success("Assessment published successfully!")
        return true
      }
      return false
    } catch (err) {
      console.error("Failed to publish assessment:", err)
      setError("Failed to publish assessment")
      showError("Failed to publish assessment")
      return false
    } finally {
      setLoading(false)
    }
  }, [success, showError])

  const assignToBatches = useCallback(async (id: string, batchIds: string[]): Promise<boolean> => {
    try {
      setLoading(true)
      setError(null)

      const response = await api.post(`/api/assessments/${id}/assign`, { batch_ids: batchIds })
      if (response.data) {
        success("Assessment assigned to batches successfully!")
        return true
      }
      return false
    } catch (err) {
      console.error("Failed to assign assessment to batches:", err)
      setError("Failed to assign assessment to batches")
      showError("Failed to assign assessment to batches")
      return false
    } finally {
      setLoading(false)
    }
  }, [success, showError])

  const refreshAssessments = useCallback(async () => {
    await fetchAssessments()
  }, [fetchAssessments])

  const refreshRecent = useCallback(async () => {
    await fetchRecentAssessments()
  }, [fetchRecentAssessments])


  // Initial data fetch
  useEffect(() => {
    fetchAssessments()
    fetchRecentAssessments()
  }, [fetchAssessments, fetchRecentAssessments])

  return {
    assessments,
    recentAssessments,
    loading,
    error,
    createAssessment,
    updateAssessment,
    deleteAssessment,
    publishAssessment,
    assignToBatches,
    refreshAssessments,
    refreshRecent
  }
}
