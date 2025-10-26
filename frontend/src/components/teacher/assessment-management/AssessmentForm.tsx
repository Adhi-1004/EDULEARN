/**
 * AssessmentForm Component
 * Handles assessment creation forms and configuration
 */
import React from "react"
import { motion } from "framer-motion"
import Card from "../../ui/Card"
import Button from "../../ui/Button"
import Input from "../../ui/Input"
import { ANIMATION_VARIANTS } from "../../../utils/constants"

interface Batch {
  id: string
  name: string
  studentCount: number
  createdAt: string
}

interface AssessmentFormProps {
  batches: Batch[]
  onCreateMCQ: () => void
  onCreateAICoding: () => void
  onAIGenerate: () => void
}

const AssessmentForm: React.FC<AssessmentFormProps> = ({
  batches,
  onCreateMCQ,
  onCreateAICoding,
  onAIGenerate
}) => {
  return (
    <motion.div variants={ANIMATION_VARIANTS.slideUp}>
      <Card className="p-6">
        <h2 className="text-2xl font-bold text-blue-200 mb-4">Create Assessment</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {/* AI Generated Assessment */}
          <div className="p-4 bg-gradient-to-br from-blue-900/20 to-blue-800/20 rounded-lg border border-blue-500/30">
            <div className="text-center">
              <div className="text-3xl mb-2">🤖</div>
              <h3 className="text-blue-200 font-semibold mb-2">AI Generated</h3>
              <p className="text-blue-300 text-sm mb-3">Generate questions automatically using AI</p>
              <Button 
                variant="primary" 
                size="sm" 
                className="w-full bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600" 
                onClick={onAIGenerate}
              >
                Generate Assessment
              </Button>
            </div>
          </div>

          {/* Manual MCQ */}
          <div className="p-4 bg-gradient-to-br from-blue-900/20 to-blue-800/20 rounded-lg border border-blue-500/30">
            <div className="text-center">
              <div className="text-3xl mb-2">📝</div>
              <h3 className="text-blue-200 font-semibold mb-2">Manual MCQ</h3>
              <p className="text-blue-300 text-sm mb-3">Create multiple choice questions manually</p>
              <Button 
                variant="primary" 
                size="sm" 
                className="w-full bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600" 
                onClick={onCreateMCQ}
              >
                Create MCQ
              </Button>
            </div>
          </div>

          {/* AI Coding Assessment */}
          <div className="p-4 bg-gradient-to-br from-blue-900/20 to-blue-800/20 rounded-lg border border-blue-500/30">
            <div className="text-center">
              <div className="text-3xl mb-2">💻</div>
              <h3 className="text-blue-200 font-semibold mb-2">AI Coding</h3>
              <p className="text-blue-300 text-sm mb-3">Generate coding problems automatically using AI</p>
              <Button 
                variant="primary" 
                size="sm" 
                className="w-full bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600" 
                onClick={onCreateAICoding}
              >
                Create AI Coding
              </Button>
            </div>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="mt-6 p-4 bg-blue-800/20 rounded-lg border border-blue-500/30">
          <h3 className="text-blue-200 font-semibold mb-2">Available Batches</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-200">{batches.length}</div>
              <div className="text-blue-300 text-sm">Total Batches</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-200">
                {batches.reduce((sum, batch) => sum + (batch.studentCount || 0), 0)}
              </div>
              <div className="text-blue-300 text-sm">Total Students</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-200">
                {batches.length > 0 
                  ? Math.round(batches.reduce((sum, batch) => sum + (batch.studentCount || 0), 0) / batches.length)
                  : 0
                }
              </div>
              <div className="text-blue-300 text-sm">Avg. Students/Batch</div>
            </div>
          </div>
        </div>
      </Card>
    </motion.div>
  )
}

export default AssessmentForm
