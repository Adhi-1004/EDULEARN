"use client"

import type React from "react"
import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { Code, Play, CheckCircle, XCircle, Clock } from "lucide-react"
import { useToast } from "../contexts/ToastContext"
import api from "../utils/api"

interface TestCase {
  input: string
  expected_output: string
  is_hidden: boolean
}

interface CodingQuestion {
  id: string
  title: string
  description: string
  problem_statement: string
  constraints: string[]
  examples: Array<{
    input: string
    output: string
    explanation: string
  }>
  hints: string[]
  points: number
  time_limit: number
  memory_limit: number
  test_cases: TestCase[]
}

interface CodingTestInterfaceProps {
  assessmentId: string
  question: CodingQuestion
  onComplete: (result: any) => void
}

const CodingTestInterface: React.FC<CodingTestInterfaceProps> = ({ assessmentId, question, onComplete }) => {
  const { success, error: showError } = useToast()
  const [code, setCode] = useState("")
  const [language, setLanguage] = useState("python")
  const [executing, setExecuting] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [testResults, setTestResults] = useState<any[]>([])
  const [showHints, setShowHints] = useState(false)

  const languages = [
    { value: "python", label: "Python" },
    { value: "javascript", label: "JavaScript" },
    { value: "java", label: "Java" },
    { value: "cpp", label: "C++" },
    { value: "go", label: "Go" },
  ]

  const defaultCode = {
    python: `def solution():
    # Write your code here
    pass`,
    javascript: `function solution() {
    // Write your code here
}`,
    java: `public class Solution {
    public static void main(String[] args) {
        // Write your code here
    }
}`,
    cpp: `#include <iostream>
using namespace std;

int main() {
    // Write your code here
    return 0;
}`,
    go: `package main

import "fmt"

func main() {
    // Write your code here
}`,
  }

  useEffect(() => {
    setCode(defaultCode[language as keyof typeof defaultCode])
  }, [language])

  const handleRunCode = async () => {
    if (!code.trim()) {
      showError("Error", "Please write some code first")
      return
    }

    try {
      setExecuting(true)

      // Simulate code execution with test cases
      const results = question.test_cases.map((testCase, index) => ({
        input: testCase.input,
        expected_output: testCase.expected_output,
        actual_output: `Simulated output for test case ${index + 1}`,
        passed: Math.random() > 0.3, // Random for demo
        execution_time: Math.floor(Math.random() * 1000),
        memory_used: Math.floor(Math.random() * 100),
      }))

      setTestResults(results)
      success("Success", "Code executed successfully!")
    } catch (err: any) {
      console.error("Failed to execute code:", err)
      showError("Error", "Failed to execute code. Please try again.")
    } finally {
      setExecuting(false)
    }
  }

  const handleSubmit = async () => {
    if (!code.trim()) {
      showError("Error", "Please write some code first")
      return
    }

    try {
      setSubmitting(true)

      const response = await api.post(`/api/assessments/${assessmentId}/coding-submit`, {
        assessment_id: assessmentId,
        question_id: question.id,
        code: code,
        language: language,
        time_taken: 0, // This would be calculated from start time
      })

      if (response.data) {
        success("Success", "Code submitted successfully!")
        onComplete(response.data)
      }
    } catch (err: any) {
      console.error("Failed to submit code:", err)
      showError("Error", "Failed to submit code. Please try again.")
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen pt-20 px-4">
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="panel p-6 mb-6 bg-surface text-fg"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <Code className="w-8 h-8 text-blue-400" />
              <div>
                <h1 className="text-2xl font-bold text-fg">{question.title}</h1>
                <p className="text-muted-fg">{question.description}</p>
              </div>
            </div>
            <div className="flex items-center space-x-4 text-sm text-muted-fg">
              <div className="flex items-center space-x-1">
                <Clock className="w-4 h-4" />
                <span>{question.time_limit}s limit</span>
              </div>
              <div className="flex items-center space-x-1">
                <CheckCircle className="w-4 h-4" />
                <span>{question.points} points</span>
              </div>
            </div>
          </div>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Problem Statement */}
          <motion.div className="panel p-6 bg-surface text-fg">
            <h2 className="text-xl font-semibold mb-4">Problem Statement</h2>
            <p className="text-muted-fg whitespace-pre-wrap">{question.problem_statement}</p>
          </motion.div>

          {/* Constraints */}
          {question.constraints.length > 0 && (
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 }}
              className="panel p-6 bg-elevated border-base"
            >
              <h3 className="text-lg font-semibold mb-3">Constraints</h3>
              <ul className="space-y-1">
                {question.constraints.map((constraint, index) => (
                  <li key={index} className="text-muted-fg">
                    • {constraint}
                  </li>
                ))}
              </ul>
            </motion.div>
          )}

          {/* Examples */}
          {question.examples.length > 0 && (
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
              className="panel p-6 bg-elevated border-base"
            >
              <h3 className="text-lg font-semibold mb-3">Examples</h3>
              <div className="space-y-4">
                {question.examples.map((example, index) => (
                  <div key={index} className="bg-elevated/30 rounded-lg p-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <h4 className="text-fg font-medium mb-2">Input:</h4>
                        <pre className="text-muted-fg text-sm bg-elevated/50 p-2 rounded">{example.input}</pre>
                      </div>
                      <div>
                        <h4 className="text-fg font-medium mb-2">Output:</h4>
                        <pre className="text-muted-fg text-sm bg-elevated/50 p-2 rounded">{example.output}</pre>
                      </div>
                    </div>
                    {example.explanation && (
                      <div className="mt-3">
                        <h4 className="text-fg font-medium mb-1">Explanation:</h4>
                        <p className="text-muted-fg text-sm">{example.explanation}</p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </motion.div>
          )}

          {/* Hints */}
          {question.hints.length > 0 && (
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 }}
              className="panel p-6 bg-elevated border-base"
            >
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-lg font-semibold text-fg">Hints</h3>
                <button onClick={() => setShowHints(!showHints)} className="text-blue-400 hover:text-blue-300 text-sm">
                  {showHints ? "Hide" : "Show"} Hints
                </button>
              </div>
              {showHints && (
                <ul className="space-y-2">
                  {question.hints.map((hint, index) => (
                    <li key={index} className="text-muted-fg flex items-start space-x-2">
                      <span className="text-blue-400 mt-1">💡</span>
                      <span>{hint}</span>
                    </li>
                  ))}
                </ul>
              )}
            </motion.div>
          )}
        </div>

        {/* Code Editor */}
        <div className="space-y-6">
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="panel p-6 bg-elevated border-base"
          >
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-fg">Code Editor</h2>
              <div className="flex items-center space-x-3">
                <select
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="px-3 py-1 bg-elevated border-base rounded text-fg text-sm"
                >
                  {languages.map((lang) => (
                    <option key={lang.value} value={lang.value}>
                      {lang.label}
                    </option>
                  ))}
                </select>
                <button
                  onClick={handleRunCode}
                  disabled={executing}
                  className="px-4 py-1 bg-green-600 hover:bg-green-700 disabled:bg-green-600/50 text-white rounded text-sm flex items-center space-x-1"
                >
                  <Play className="w-3 h-3" />
                  <span>{executing ? "Running..." : "Run"}</span>
                </button>
              </div>
            </div>

            <textarea
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder="Write your code here..."
              className="w-full h-96 px-3 py-2 bg-elevated border-base rounded-lg text-fg font-mono text-sm resize-none focus:outline-none focus:ring-2 focus:ring-base"
              spellCheck={false}
            />
          </motion.div>

          {/* Test Results */}
          {testResults.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="panel p-6 bg-elevated border-base"
            >
              <h3 className="text-lg font-semibold mb-4">Test Results</h3>
              <div className="space-y-3">
                {testResults.map((result, index) => (
                  <div key={index} className="bg-elevated/30 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-fg font-medium">Test Case {index + 1}</span>
                      <div className="flex items-center space-x-2">
                        {result.passed ? (
                          <CheckCircle className="w-4 h-4 text-green-400" />
                        ) : (
                          <XCircle className="w-4 h-4 text-red-400" />
                        )}
                        <span className={`text-sm ${result.passed ? "text-green-400" : "text-red-400"}`}>
                          {result.passed ? "Passed" : "Failed"}
                        </span>
                      </div>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                      <div>
                        <span className="text-muted-fg">Input: </span>
                        <pre className="text-fg mt-1">{result.input}</pre>
                      </div>
                      <div>
                        <span className="text-muted-fg">Expected: </span>
                        <pre className="text-fg mt-1">{result.expected_output}</pre>
                      </div>
                      <div>
                        <span className="text-muted-fg">Output: </span>
                        <pre className="text-fg mt-1">{result.actual_output}</pre>
                      </div>
                      <div className="flex items-center space-x-4 text-xs text-muted-fg">
                        <span>Time: {result.execution_time}ms</span>
                        <span>Memory: {result.memory_used}MB</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>
          )}

          {/* Submit Button */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="flex justify-end"
          >
            <button
              onClick={handleSubmit}
              disabled={submitting || !code.trim()}
              className="px-8 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-600/50 text-white rounded-lg transition-colors flex items-center space-x-2"
            >
              {submitting ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              ) : (
                <CheckCircle className="w-4 h-4" />
              )}
              <span>{submitting ? "Submitting..." : "Submit Solution"}</span>
            </button>
          </motion.div>
        </div>
      </div>
    </div>
  )
}

export default CodingTestInterface
