"use client"

import React, { useEffect, useMemo, useState } from "react"
import { useNavigate, useParams } from "react-router-dom"
import { motion } from "framer-motion"
import Card from "../components/ui/Card"
import Button from "../components/ui/Button"
import LoadingState from "../components/LoadingState"
import ErrorState from "../components/ErrorState"
import api from "../utils/api"
import { ANIMATION_VARIANTS } from "../utils/constants"

interface AssessmentInfo {
  id: string
  title: string
  subject: string
  difficulty: string
  description?: string
  time_limit?: number
  question_count?: number
}

interface AssessmentStudentResult {
  student_id: string
  student_name: string
  student_email: string
  score: number
  percentage: number
  time_taken: number
  submitted_at: string
  total_questions: number
}

interface TeacherStudentResultItem {
  result_id: string
  assessment_id: string
  assessment_title: string
  percentage: number
  score: number
  total_questions: number
  time_taken: number
  submitted_at: string
}

const TeacherAssessmentResults: React.FC = () => {
  const { assessmentId } = useParams<{ assessmentId: string }>()
  const navigate = useNavigate()

  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [assessment, setAssessment] = useState<AssessmentInfo | null>(null)
  const [results, setResults] = useState<AssessmentStudentResult[]>([])
  const [assigned, setAssigned] = useState<any[]>([])
  const [search, setSearch] = useState("")

  useEffect(() => {
    const fetchData = async () => {
      if (!assessmentId) return
      try {
        setLoading(true)
        setError(null)

        // Try to fetch assessment details (teacher route first, then fallback)
        let aData: any = null
        try {
          const aRes = await api.get(`/api/assessments/teacher/${assessmentId}`)
          aData = aRes.data
        } catch (e) {
          try {
            const aRes = await api.get(`/api/assessments/${assessmentId}/details`)
            aData = aRes.data
          } catch (_) {
            aData = null
          }
        }
        if (aData) {
          setAssessment({
            id: aData.id || assessmentId,
            title: aData.title,
            subject: aData.subject || aData.topic,
            difficulty: aData.difficulty,
            description: aData.description,
            time_limit: aData.time_limit,
            question_count: aData.question_count || (aData.questions ? aData.questions.length : undefined)
          })
        }

        // Fetch combined results for this assessment
        const rRes = await api.get(`/api/assessments/teacher/${assessmentId}/results`)
        setResults(rRes.data || [])

        // Fetch assigned students with attendance
        try {
          const aRes = await api.get(`/api/assessments/teacher/${assessmentId}/assigned-students`)
          setAssigned(aRes.data || [])
        } catch (e) {
          // endpoint may not exist yet; degrade gracefully
          setAssigned([])
        }
      } catch (err: any) {
        console.error("Failed to load assessment results:", err)
        setError(err?.response?.data?.detail || "Failed to load assessment results")
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [assessmentId])

  const filteredResults = useMemo(() => {
    const term = search.trim().toLowerCase()
    if (!term) return results
    return results.filter(r =>
      r.student_name?.toLowerCase().includes(term) ||
      r.student_email?.toLowerCase().includes(term)
    )
  }, [results, search])

  const mergedAssigned = useMemo(() => {
    if (!assigned?.length) return []
    const term = search.trim().toLowerCase()
    const rows = assigned.map((s: any) => ({
      ...s,
      present: !!s.submitted,
    }))
    return term
      ? rows.filter((r: any) => (r.student_name||"").toLowerCase().includes(term) || (r.student_email||"").toLowerCase().includes(term))
      : rows
  }, [assigned, search])

  const viewStudentDetailedResult = async (studentId: string) => {
    try {
      console.log("📊 [VIEW RESULT] Fetching results for student:", studentId, "assessment:", assessmentId)
      
      // Fetch this student's results and find the one matching this assessment to get result_id
      const res = await api.get(`/api/assessments/teacher/student-results/${studentId}`)
      console.log("📊 [VIEW RESULT] API Response:", res.data)
      
      const items: TeacherStudentResultItem[] = res?.data?.results || res?.data?.student_results || []
      console.log("📊 [VIEW RESULT] Total results found:", items.length)
      
      if (items.length > 0) {
        console.log("📊 [VIEW RESULT] Sample result:", items[0])
        console.log("📊 [VIEW RESULT] Looking for assessment_id:", assessmentId)
        items.forEach((item, idx) => {
          console.log(`📊 [VIEW RESULT] Result ${idx}: assessment_id="${item.assessment_id}", result_id="${item.result_id}"`)
        })
      }
      
      const match = items.find(it => {
        const idMatch = it.assessment_id === assessmentId || (it as any).assessmentId === assessmentId
        console.log(`📊 [VIEW RESULT] Comparing: "${it.assessment_id}" === "${assessmentId}" = ${idMatch}`)
        return idMatch
      })
      
      console.log("📊 [VIEW RESULT] Match found:", match)
      
      if (match && match.result_id) {
        console.log("📊 [VIEW RESULT] Navigating to result:", match.result_id)
        navigate(`/teacher/test-result/${match.result_id}`)
        return
      }
      
      // Fallback: try to fetch detailed result by probing possible collections? Not available from here, show error
      console.error("❌ [VIEW RESULT] Could not locate matching result")
      setError("Could not locate detailed result for this student.")
    } catch (err: any) {
      console.error("❌ [VIEW RESULT] Failed to resolve student's result:", err)
      setError("Failed to open student's detailed result")
    }
  }

  const formatTime = (seconds: number) => {
    const m = Math.floor((seconds || 0) / 60)
    const s = (seconds || 0) % 60
    return `${m}m ${s}s`
  }

  if (loading) {
    return (
      <div className="min-h-screen pt-20 px-4 flex items-center justify-center">
        <LoadingState size="lg" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen pt-20 px-4 flex items-center justify-center">
        <Card className="p-8 text-center">
          <ErrorState
            title="Unable to load results"
            message={error}
            onBack={() => navigate("/teacher/assessment-management")}
            backText="Back"
            showCard={true}
          />
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen pt-16 px-4">
      <motion.div
        variants={ANIMATION_VARIANTS.fadeIn}
        initial="initial"
        animate="animate"
        className="max-w-7xl mx-auto"
      >
        <Card className="p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-blue-200">Assessment Results</h1>
              <p className="text-blue-300">
                {assessment ? (
                  <>
                    {assessment.title} • {assessment.subject} • {assessment.difficulty}
                  </>
                ) : (
                  <>Assessment ID: {assessmentId}</>
                )}
              </p>
            </div>
            <Button variant="secondary" onClick={() => navigate("/teacher/assessment-management")}>Back</Button>
          </div>

          <div className="flex items-center gap-2">
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search students by name or email..."
              className="w-full px-3 py-2 bg-black/20 backdrop-blur-md border border-blue-500/30 rounded-lg text-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-400"
            />
          </div>
        </Card>

        <Card className="p-6">
          <h2 className="text-xl font-semibold text-blue-200 mb-4">Assigned Students</h2>
          {mergedAssigned.length === 0 ? (
            <div className="text-blue-300">No assigned students found.</div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {mergedAssigned.map((s: any, idx: number) => (
                <motion.div
                  key={`${s.student_id}-${idx}`}
                  variants={ANIMATION_VARIANTS.slideUp}
                  initial="initial"
                  animate="animate"
                  transition={{ delay: idx * 0.03 }}
                  className="bg-gradient-to-br from-blue-900/20 to-blue-800/20 rounded-lg border border-blue-500/30 p-4"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <div className="text-blue-200 font-semibold">{s.student_name || "Unknown"}</div>
                      <div className="text-blue-300 text-sm">{s.student_email || ""}</div>
                    </div>
                    <span className={`text-xs px-2 py-1 rounded border ${s.present ? "bg-green-600/20 border-green-500/30 text-green-300" : "bg-red-600/20 border-red-500/30 text-red-300"}`}>
                      {s.present ? "Present" : "Absent"}
                    </span>
                  </div>
                  {s.present && (
                    <div className="text-blue-400 text-xs mb-3">
                      <span>Score: {s.score}/{s.total_questions} ({(s.percentage||0).toFixed(1)}%)</span>
                      <span className="mx-2">•</span>
                      <span>Time: {formatTime(s.time_taken||0)}</span>
                    </div>
                  )}
                  <div className="flex items-center justify-between">
                    <div className="text-blue-400 text-xs">
                      {s.submitted_at ? new Date(s.submitted_at).toLocaleString() : ""}
                    </div>
                    {s.present ? (
                      <Button variant="secondary" size="sm" onClick={() => s.result_id ? navigate(`/teacher/test-result/${s.result_id}`) : viewStudentDetailedResult(s.student_id)}>
                        View Details
                      </Button>
                    ) : (
                      <div className="text-blue-500 text-xs">Not submitted</div>
                    )}
                  </div>
                </motion.div>
              ))}
            </div>
          )}

          <h2 className="text-xl font-semibold text-blue-200 mt-8 mb-4">Submissions</h2>
          {filteredResults.length === 0 ? (
            <div className="text-blue-300">No submissions yet.</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-blue-500/30">
                    <th className="text-left py-3 px-4 text-blue-300 font-medium">Student</th>
                    <th className="text-left py-3 px-4 text-blue-300 font-medium">Email</th>
                    <th className="text-left py-3 px-4 text-blue-300 font-medium">Score</th>
                    <th className="text-left py-3 px-4 text-blue-300 font-medium">Time Taken</th>
                    <th className="text-left py-3 px-4 text-blue-300 font-medium">Submitted</th>
                    <th className="text-left py-3 px-4 text-blue-300 font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredResults.map((r, idx) => (
                    <motion.tr
                      key={`${r.student_id}-${idx}`}
                      variants={ANIMATION_VARIANTS.slideUp}
                      initial="initial"
                      animate="animate"
                      transition={{ delay: idx * 0.03 }}
                      className="border-b border-blue-500/20"
                    >
                      <td className="py-3 px-4 text-blue-200">{r.student_name || "Unknown"}</td>
                      <td className="py-3 px-4 text-blue-300">{r.student_email || ""}</td>
                      <td className="py-3 px-4">
                        <span className={`${(r.percentage||0) >= 80 ? "text-green-400" : (r.percentage||0) >= 60 ? "text-yellow-400" : "text-red-400"} font-semibold`}>
                          {r.score}/{r.total_questions} ({(r.percentage || 0).toFixed(1)}%)
                        </span>
                      </td>
                      <td className="py-3 px-4 text-blue-300">{formatTime(r.time_taken)}</td>
                      <td className="py-3 px-4 text-blue-300">{new Date(r.submitted_at).toLocaleString()}</td>
                      <td className="py-3 px-4">
                        <Button variant="secondary" size="sm" onClick={() => viewStudentDetailedResult(r.student_id)}>
                          View Details
                        </Button>
                      </td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      </motion.div>
    </div>
  )
}

export default TeacherAssessmentResults


