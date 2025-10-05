"use client"

import type React from "react"
import { useState } from "react"
import { motion } from "framer-motion"
import { Code, Trash2, Save } from "lucide-react"
import { useToast } from "../contexts/ToastContext"
import api from "../utils/api"

interface CodingQuestionFormProps {
  assessmentId: string
  onQuestionAdded: () => void
  onClose: () => void
}

const CodingQuestionForm: React.FC<CodingQuestionFormProps> = ({ assessmentId, onQuestionAdded, onClose }) => {
  const { success, error: showError } = useToast()
  const [loading, setLoading] = useState(false)

  const [formData, setFormData] = useState({
    title: "",
    description: "",
    problem_statement: "",
    constraints: [""],
    examples: [{ input: "", output: "", explanation: "" }],
    test_cases: [{ input: "", expected_output: "", is_hidden: false }],
    hints: [""],
    points: 10,
    time_limit: 30,
    memory_limit: 128,
  })

  const handleInputChange = (field: keyof typeof formData, value: any) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }))
  }

  const handleArrayChange = (field: keyof typeof formData, index: number, value: any) => {
    setFormData((prev) => ({
      ...prev,
      [field]: (prev[field] as any[]).map((item: any, i: number) => (i === index ? value : item)),
    }))
  }

  const addArrayItem = (field: keyof typeof formData, defaultValue: any) => {
    setFormData((prev) => ({
      ...prev,
      [field]: [...(prev[field] as any[]), defaultValue],
    }))
  }

  const removeArrayItem = (field: keyof typeof formData, index: number) => {
    setFormData((prev) => ({
      ...prev,
      [field]: (prev[field] as any[]).filter((_: any, i: number) => i !== index),
    }))
  }

  const handleSubmit = async () => {
    // Validate required fields
    if (!formData.title.trim()) {
      showError("Error", "Please enter a title for the coding question")
      return
    }

    if (!formData.problem_statement.trim()) {
      showError("Error", "Please enter a problem statement")
      return
    }

    if (formData.problem_statement.trim().length < 10) {
      showError("Error", "Problem statement must be at least 10 characters long")
      return
    }

    // Ensure description is not empty and meets minimum length
    const description = formData.description.trim() || "Coding challenge question"
    if (description.length < 10) {
      showError("Error", "Description must be at least 10 characters long")
      return
    }

    if (formData.test_cases.length === 0) {
      showError("Error", "Please add at least one test case")
      return
    }

    const validTestCases = formData.test_cases.filter((t) => t.input.trim() && t.expected_output.trim())
    if (validTestCases.length === 0) {
      showError("Error", "Please add at least one valid test case with input and expected output")
      return
    }

    try {
      setLoading(true)

      // Prepare data according to backend schema
      const filteredTestCases = formData.test_cases.filter((t) => t.input.trim() && t.expected_output.trim())
      const filteredExamples = formData.examples.filter((e) => e.input.trim() && e.output.trim())

      const requestData = {
        title: formData.title.trim(),
        description: description, // Use the validated description
        problem_statement: formData.problem_statement.trim(),
        constraints: formData.constraints.filter((c) => c.trim()),
        examples: filteredExamples.map((example) => ({
          input: example.input.trim(),
          output: example.output.trim(),
          explanation: example.explanation.trim() || "",
        })),
        test_cases: filteredTestCases.map((testCase) => ({
          input: testCase.input.trim(),
          expected_output: testCase.expected_output.trim(),
          is_hidden: testCase.is_hidden || false,
        })),
        hidden_test_cases: filteredTestCases
          .filter((t) => t.is_hidden)
          .map((testCase) => ({
            input: testCase.input.trim(),
            expected_output: testCase.expected_output.trim(),
          })),
        hints: formData.hints.filter((h) => h.trim()),
        points: Math.max(1, formData.points), // Ensure points is at least 1
        time_limit: Math.max(1, formData.time_limit), // Ensure time_limit is at least 1
        memory_limit: Math.max(1, formData.memory_limit), // Ensure memory_limit is at least 1
      }

      console.log("🔍 [CODING QUESTION] Sending data:", requestData)

      const response = await api.post(`/api/assessments/${assessmentId}/coding-questions`, requestData)

      if (response.data) {
        success("Success", "Coding question added successfully!")
        onQuestionAdded()
        onClose()
      }
    } catch (err: any) {
      console.error("Failed to add coding question:", err)

      // Show more specific error messages
      if (err.response?.status === 422) {
        const errorDetails = err.response?.data?.detail || "Validation error"
        showError("Validation Error", `Please check your input: ${errorDetails}`)
      } else if (err.response?.status === 400) {
        showError("Bad Request", "Invalid data provided. Please check your input.")
      } else if (err.response?.status === 404) {
        showError("Not Found", "Assessment not found. Please try again.")
      } else if (err.response?.status === 403) {
        showError("Access Denied", "You do not have permission to add questions to this assessment.")
      } else {
        showError("Error", `Failed to add coding question: ${err.message || "Please try again."}`)
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        className="panel p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto bg-surface text-fg"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex justify-between items-center mb-6">
          <div className="flex items-center space-x-2">
            <Code className="w-6 h-6 text-accent" />
            <h2 className="text-2xl font-bold">Add Coding Question</h2>
          </div>
          <button onClick={onClose} className="text-muted-fg hover:text-fg transition-colors">
            ✕
          </button>
        </div>

        <div className="space-y-6">
          {/* Basic Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-fg font-medium mb-2">Title *</label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => handleInputChange("title", e.target.value)}
                placeholder="e.g., Two Sum Problem"
                className="w-full px-3 py-2 bg-elevated border border-base rounded-lg text-fg focus:outline-none focus:ring-2 focus:ring-[var(--primary)]"
              />
            </div>
            <div>
              <label className="block text-fg font-medium mb-2">Points</label>
              <input
                type="number"
                value={formData.points}
                onChange={(e) => handleInputChange("points", Number.parseInt(e.target.value))}
                min="1"
                className="w-full px-3 py-2 bg-elevated border border-base rounded-lg text-fg focus:outline-none focus:ring-2 focus:ring-[var(--primary)]"
              />
            </div>
          </div>

          {/* Description */}
          <div>
            <label className="block text-fg font-medium mb-2">Description</label>
            <textarea
              value={formData.description}
              onChange={(e) => handleInputChange("description", e.target.value)}
              placeholder="Brief description of the problem..."
              className="w-full px-3 py-2 bg-elevated border border-base rounded-lg text-fg focus:outline-none focus:ring-2 focus:ring-[var(--primary)] h-20 resize-none"
            />
          </div>

          {/* Problem Statement */}
          <div>
            <label className="block text-fg font-medium mb-2">Problem Statement *</label>
            <textarea
              value={formData.problem_statement}
              onChange={(e) => handleInputChange("problem_statement", e.target.value)}
              placeholder="Detailed problem statement..."
              className="w-full px-3 py-2 bg-elevated border border-base rounded-lg text-fg focus:outline-none focus:ring-2 focus:ring-[var(--primary)] h-32 resize-none"
            />
          </div>

          {/* Constraints */}
          <div>
            <label className="block text-fg font-medium mb-2">Constraints</label>
            {formData.constraints.map((constraint, index) => (
              <div key={index} className="flex items-center space-x-2 mb-2">
                <input
                  type="text"
                  value={constraint}
                  onChange={(e) => handleArrayChange("constraints", index, e.target.value)}
                  placeholder="e.g., 1 ≤ n ≤ 10^5"
                  className="flex-1 px-3 py-2 bg-elevated border border-base rounded-lg text-fg focus:outline-none focus:ring-2 focus:ring-[var(--primary)]"
                />
                <button
                  onClick={() => removeArrayItem("constraints", index)}
                  className="text-red-400 hover:text-red-300"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
            <button
              onClick={() => addArrayItem("constraints", "")}
              className="text-blue-400 hover:text-blue-300 text-sm"
            >
              + Add Constraint
            </button>
          </div>

          {/* Examples */}
          <div>
            <label className="block text-fg font-medium mb-2">Examples</label>
            {formData.examples.map((example, index) => (
              <div key={index} className="border border-base/30 rounded-lg p-3 mb-3">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-2">
                  <div>
                    <label className="block text-fg-300 text-sm mb-1">Input</label>
                    <textarea
                      value={example.input}
                      onChange={(e) => handleArrayChange("examples", index, { ...example, input: e.target.value })}
                      placeholder="Input example..."
                      className="w-full px-2 py-1 bg-elevated border border-base rounded text-fg text-sm resize-none h-16"
                    />
                  </div>
                  <div>
                    <label className="block text-fg-300 text-sm mb-1">Output</label>
                    <textarea
                      value={example.output}
                      onChange={(e) => handleArrayChange("examples", index, { ...example, output: e.target.value })}
                      placeholder="Expected output..."
                      className="w-full px-2 py-1 bg-elevated border border-base rounded text-fg text-sm resize-none h-16"
                    />
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex-1 mr-2">
                    <label className="block text-fg-300 text-sm mb-1">Explanation</label>
                    <input
                      type="text"
                      value={example.explanation}
                      onChange={(e) =>
                        handleArrayChange("examples", index, { ...example, explanation: e.target.value })
                      }
                      placeholder="Explanation (optional)..."
                      className="w-full px-2 py-1 bg-elevated border border-base rounded text-fg text-sm"
                    />
                  </div>
                  <button
                    onClick={() => removeArrayItem("examples", index)}
                    className="text-red-400 hover:text-red-300 ml-2"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
            <button
              onClick={() => addArrayItem("examples", { input: "", output: "", explanation: "" })}
              className="text-blue-400 hover:text-blue-300 text-sm"
            >
              + Add Example
            </button>
          </div>

          {/* Test Cases */}
          <div>
            <label className="block text-fg font-medium mb-2">Test Cases *</label>
            {formData.test_cases.map((testCase, index) => (
              <div key={index} className="border border-base/30 rounded-lg p-3 mb-3">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-2">
                  <div>
                    <label className="block text-fg-300 text-sm mb-1">Input</label>
                    <textarea
                      value={testCase.input}
                      onChange={(e) => handleArrayChange("test_cases", index, { ...testCase, input: e.target.value })}
                      placeholder="Test case input..."
                      className="w-full px-2 py-1 bg-elevated border border-base rounded text-fg text-sm resize-none h-16"
                    />
                  </div>
                  <div>
                    <label className="block text-fg-300 text-sm mb-1">Expected Output</label>
                    <textarea
                      value={testCase.expected_output}
                      onChange={(e) =>
                        handleArrayChange("test_cases", index, { ...testCase, expected_output: e.target.value })
                      }
                      placeholder="Expected output..."
                      className="w-full px-2 py-1 bg-elevated border border-base rounded text-fg text-sm resize-none h-16"
                    />
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <label className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={testCase.is_hidden}
                      onChange={(e) =>
                        handleArrayChange("test_cases", index, { ...testCase, is_hidden: e.target.checked })
                      }
                      className="rounded"
                    />
                    <span className="text-fg-300 text-sm">Hidden test case</span>
                  </label>
                  <button
                    onClick={() => removeArrayItem("test_cases", index)}
                    className="text-red-400 hover:text-red-300"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
            <button
              onClick={() => addArrayItem("test_cases", { input: "", expected_output: "", is_hidden: false })}
              className="text-blue-400 hover:text-blue-300 text-sm"
            >
              + Add Test Case
            </button>
          </div>

          {/* Hints */}
          <div>
            <label className="block text-fg font-medium mb-2">Hints</label>
            {formData.hints.map((hint, index) => (
              <div key={index} className="flex items-center space-x-2 mb-2">
                <input
                  type="text"
                  value={hint}
                  onChange={(e) => handleArrayChange("hints", index, e.target.value)}
                  placeholder="Hint for students..."
                  className="flex-1 px-3 py-2 bg-elevated border border-base rounded-lg text-fg focus:outline-none focus:ring-2 focus:ring-[var(--primary)]"
                />
                <button onClick={() => removeArrayItem("hints", index)} className="text-red-400 hover:text-red-300">
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
            <button onClick={() => addArrayItem("hints", "")} className="text-blue-400 hover:text-blue-300 text-sm">
              + Add Hint
            </button>
          </div>

          {/* Limits */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-fg font-medium mb-2">Time Limit (seconds)</label>
              <input
                type="number"
                value={formData.time_limit}
                onChange={(e) => handleInputChange("time_limit", Number.parseInt(e.target.value))}
                min="1"
                className="w-full px-3 py-2 bg-elevated border border-base rounded-lg text-fg focus:outline-none focus:ring-2 focus:ring-[var(--primary)]"
              />
            </div>
            <div>
              <label className="block text-fg font-medium mb-2">Memory Limit (MB)</label>
              <input
                type="number"
                value={formData.memory_limit}
                onChange={(e) => handleInputChange("memory_limit", Number.parseInt(e.target.value))}
                min="1"
                className="w-full px-3 py-2 bg-elevated border border-base rounded-lg text-fg focus:outline-none focus:ring-2 focus:ring-[var(--primary)]"
              />
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex justify-end space-x-3 mt-6">
          <button
            onClick={onClose}
            className="px-6 py-2 bg-elevated hover:bg-base text-fg rounded-lg transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={loading}
            className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-600/50 text-white rounded-lg transition-colors flex items-center space-x-2"
          >
            {loading ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            ) : (
              <Save className="w-4 h-4" />
            )}
            <span>{loading ? "Adding..." : "Add Question"}</span>
          </button>
        </div>
      </motion.div>
    </motion.div>
  )
}

export default CodingQuestionForm
