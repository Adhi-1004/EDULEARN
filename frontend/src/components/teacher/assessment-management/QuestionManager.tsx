/**
 * QuestionManager Component
 * Handles question creation and management for assessments
 */
import React, { useState } from "react"
import { motion } from "framer-motion"
import Card from "../../ui/Card"
import Button from "../../ui/Button"
import Input from "../../ui/Input"
import { ANIMATION_VARIANTS } from "../../../utils/constants"

interface Question {
  id?: string
  question: string
  options: string[]
  correct_answer: number
  explanation: string
  points?: number
}

interface QuestionManagerProps {
  questions: Question[]
  onQuestionsChange: (questions: Question[]) => void
  onSaveAssessment: () => void
  onCancel: () => void
  isOpen: boolean
  assessmentTitle: string
  assessmentTopic: string
  assessmentDifficulty: string
}

const QuestionManager: React.FC<QuestionManagerProps> = ({
  questions,
  onQuestionsChange,
  onSaveAssessment,
  onCancel,
  isOpen,
  assessmentTitle,
  assessmentTopic,
  assessmentDifficulty
}) => {
  const [currentQuestion, setCurrentQuestion] = useState<Question>({
    question: "",
    options: ["", "", "", ""],
    correct_answer: 0,
    explanation: "",
    points: 1
  })
  const [editingIndex, setEditingIndex] = useState<number | null>(null)

  const handleAddQuestion = () => {
    if (!currentQuestion.question.trim()) {
      return
    }

    const newQuestion: Question = {
      ...currentQuestion,
      id: Date.now().toString()
    }

    if (editingIndex !== null) {
      // Edit existing question
      const updatedQuestions = [...questions]
      updatedQuestions[editingIndex] = newQuestion
      onQuestionsChange(updatedQuestions)
      setEditingIndex(null)
    } else {
      // Add new question
      onQuestionsChange([...questions, newQuestion])
    }

    // Reset form
    setCurrentQuestion({
      question: "",
      options: ["", "", "", ""],
      correct_answer: 0,
      explanation: "",
      points: 1
    })
  }

  const handleEditQuestion = (index: number) => {
    const question = questions[index]
    setCurrentQuestion(question)
    setEditingIndex(index)
  }

  const handleDeleteQuestion = (index: number) => {
    const updatedQuestions = questions.filter((_, i) => i !== index)
    onQuestionsChange(updatedQuestions)
  }

  const handleOptionChange = (index: number, value: string) => {
    const newOptions = [...currentQuestion.options]
    newOptions[index] = value
    setCurrentQuestion({ ...currentQuestion, options: newOptions })
  }

  const handleAddOption = () => {
    if (currentQuestion.options.length < 6) {
      setCurrentQuestion({
        ...currentQuestion,
        options: [...currentQuestion.options, ""]
      })
    }
  }

  const handleRemoveOption = (index: number) => {
    if (currentQuestion.options.length > 2) {
      const newOptions = currentQuestion.options.filter((_, i) => i !== index)
      setCurrentQuestion({ ...currentQuestion, options: newOptions })
      
      // Adjust correct answer if necessary
      if (currentQuestion.correct_answer >= index) {
        setCurrentQuestion({
          ...currentQuestion,
          correct_answer: Math.max(0, currentQuestion.correct_answer - 1)
        })
      }
    }
  }

  if (!isOpen) return null

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        className="bg-blue-900/95 backdrop-blur-sm border border-blue-500/30 rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto"
      >
        <Card className="p-6">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-2xl font-bold text-blue-200">Question Manager</h2>
              <p className="text-blue-300 text-sm">
                {assessmentTitle} • {assessmentTopic} • {assessmentDifficulty}
              </p>
            </div>
            <Button variant="ghost" onClick={onCancel} className="text-blue-300 hover:text-blue-200">
              ✕
            </Button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Question Form */}
            <div>
              <h3 className="text-lg font-semibold text-blue-200 mb-4">
                {editingIndex !== null ? "Edit Question" : "Add New Question"}
              </h3>
              
              <div className="space-y-4">
                {/* Question Text */}
                <div>
                  <label className="text-blue-300 text-sm mb-2 block">Question</label>
                  <textarea
                    value={currentQuestion.question}
                    onChange={(e) => setCurrentQuestion({ ...currentQuestion, question: e.target.value })}
                    className="w-full px-3 py-2 bg-blue-900/50 border border-blue-500/30 rounded-lg text-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    rows={3}
                    placeholder="Enter your question here..."
                  />
                </div>

                {/* Options */}
                <div>
                  <label className="text-blue-300 text-sm mb-2 block">Options</label>
                  <div className="space-y-2">
                    {currentQuestion.options.map((option, index) => (
                      <div key={index} className="flex items-center space-x-2">
                        <input
                          type="radio"
                          name="correct_answer"
                          checked={currentQuestion.correct_answer === index}
                          onChange={() => setCurrentQuestion({ ...currentQuestion, correct_answer: index })}
                          className="w-4 h-4 text-blue-500 bg-blue-900 border-blue-500 focus:ring-blue-500"
                        />
                        <Input
                          type="text"
                          value={option}
                          onChange={(e) => handleOptionChange(index, e.target.value)}
                          placeholder={`Option ${index + 1}`}
                          className="flex-1"
                        />
                        {currentQuestion.options.length > 2 && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleRemoveOption(index)}
                            className="text-red-300 hover:text-red-200"
                          >
                            ✕
                          </Button>
                        )}
                      </div>
                    ))}
                  </div>
                  
                  {currentQuestion.options.length < 6 && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={handleAddOption}
                      className="mt-2 text-blue-300 hover:text-blue-200"
                    >
                      + Add Option
                    </Button>
                  )}
                </div>

                {/* Explanation */}
                <div>
                  <label className="text-blue-300 text-sm mb-2 block">Explanation (Optional)</label>
                  <textarea
                    value={currentQuestion.explanation}
                    onChange={(e) => setCurrentQuestion({ ...currentQuestion, explanation: e.target.value })}
                    className="w-full px-3 py-2 bg-blue-900/50 border border-blue-500/30 rounded-lg text-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    rows={2}
                    placeholder="Explain why this is the correct answer..."
                  />
                </div>

                {/* Points */}
                <div>
                  <label className="text-blue-300 text-sm mb-2 block">Points</label>
                  <Input
                    type="number"
                    min="1"
                    max="10"
                    value={currentQuestion.points || 1}
                    onChange={(e) => setCurrentQuestion({ ...currentQuestion, points: parseInt(e.target.value) || 1 })}
                    className="w-20"
                  />
                </div>

                {/* Add/Update Button */}
                <Button
                  variant="primary"
                  onClick={handleAddQuestion}
                  disabled={!currentQuestion.question.trim() || currentQuestion.options.filter(o => o.trim()).length < 2}
                  className="w-full"
                >
                  {editingIndex !== null ? "Update Question" : "Add Question"}
                </Button>

                {editingIndex !== null && (
                  <Button
                    variant="ghost"
                    onClick={() => {
                      setEditingIndex(null)
                      setCurrentQuestion({
                        question: "",
                        options: ["", "", "", ""],
                        correct_answer: 0,
                        explanation: "",
                        points: 1
                      })
                    }}
                    className="w-full"
                  >
                    Cancel Edit
                  </Button>
                )}
              </div>
            </div>

            {/* Questions List */}
            <div>
              <h3 className="text-lg font-semibold text-blue-200 mb-4">
                Questions ({questions.length})
              </h3>
              
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {questions.map((question, index) => (
                  <div
                    key={question.id || index}
                    className="p-3 bg-blue-900/20 border border-blue-500/30 rounded-lg"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <h4 className="text-blue-200 font-medium text-sm">
                        Q{index + 1}: {question.question.substring(0, 50)}...
                      </h4>
                      <div className="flex space-x-1">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleEditQuestion(index)}
                          className="text-blue-300 hover:text-blue-200"
                        >
                          Edit
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDeleteQuestion(index)}
                          className="text-red-300 hover:text-red-200"
                        >
                          Delete
                        </Button>
                      </div>
                    </div>
                    
                    <div className="text-blue-300 text-xs">
                      <div>Correct Answer: {question.options[question.correct_answer]}</div>
                      <div>Points: {question.points || 1}</div>
                    </div>
                  </div>
                ))}
              </div>

              {questions.length === 0 && (
                <div className="text-center py-8 text-blue-300">
                  No questions added yet
                </div>
              )}
            </div>
          </div>

          {/* Actions */}
          <div className="flex justify-end space-x-3 mt-6 pt-4 border-t border-blue-500/30">
            <Button variant="ghost" onClick={onCancel}>
              Cancel
            </Button>
            <Button
              variant="primary"
              onClick={onSaveAssessment}
              disabled={questions.length === 0}
            >
              Save Assessment ({questions.length} questions)
            </Button>
          </div>
        </Card>
      </motion.div>
    </motion.div>
  )
}

export default QuestionManager
