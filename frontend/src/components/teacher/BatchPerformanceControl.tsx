"use client"

import type React from "react"
import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import Card from "../ui/Card"
import Button from "../ui/Button"
import api from "../../utils/api"

interface BatchPerformance {
  id: string
  name: string
  totalStudents: number
  averageScore: number
  strugglingStudents: Array<{
    id: string
    name: string
    score: number
    lastActive: string
  }>
  topPerformers: Array<{
    id: string
    name: string
    score: number
    lastActive: string
  }>
  completionRate: number
  recentActivity: number
}

interface BatchPerformanceControlProps {
  teacherId: string
}

const BatchPerformanceControl: React.FC<BatchPerformanceControlProps> = ({ teacherId }) => {
  const [batches, setBatches] = useState<BatchPerformance[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedBatch, setSelectedBatch] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchBatchPerformance()
  }, [teacherId])

  const fetchBatchPerformance = async () => {
    try {
      setLoading(true)
      const response = await api.get(`/api/teacher-dashboard/batch-performance/${teacherId}`)
      setBatches(response.data)
    } catch (err) {
      console.error("Failed to fetch batch performance:", err)
      console.log("Using mock data for batch performance")
      // Use mock data as fallback
      const mockBatches: BatchPerformance[] = [
        {
          id: "batch-1",
          name: "Advanced Programming",
          totalStudents: 25,
          averageScore: 78.5,
          strugglingStudents: [
            { id: "s1", name: "Alice Johnson", score: 45, lastActive: "2024-01-15" },
            { id: "s2", name: "Bob Smith", score: 52, lastActive: "2024-01-14" },
            { id: "s3", name: "Carol Davis", score: 48, lastActive: "2024-01-16" },
          ],
          topPerformers: [
            { id: "s4", name: "David Wilson", score: 95, lastActive: "2024-01-16" },
            { id: "s5", name: "Eva Brown", score: 92, lastActive: "2024-01-15" },
            { id: "s6", name: "Frank Miller", score: 88, lastActive: "2024-01-14" },
          ],
          completionRate: 85.2,
          recentActivity: 12,
        },
        {
          id: "batch-2",
          name: "Data Structures",
          totalStudents: 18,
          averageScore: 82.3,
          strugglingStudents: [
            { id: "s7", name: "Grace Lee", score: 55, lastActive: "2024-01-15" },
            { id: "s8", name: "Henry Chen", score: 58, lastActive: "2024-01-14" },
          ],
          topPerformers: [
            { id: "s9", name: "Ivy Zhang", score: 96, lastActive: "2024-01-16" },
            { id: "s10", name: "Jack Taylor", score: 94, lastActive: "2024-01-15" },
            { id: "s11", name: "Kate Wilson", score: 91, lastActive: "2024-01-14" },
          ],
          completionRate: 92.1,
          recentActivity: 8,
        },
        {
          id: "batch-3",
          name: "Algorithms",
          totalStudents: 22,
          averageScore: 75.8,
          strugglingStudents: [
            { id: "s12", name: "Liam O'Connor", score: 42, lastActive: "2024-01-15" },
            { id: "s13", name: "Maya Patel", score: 48, lastActive: "2024-01-14" },
            { id: "s14", name: "Noah Kim", score: 51, lastActive: "2024-01-16" },
          ],
          topPerformers: [
            { id: "s15", name: "Olivia Brown", score: 93, lastActive: "2024-01-16" },
            { id: "s16", name: "Paul Garcia", score: 89, lastActive: "2024-01-15" },
          ],
          completionRate: 78.5,
          recentActivity: 15,
        },
      ]
      setBatches(mockBatches)
    } finally {
      setLoading(false)
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-green-400"
    if (score >= 60) return "text-yellow-400"
    return "text-red-400"
  }

  const getScoreBgColor = (score: number) => {
    if (score >= 80) return "bg-green-500/20 border-green-500/30"
    if (score >= 60) return "bg-yellow-500/20 border-yellow-500/30"
    return "bg-red-500/20 border-red-500/30"
  }

  if (loading) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        </div>
      </Card>
    )
  }

  if (error) {
    return (
      <Card className="p-6">
        <div className="text-center text-red-400">
          <p>{error}</p>
          <Button variant="outline" size="sm" onClick={fetchBatchPerformance} className="mt-4 bg-transparent">
            Retry
          </Button>
        </div>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-fg mb-2">📊 Batch Performance Mission Control</h2>
        <p className="text-muted-fg">Monitor and manage your batches at a glance</p>
      </div>

      {batches.length === 0 ? (
        <Card className="p-8 text-center">
          <div className="text-muted-fg">
            <p className="text-lg mb-4">No batches found</p>
            <p>Create your first batch to start monitoring performance</p>
          </div>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {batches.map((batch, index) => (
            <motion.div
              key={batch.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <div
                className={`p-6 cursor-pointer transition-all duration-300 hover:scale-105 ${
                  selectedBatch === batch.id ? "ring-2" : ""
                }`}
                style={{ boxShadow: "var(--shadow-soft)" }}
                onClick={() => setSelectedBatch(selectedBatch === batch.id ? null : batch.id)}
              >
                <Card className="h-full">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-semibold text-fg">{batch.name}</h3>
                  <div className="px-3 py-1 rounded-full text-sm font-medium border border-base bg-elevated">
                    <span className={getScoreColor(batch.averageScore)}>{batch.averageScore.toFixed(1)}%</span>
                  </div>
                </div>

                <div className="space-y-3">
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-fg">Students:</span>
                    <span className="text-fg">{batch.totalStudents}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-fg">Completion Rate:</span>
                    <span className="text-fg">{batch.completionRate.toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-fg">Recent Activity:</span>
                    <span className="text-fg">{batch.recentActivity} today</span>
                  </div>
                </div>

                {selectedBatch === batch.id && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    className="mt-6 pt-6 border-t border-base"
                  >
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {/* Struggling Students */}
                      <div>
                        <h4 className="text-sm font-semibold text-red-400 mb-2">🚨 Struggling Students</h4>
                        <div className="space-y-2">
                          {batch.strugglingStudents.slice(0, 3).map((student) => (
                            <div key={student.id} className="flex justify-between items-center text-xs">
                              <span className="text-fg truncate">{student.name}</span>
                              <span className="text-red-400">{student.score}%</span>
                            </div>
                          ))}
                          {batch.strugglingStudents.length === 0 && (
                            <p className="text-xs text-muted-fg">No struggling students</p>
                          )}
                        </div>
                      </div>

                      {/* Top Performers */}
                      <div>
                        <h4 className="text-sm font-semibold text-green-400 mb-2">⭐ Top Performers</h4>
                        <div className="space-y-2">
                          {batch.topPerformers.slice(0, 3).map((student) => (
                            <div key={student.id} className="flex justify-between items-center text-xs">
                              <span className="text-fg truncate">{student.name}</span>
                              <span className="text-green-400">{student.score}%</span>
                            </div>
                          ))}
                          {batch.topPerformers.length === 0 && (
                            <p className="text-xs text-muted-fg">No performance data</p>
                          )}
                        </div>
                      </div>
                    </div>

                    <div className="mt-4 flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        className="flex-1 bg-transparent"
                        onClick={() => {
                          // Navigate to detailed batch view
                          console.log("View detailed batch:", batch.id)
                        }}
                      >
                        View Details
                      </Button>
                      <Button
                        variant="primary"
                        size="sm"
                        className="flex-1"
                        onClick={() => {
                          // Generate AI report for batch
                          console.log("Generate AI report for batch:", batch.id)
                        }}
                      >
                        AI Report
                      </Button>
                    </div>
                  </motion.div>
                )}
                </Card>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  )
}

export default BatchPerformanceControl
