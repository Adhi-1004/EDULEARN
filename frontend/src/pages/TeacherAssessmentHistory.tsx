"use client"

import React, { useEffect, useMemo, useState } from "react"
import { useNavigate } from "react-router-dom"
import { motion } from "framer-motion"
import Card from "../components/ui/Card"
import Button from "../components/ui/Button"
import LoadingState from "../components/LoadingState"
import ErrorState from "../components/ErrorState"
import api from "../utils/api"
import { ANIMATION_VARIANTS } from "../utils/constants"

interface AssessmentItem {
  id: string
  title: string
  topic?: string
  subject?: string
  difficulty: string
  description?: string
  time_limit?: number
  question_count?: number
  created_at?: string
  status?: string
  type?: string
}

const TeacherAssessmentHistory: React.FC = () => {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [assessments, setAssessments] = useState<AssessmentItem[]>([])
  const [search, setSearch] = useState("")
  const [difficulty, setDifficulty] = useState("all")
  const [status, setStatus] = useState("all")

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        setError(null)
        // Use teacher assessments endpoint - fetches only from teacher_assessments collection
        const res = await api.get("/api/teacher/assessments")
        const list: AssessmentItem[] = Array.isArray(res.data) ? res.data : []
        setAssessments(list)
      } catch (err: any) {
        console.error("Failed to load assessments:", err)
        setError(err?.response?.data?.detail || "Failed to load assessments")
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase()
    return assessments.filter(a => {
      const matchesSearch = !q || a.title.toLowerCase().includes(q) || (a.topic || a.subject || "").toLowerCase().includes(q)
      const matchesDiff = difficulty === "all" || a.difficulty === difficulty
      const matchesStatus = status === "all" || (a.status || "").toLowerCase() === status
      return matchesSearch && matchesDiff && matchesStatus
    }).sort((a, b) => {
      const ad = a.created_at ? new Date(a.created_at).getTime() : 0
      const bd = b.created_at ? new Date(b.created_at).getTime() : 0
      return bd - ad
    })
  }, [assessments, search, difficulty, status])

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
            title="Unable to load history" 
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
              <h1 className="text-3xl font-bold text-blue-200">Assessment History</h1>
              <p className="text-blue-300">All assessments you have posted</p>
            </div>
            <Button variant="secondary" onClick={() => navigate("/teacher/assessment-management")}>Back</Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by title or subject..."
              className="w-full px-3 py-2 bg-black/20 backdrop-blur-md border border-blue-500/30 rounded-lg text-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-400"
            />
            <select
              value={difficulty}
              onChange={(e) => setDifficulty(e.target.value)}
              className="w-full px-3 py-2 bg-black/20 backdrop-blur-md border border-blue-500/30 rounded-lg text-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-400"
            >
              <option value="all">All Difficulties</option>
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
            </select>
            <select
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              className="w-full px-3 py-2 bg-black/20 backdrop-blur-md border border-blue-500/30 rounded-lg text-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-400"
            >
              <option value="all">All Status</option>
              <option value="active">active</option>
              <option value="draft">draft</option>
              <option value="archived">archived</option>
            </select>
          </div>
        </Card>

        <Card className="p-6">
          {filtered.length === 0 ? (
            <div className="text-center py-10 text-blue-300">No assessments found.</div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filtered.map((a, idx) => (
                <motion.div
                  key={a.id}
                  variants={ANIMATION_VARIANTS.slideUp}
                  initial="initial"
                  animate="animate"
                  transition={{ delay: idx * 0.03 }}
                  className="bg-gradient-to-br from-blue-900/20 to-blue-800/20 rounded-lg border border-blue-500/30 p-4"
                >
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="text-lg font-semibold text-blue-200">{a.title}</h3>
                    <span className="text-xs px-2 py-1 rounded bg-blue-600/20 border border-blue-500/30 text-blue-200 capitalize">{a.difficulty}</span>
                  </div>
                  <p className="text-blue-300 text-sm mb-3">{a.topic || a.subject}</p>
                  <div className="text-blue-400 text-xs mb-4">
                    <span>Questions: {a.question_count ?? "-"}</span>
                    <span className="mx-2">•</span>
                    <span>Time: {a.time_limit ?? "-"} min</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <Button variant="secondary" size="sm" onClick={() => navigate(`/teacher/assessment/${a.id}/results`)}>
                      View Results
                    </Button>
                    <span className="text-blue-400 text-xs">{a.created_at ? new Date(a.created_at).toLocaleString() : ""}</span>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </Card>
      </motion.div>
    </div>
  )
}

export default TeacherAssessmentHistory


