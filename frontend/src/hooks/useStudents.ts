/**
 * useStudents Hook
 * Custom hook for managing student-related operations
 */
import { useState, useEffect, useCallback } from "react"
import { useToast } from "../contexts/ToastContext"
import api from "../utils/api"

interface Student {
  id: string
  name: string
  email: string
  progress: number
  lastActive: string
  batch?: string
  batchId?: string
  performance?: {
    totalAssessments: number
    averageScore: number
    strengths: string[]
    weaknesses: string[]
  }
}

interface StudentCreateData {
  name: string
  email: string
  batchId?: string
}

interface UseStudentsReturn {
  students: Student[]
  loading: boolean
  error: string | null
  createStudent: (data: StudentCreateData) => Promise<Student | null>
  updateStudent: (id: string, data: Partial<StudentCreateData>) => Promise<boolean>
  deleteStudent: (id: string) => Promise<boolean>
  getStudentDetails: (id: string) => Promise<Student | null>
  getStudentPerformance: (id: string) => Promise<any>
  bulkCreateStudents: (students: StudentCreateData[]) => Promise<boolean>
  refreshStudents: () => Promise<void>
}

export const useStudents = (): UseStudentsReturn => {
  const { success, error: showError } = useToast()
  const [students, setStudents] = useState<Student[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchStudents = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await api.get("/api/teacher/students")
      if (response.data.success) {
        setStudents(response.data.students)
      } else {
        console.warn("No students data received")
        setStudents([])
      }
    } catch (err) {
      console.error("Failed to fetch students:", err)
      setError("Failed to fetch students")
      setStudents([])
    } finally {
      setLoading(false)
    }
  }, [])

  const createStudent = useCallback(async (data: StudentCreateData): Promise<Student | null> => {
    try {
      setLoading(true)
      setError(null)

      const response = await api.post("/api/teacher/students/add", {
        name: data.name,
        email: data.email,
        batch_id: data.batchId
      })
      if (response.data.success) {
        const newStudent: Student = {
          id: response.data.student_id,
          name: data.name,
          email: data.email,
          progress: 0,
          lastActive: new Date().toISOString(),
          batchId: data.batchId
        }
        setStudents(prev => [newStudent, ...prev])
        success("Student created successfully!")
        return newStudent
      }
      return null
    } catch (err) {
      console.error("Failed to create student:", err)
      setError("Failed to create student")
      showError("Failed to create student")
      return null
    } finally {
      setLoading(false)
    }
  }, [success, showError])

  const updateStudent = useCallback(async (id: string, data: Partial<StudentCreateData>): Promise<boolean> => {
    try {
      setLoading(true)
      setError(null)

      const response = await api.put(`/api/teacher/students/${id}`, data)
      if (response.data) {
        setStudents(prev => 
          prev.map(student => 
            student.id === id ? { ...student, ...data } : student
          )
        )
        success("Student updated successfully!")
        return true
      }
      return false
    } catch (err) {
      console.error("Failed to update student:", err)
      setError("Failed to update student")
      showError("Failed to update student")
      return false
    } finally {
      setLoading(false)
    }
  }, [success, showError])

  const deleteStudent = useCallback(async (id: string): Promise<boolean> => {
    try {
      setLoading(true)
      setError(null)

      const response = await api.delete(`/api/teacher/students/${id}`)
      if (response.status === 200) {
        setStudents(prev => prev.filter(student => student.id !== id))
        success("Student deleted successfully!")
        return true
      }
      return false
    } catch (err) {
      console.error("Failed to delete student:", err)
      setError("Failed to delete student")
      showError("Failed to delete student")
      return false
    } finally {
      setLoading(false)
    }
  }, [success, showError])

  const getStudentDetails = useCallback(async (id: string): Promise<Student | null> => {
    try {
      setLoading(true)
      setError(null)

      const response = await api.get(`/api/teacher/students/${id}`)
      if (response.data) {
        return response.data
      }
      return null
    } catch (err) {
      console.error("Failed to get student details:", err)
      setError("Failed to get student details")
      return null
    } finally {
      setLoading(false)
    }
  }, [])

  const getStudentPerformance = useCallback(async (id: string): Promise<any> => {
    try {
      setLoading(true)
      setError(null)

      const response = await api.get(`/api/teacher/students/${id}/performance`)
      if (response.data) {
        return response.data
      }
      return null
    } catch (err) {
      console.error("Failed to get student performance:", err)
      setError("Failed to get student performance")
      return null
    } finally {
      setLoading(false)
    }
  }, [])

  const bulkCreateStudents = useCallback(async (studentsData: StudentCreateData[]): Promise<boolean> => {
    try {
      setLoading(true)
      setError(null)

      const response = await api.post("/api/teacher/students/bulk", {
        students: studentsData
      })
      if (response.data.success) {
        // Refresh the students list
        await fetchStudents()
        success(`${studentsData.length} students created successfully!`)
        return true
      }
      return false
    } catch (err) {
      console.error("Failed to bulk create students:", err)
      setError("Failed to bulk create students")
      showError("Failed to bulk create students")
      return false
    } finally {
      setLoading(false)
    }
  }, [success, showError, fetchStudents])

  const refreshStudents = useCallback(async () => {
    await fetchStudents()
  }, [fetchStudents])

  // Initial data fetch
  useEffect(() => {
    fetchStudents()
  }, [fetchStudents])

  return {
    students,
    loading,
    error,
    createStudent,
    updateStudent,
    deleteStudent,
    getStudentDetails,
    getStudentPerformance,
    bulkCreateStudents,
    refreshStudents
  }
}
