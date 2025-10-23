/**
 * AssessmentHistory Component
 * Displays recent assessments and provides navigation to assessment history
 */
import React from "react"
import { motion } from "framer-motion"
import Card from "../../ui/Card"
import Button from "../../ui/Button"
import { ANIMATION_VARIANTS } from "../../../utils/constants"

interface Assessment {
  id: string
  title: string
  topic?: string
  subject?: string
  difficulty: string
  created_at?: string
  total_questions?: number
  total_students?: number
}

interface AssessmentHistoryProps {
  recentAssessments: Assessment[]
}

const AssessmentHistory: React.FC<AssessmentHistoryProps> = ({
  recentAssessments
}) => {
  const handleViewAssessment = (assessmentId: string) => {
    window.location.assign(`/teacher/assessment/${assessmentId}/results`)
  }

  const handleViewHistory = () => {
    window.location.assign('/teacher/assessment-history')
  }


  return (
    <motion.div variants={ANIMATION_VARIANTS.slideUp} className="mb-8">
      <div className="grid grid-cols-1 gap-4">
        {/* Recent Tests */}
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold text-blue-200">Recent Tests</h2>
            <Button 
              variant="secondary" 
              size="sm" 
              onClick={handleViewHistory}
            >
              View All
            </Button>
          </div>
          
          {recentAssessments.length === 0 ? (
            <div className="text-center py-8">
              <div className="text-blue-300 mb-2">No recent tests</div>
              <p className="text-blue-400 text-sm">Create your first assessment to get started</p>
            </div>
          ) : (
            <div className="space-y-3">
              {recentAssessments.slice(0, 5).map((assessment) => (
                <div 
                  key={assessment.id} 
                  className="p-3 bg-blue-900/20 rounded-lg border border-blue-500/30 flex items-center justify-between hover:bg-blue-900/30 transition-colors"
                >
                  <div className="flex-1">
                    <div className="text-blue-200 font-semibold">{assessment.title}</div>
                    <div className="text-blue-300 text-sm">
                      {assessment.topic || assessment.subject} • {assessment.difficulty}
                      {assessment.total_questions && ` • ${assessment.total_questions} questions`}
                      {assessment.total_students && ` • ${assessment.total_students} students`}
                    </div>
                    {assessment.created_at && (
                      <div className="text-blue-400 text-xs">
                        Created {new Date(assessment.created_at).toLocaleDateString()}
                      </div>
                    )}
                  </div>
                  <Button 
                    variant="secondary" 
                    size="sm" 
                    onClick={() => handleViewAssessment(assessment.id)}
                  >
                    View Results
                  </Button>
                </div>
              ))}
            </div>
          )}
        </Card>

      </div>
    </motion.div>
  )
}

export default AssessmentHistory
