"use client"

import type React from "react"
import { useState, useEffect } from "react"
import { useParams } from "react-router-dom"
import { motion } from "framer-motion"
import type { User, CodingProblem, CodingTestResult } from "../types"
import { useTheme } from "../contexts/ThemeContext"
import { useToast } from "../contexts/ToastContext"
import { Editor } from "@monaco-editor/react"
import api from "../utils/api"
import { ANIMATION_VARIANTS } from "../utils/constants"
import PageShell from "../components/ui/PageShell"
import Button from "../components/ui/Button"
import LoadingSpinner from "../components/ui/LoadingSpinner"

interface CodingProblemPageProps {
  user: User
}

const CodingProblemPage: React.FC<CodingProblemPageProps> = ({ user: _user }) => {
  const { problemId } = useParams<{ problemId: string }>()
  const { colorScheme } = useTheme()
  const { success, error: showError, info } = useToast()

  const [problem, setProblem] = useState<CodingProblem | null>(null)
  const [code, setCode] = useState<string>("")
  const [language, setLanguage] = useState<string>("python")
  const [loading, setLoading] = useState(true)
  const [executing, setExecuting] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [testResults, setTestResults] = useState<CodingTestResult[]>([])
  const [showHints, setShowHints] = useState(false)
  const [hintsUsed, setHintsUsed] = useState(0)
  const [sessionId, setSessionId] = useState<string>("")
  const [keystrokes, setKeystrokes] = useState(0)
  const [startTime] = useState(Date.now())
  const [autocompleteEnabled, setAutocompleteEnabled] = useState(true)
  const [useJudge0, setUseJudge0] = useState(false)
  const [expandedTests, setExpandedTests] = useState<Set<number>>(new Set())

  const languages = [
    { value: "python", label: "Python", template: "# Write your solution here\ndef solution():\n    pass" },
    {
      value: "javascript",
      label: "JavaScript",
      template: "// Write your solution here\nfunction solution() {\n    // Your code\n}",
    },
    {
      value: "java",
      label: "Java",
      template:
        "// Write your solution here\npublic class Solution {\n    public void solution() {\n        // Your code\n    }\n}",
    },
    {
      value: "cpp",
      label: "C++",
      template:
        "// Write your solution here\n#include <iostream>\nusing namespace std;\n\nint main() {\n    // Your code\n    return 0;\n}",
    },
  ]

  // Get the correct Monaco language ID
  const getMonacoLanguage = (lang: string) => {
    const languageMap: { [key: string]: string } = {
      python: "python",
      javascript: "javascript",
      java: "java",
      cpp: "cpp",
    }
    return languageMap[lang] || "python"
  }

  useEffect(() => {
    if (problemId) {
      fetchProblem()
      startSession()
    }
  }, [problemId])

  useEffect(() => {
    // Set default template when language changes
    const selectedLang = languages.find((lang) => lang.value === language)
    if (selectedLang) {
      // Only set template if code is empty or just whitespace
      if (!code.trim() || code.trim() === "") {
        setCode(selectedLang.template)
      }
    }
  }, [language])

  const fetchProblem = async () => {
    try {
      setLoading(true)
      const response = await api.get(`/api/coding/problems/${problemId}`)

      if (response.data.success) {
        setProblem(response.data.problem)
      } else {
        showError("Problem not found")
      }
    } catch (error) {
      showError("Failed to load problem")
    } finally {
      setLoading(false)
    }
  }

  const startSession = async () => {
    try {
      const response = await api.post("/api/coding/sessions/start", {
        problem_id: problemId,
      })

      if (response.data.success) {
        setSessionId(response.data.session_id)
      }
    } catch (error) {
      console.error("Failed to start session:", error)
    }
  }

  const updateSession = async (updates: any) => {
    if (!sessionId) return

    try {
      await api.put(`/api/coding/sessions/${sessionId}`, updates)
    } catch (error) {
      console.error("Failed to update session:", error)
    }
  }

  const handleCodeChange = (newCode: string) => {
    setCode(newCode)
    setKeystrokes((prev) => prev + 1)

    // Update session every 50 keystrokes
    if (keystrokes % 50 === 0) {
      updateSession({
        keystrokes: keystrokes + 1,
        lines_of_code: newCode.split("\n").length,
      })
    }
  }

  const runCode = async (codeToRun?: string) => {
    const codeToExecute = codeToRun || code

    if (!problem || !codeToExecute.trim()) {
      showError("Please write some code first")
      return
    }

    // Validate code before execution
    const validation = validateCode(codeToExecute)
    if (!validation.isValid) {
      showError(`Code validation failed: ${validation.errors.join(", ")}`)
      return
    }

    setExecuting(true)
    setTestResults([])

    try {
      // Use actual test cases for running (not just examples)
      const testCases =
        problem.test_cases ||
        problem.examples.map((example, index) => ({
          input: parseInput(example.input),
          output: parseOutput(example.output),
          description: `Example ${index + 1}`,
        }))

      console.log("🧪 [EXECUTION] Using test cases:", testCases.length)
      console.log("🧪 [EXECUTION] Test cases:", testCases)

      const response = await api.post("/api/coding/execute", {
        code: codeToExecute,
        language,
        test_cases: testCases,
        timeout: 10,
        use_judge0: useJudge0,
      })

      console.log("🔍 [EXECUTION] Response:", response.data)

      const exec = response.data.execution_result || response.data
      if (response.data.success && exec) {
        const results = exec.results || []
        setTestResults(results)

        const passed = results.filter((r: any) => r.passed).length
        const total = results.length

        console.log(`📊 [EXECUTION] Results: ${passed}/${total} passed`)

        if (passed === total && total > 0) {
          success(`All ${total} test cases passed! 🎉`)
        } else if (total > 0) {
          const failedTests = results.filter((r: any) => !r.passed)
          if (failedTests.length > 0) {
            console.log("❌ [EXECUTION] Failed tests:", failedTests)
            info(`${passed}/${total} test cases passed. Check the results below for details.`)
          } else {
            info(`${passed}/${total} test cases passed`)
          }
        } else {
          success("Code executed successfully!")
        }

        // Update session with detailed results
        updateSession({
          test_runs: 1,
          last_test_results: {
            passed,
            total,
            execution_time: results.reduce((sum: number, r: any) => sum + (r.execution_time || 0), 0),
          },
        })
      } else {
        console.error("❌ [EXECUTION] Execution failed:", response.data)
        const errorMessage = exec?.error || response.data.error || response.data.error_message || "Execution failed"
        const errorDetails = response.data.details || ""
        showError(`Execution failed: ${errorMessage}${errorDetails ? `\nDetails: ${errorDetails}` : ""}`)
      }
    } catch (error: any) {
      console.error("Execution error:", error)
      const errorMessage =
        error.response?.data?.detail || error.response?.data?.error || "Code execution failed. Please check your code."
      showError(errorMessage)

      // Update session with error
      updateSession({
        test_runs: 1,
        last_error: errorMessage,
      })
    } finally {
      setExecuting(false)
    }
  }

  const submitSolution = async (codeToSubmit?: string) => {
    const codeToExecute = codeToSubmit || code

    if (!problem || !codeToExecute.trim()) {
      showError("Please write some code first")
      return
    }

    // Validate code before submission
    const validation = validateCode(codeToExecute)
    if (!validation.isValid) {
      showError(`Code validation failed: ${validation.errors.join(", ")}`)
      return
    }

    setSubmitting(true)

    try {
      // Use the same test cases that were used in execution for consistency
      const testCasesToUse =
        problem.test_cases ||
        problem.examples.map((example, index) => ({
          input: parseInput(example.input),
          output: parseOutput(example.output),
          description: `Example ${index + 1}`,
        }))

      console.log("📤 [SUBMISSION] Using test cases:", testCasesToUse.length)
      console.log("📤 [SUBMISSION] Test cases:", testCasesToUse)

      const testResponse = await api.post("/api/coding/execute", {
        code: codeToExecute,
        language,
        test_cases: testCasesToUse,
        timeout: 10,
        use_judge0: useJudge0,
      })

      const exec = testResponse.data.execution_result || testResponse.data
      if (!testResponse.data.success || !exec) {
        showError("Code failed test cases. Please fix your solution.")
        setTestResults(exec?.results || [])
        return
      }

      const passedTests = (exec.results || []).filter((r: any) => r.passed).length
      const totalTests = (exec.results || []).length

      if (passedTests < totalTests) {
        showError(`Only ${passedTests}/${totalTests} test cases passed. Please fix your solution before submitting.`)
        setTestResults(exec.results || [])
        return
      }

      // Submit to coding platform
      const response = await api.post("/api/coding/submit", {
        problem_id: problemId,
        code: codeToExecute,
        language,
        session_id: sessionId,
      })

      if (response.data.success) {
        const submission = response.data.submission

        if (submission.status === "accepted") {
          success("🎉 Solution Accepted! Great job!")

          // End session with success
          if (sessionId) {
            await api.post(`/api/coding/sessions/${sessionId}/end`, {
              final_status: "accepted",
              solution_code: codeToExecute,
              completion_time: Date.now() - startTime,
            })
          }

          // Navigate to submission details
          setTimeout(() => {
            window.location.href = `/coding/submission/${submission.id}`
          }, 2000)
        } else {
          const statusMessages = {
            wrong_answer: "Wrong Answer - Some test cases failed",
            time_limit_exceeded: "Time Limit Exceeded - Your solution is too slow",
            runtime_error: "Runtime Error - Check your code for errors",
            compilation_error: "Compilation Error - Fix syntax errors",
            memory_limit_exceeded: "Memory Limit Exceeded - Your solution uses too much memory",
            presentation_error: "Presentation Error - Check your output format",
          }

          const errorMessage = statusMessages[submission.status as keyof typeof statusMessages] || "Submission failed"
          showError(errorMessage)
          setTestResults(submission.test_results || [])

          // Update session with failure
          updateSession({
            submissions: 1,
            last_submission_status: submission.status,
            last_error: errorMessage,
          })
        }
      } else {
        showError(response.data.error || "Submission failed")
      }
    } catch (error: any) {
      console.error("Submission error:", error)
      const errorMessage =
        error.response?.data?.detail || error.response?.data?.error || "Failed to submit solution. Please try again."
      showError(errorMessage)

      // Update session with error
      updateSession({
        submissions: 1,
        last_error: errorMessage,
      })
    } finally {
      setSubmitting(false)
    }
  }

  const showHint = () => {
    if (!problem || hintsUsed >= problem.hints.length) return

    setShowHints(true)
    setHintsUsed((prev) => prev + 1)

    // Update session
    updateSession({ hints_used: 1 })
  }

  const parseInput = (inputStr: string): any => {
    try {
      // Enhanced input parsing for different formats
      if (inputStr.includes("=")) {
        const match = inputStr.match(/=\s*(.+)$/)
        if (match) {
          return JSON.parse(match[1].replace(/'/g, '"'))
        }
      }

      // Try to parse as JSON directly
      if (inputStr.startsWith("[") || inputStr.startsWith("{")) {
        return JSON.parse(inputStr.replace(/'/g, '"'))
      }

      // Handle space-separated values
      if (inputStr.includes(" ")) {
        const parts = inputStr.split(" ").map((part) => {
          const num = Number.parseFloat(part)
          return isNaN(num) ? part : num
        })
        return parts.length === 1 ? parts[0] : parts
      }

      // Try to parse as number
      const num = Number.parseFloat(inputStr)
      return isNaN(num) ? inputStr : num
    } catch {
      return inputStr
    }
  }

  const parseOutput = (outputStr: string): any => {
    try {
      // Enhanced output parsing
      if (outputStr.startsWith("[") || outputStr.startsWith("{")) {
        return JSON.parse(outputStr.replace(/'/g, '"'))
      }

      // Try to parse as number
      const num = Number.parseFloat(outputStr)
      if (!isNaN(num)) {
        return num
      }

      return outputStr
    } catch {
      return outputStr
    }
  }

  // Helper function to validate code before execution
  const validateCode = (code: string): { isValid: boolean; errors: string[] } => {
    const errors: string[] = []

    if (!code.trim()) {
      errors.push("Code cannot be empty")
    }

    if (language === "python") {
      // Basic Python syntax checks
      const lines = code.split("\n")
      let indentLevel = 0

      for (let i = 0; i < lines.length; i++) {
        const line = lines[i]
        if (line.trim()) {
          const currentIndent = line.length - line.trimStart().length
          if (currentIndent > indentLevel + 4) {
            errors.push(`Line ${i + 1}: Unexpected indentation`)
          }
          if (line.trim().endsWith(":")) {
            indentLevel = currentIndent
          }
        }
      }
    }

    return { isValid: errors.length === 0, errors }
  }

  const toggleTestExpansion = (index: number) => {
    setExpandedTests((prev) => {
      const newSet = new Set(prev)
      if (newSet.has(index)) {
        newSet.delete(index)
      } else {
        newSet.add(index)
      }
      return newSet
    })
  }


  if (loading) {
    return (
      <div className="min-h-screen pt-20 px-4 flex items-center justify-center">
        <LoadingSpinner size="lg" text="Loading problem..." />
      </div>
    )
  }

  if (!problem) {
    return (
      <div className="min-h-screen pt-20 px-4 flex items-center justify-center">
        <PageShell
          title="Problem"
          headerRight={
            <Button onClick={() => (window.location.href = "/coding")} variant="outline" size="sm">
              ← Back
            </Button>
          }
        >
          <div className="text-6xl mb-4">❌</div>
          <h2 className="text-2xl font-bold text-purple-200 mb-2">Problem Not Found</h2>
          <p className="text-purple-300 mb-6">The requested problem could not be loaded.</p>
        </PageShell>
      </div>
    )
  }

  return (
    <PageShell
      title={problem ? problem.title : "Problem"}
      subtitle={problem ? `${problem.topic} • ${problem.difficulty}` : undefined}
      headerRight={
        <Button onClick={() => (window.location.href = "/coding")} variant="outline" size="sm">
          ← Back
        </Button>
      }
    >
      <div className="min-h-[calc(100vh-7rem)] px-1 sm:px-0">
        <div className="w-[95%] mx-auto">
          <div
            className="grid grid-cols-1 lg:grid-cols-[45%_55%] xl:grid-cols-[40%_60%] gap-6"
            style={{ minHeight: "calc(100vh - 160px)" }}
          >
            {/* Problem Description */}
            <motion.div
              variants={ANIMATION_VARIANTS.slideLeft}
              initial="initial"
              animate="animate"
              className="overflow-visible"
              style={{ minHeight: "600px" }}
            >
              <div className="p-6 h-full">
                {/* Description */}
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-purple-200 mb-3">Description</h3>
                  <p className="text-purple-300 leading-relaxed whitespace-pre-line">{problem.description}</p>
                </div>

                {/* Examples */}
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-purple-200 mb-3">Examples</h3>
                  <div className="space-y-4">
                    {problem.examples.map((example, index) => (
                      <div key={index} className="bg-purple-900/20 rounded-lg p-4">
                        <div className="font-semibold text-purple-200 mb-2">Example {index + 1}:</div>
                        <div className="space-y-2 text-sm">
                          <div>
                            <span className="text-purple-300">Input: </span>
                            <code className="text-purple-100 bg-purple-800/30 px-2 py-1 rounded">
                              {typeof example.input === "string" ? example.input : JSON.stringify(example.input)}
                            </code>
                          </div>
                          <div>
                            <span className="text-purple-300">Output: </span>
                            <code className="text-purple-100 bg-purple-800/30 px-2 py-1 rounded">
                              {typeof example.output === "string" ? example.output : JSON.stringify(example.output)}
                            </code>
                          </div>
                          {example.explanation && (
                            <div>
                              <span className="text-purple-300">Explanation: </span>
                              <span className="text-purple-200">{example.explanation}</span>
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Test Cases */}
                {problem.test_cases && problem.test_cases.length > 0 && (
                  <div className="mb-6">
                    <h3 className="text-lg font-semibold text-purple-200 mb-3">Test Cases</h3>
                    <div className="space-y-4">
                      {problem.test_cases.map((testCase, index) => (
                        <div key={index} className="bg-blue-900/20 rounded-lg p-4 border border-blue-500/30">
                          <div className="font-semibold text-blue-200 mb-2">Test Case {index + 1}:</div>
                          <div className="space-y-2 text-sm">
                            <div>
                              <span className="text-blue-300">Input: </span>
                              <code className="text-blue-100 bg-blue-800/30 px-2 py-1 rounded font-mono">
                                {typeof testCase.input === "string" ? testCase.input : JSON.stringify(testCase.input)}
                              </code>
                            </div>
                            <div>
                              <span className="text-blue-300">Expected Output: </span>
                              <code className="text-blue-100 bg-blue-800/30 px-2 py-1 rounded font-mono">
                                {typeof testCase.output === "string" ? testCase.output : JSON.stringify(testCase.output)}
                              </code>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Constraints */}
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-purple-200 mb-3">Constraints</h3>
                  <ul className="space-y-1">
                    {problem.constraints.map((constraint, index) => (
                      <li key={index} className="text-purple-300 text-sm">
                        • {constraint}
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Hints */}
                <div className="mb-6">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="text-lg font-semibold text-purple-200">
                      Hints ({hintsUsed}/{problem.hints.length})
                    </h3>
                    {hintsUsed < problem.hints.length && (
                      <Button onClick={showHint} variant="outline" size="sm">
                        💡 Show Hint
                      </Button>
                    )}
                  </div>

                  {showHints && (
                    <div className="space-y-2">
                      {problem.hints.slice(0, hintsUsed).map((hint, index) => (
                        <motion.div
                          key={index}
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-3"
                        >
                          <div className="text-sm text-blue-200">
                            <span className="font-semibold">Hint {index + 1}: </span>
                            {hint}
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Expected Complexity */}
                <div>
                  <h3 className="text-lg font-semibold text-purple-200 mb-3">Expected Complexity</h3>
                  <div className="flex space-x-4 text-sm">
                    <div>
                      <span className="text-purple-300">Time: </span>
                      <code className="text-purple-100 bg-purple-800/30 px-2 py-1 rounded">
                        {problem.expected_complexity.time}
                      </code>
                    </div>
                    <div>
                      <span className="text-purple-300">Space: </span>
                      <code className="text-purple-100 bg-purple-800/30 px-2 py-1 rounded">
                        {problem.expected_complexity.space}
                      </code>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>

            {/* Code Editor */}
            <motion.div
              variants={ANIMATION_VARIANTS.slideRight}
              initial="initial"
              animate="animate"
              className="flex flex-col"
            >
              <div style={{ height: "calc(100vh - 140px)", minHeight: "600px" }}>
                <div className="p-6 flex flex-col h-full">
                  {/* Editor Header */}
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-4">
                      <select
                        value={language}
                        onChange={(e) => setLanguage(e.target.value)}
                        className="px-3 py-1 bg-purple-800/30 border border-purple-500/30 rounded text-purple-100 text-sm focus:outline-none focus:border-purple-400"
                      >
                        {languages.map((lang) => (
                          <option key={lang.value} value={lang.value}>
                            {lang.label}
                          </option>
                        ))}
                      </select>

                      <div className="flex items-center space-x-4">
                        <label className="flex items-center space-x-2 text-sm text-purple-300">
                          <input
                            type="checkbox"
                            checked={autocompleteEnabled}
                            onChange={(e) => setAutocompleteEnabled(e.target.checked)}
                            className="w-4 h-4 text-purple-600 bg-purple-800/30 border-purple-500/30 rounded focus:ring-purple-400 focus:ring-2"
                          />
                          <span>Autocomplete</span>
                        </label>

                        <label className="flex items-center space-x-2 text-sm text-purple-300">
                          <input
                            type="checkbox"
                            checked={useJudge0}
                            onChange={(e) => setUseJudge0(e.target.checked)}
                            className="w-4 h-4 text-purple-600 bg-purple-800/30 border-purple-500/30 rounded focus:ring-purple-400 focus:ring-2"
                          />
                          <span>Judge0 API</span>
                        </label>
                      </div>

                      <div className="text-sm text-purple-400">
                        Time: {Math.floor((Date.now() - startTime) / 1000)}s
                      </div>
                    </div>

                    <div className="flex space-x-2">
                      <Button
                        onClick={() => runCode()}
                        disabled={executing || !code.trim()}
                        variant="outline"
                        size="sm"
                      >
                        {executing ? (
                          <>
                            <LoadingSpinner size="sm" />
                            <span className="ml-1">Running...</span>
                          </>
                        ) : (
                          "▶️ Run"
                        )}
                      </Button>

                      <Button
                        onClick={() => submitSolution()}
                        disabled={submitting || !code.trim()}
                        variant="primary"
                        size="sm"
                      >
                        {submitting ? (
                          <>
                            <LoadingSpinner size="sm" />
                            <span className="ml-1">Submitting...</span>
                          </>
                        ) : (
                          "🚀 Submit"
                        )}
                      </Button>
                    </div>
                  </div>

                  {/* Monaco Code Editor */}
                  <div
                    className="border border-purple-500/20 rounded-lg overflow-hidden"
                    style={{
                      minHeight: "500px",
                      maxHeight: "70vh",
                      flex: "1 1 auto",
                    }}
                  >
                    <Editor
                      height="100%"
                      width="100%"
                      defaultLanguage={getMonacoLanguage(language)}
                      language={getMonacoLanguage(language)}
                      theme={colorScheme === "dark" ? "vs-dark" : "light"}
                      value={code}
                      onChange={(value) => handleCodeChange(value || "")}
                      onMount={(editor, monaco) => {
                        // Configure language-specific features
                        if (language === "javascript") {
                          // Enable JavaScript-specific features
                          monaco.languages.typescript.javascriptDefaults.setDiagnosticsOptions({
                            noSemanticValidation: false,
                            noSyntaxValidation: false,
                          })
                        }

                        // Configure editor for better autocomplete
                        editor.updateOptions({
                          suggest: {
                            showKeywords: autocompleteEnabled,
                            showSnippets: autocompleteEnabled,
                            showFunctions: autocompleteEnabled,
                            showConstructors: autocompleteEnabled,
                            showFields: autocompleteEnabled,
                            showVariables: autocompleteEnabled,
                            showClasses: autocompleteEnabled,
                            showStructs: autocompleteEnabled,
                            showInterfaces: autocompleteEnabled,
                            showModules: autocompleteEnabled,
                            showProperties: autocompleteEnabled,
                            showEvents: autocompleteEnabled,
                            showOperators: autocompleteEnabled,
                            showUnits: autocompleteEnabled,
                            showValues: autocompleteEnabled,
                            showConstants: autocompleteEnabled,
                            showEnums: autocompleteEnabled,
                            showEnumMembers: autocompleteEnabled,
                            showColors: autocompleteEnabled,
                            showFiles: autocompleteEnabled,
                            showReferences: autocompleteEnabled,
                            showFolders: autocompleteEnabled,
                            showTypeParameters: autocompleteEnabled,
                            showIssues: autocompleteEnabled,
                            showUsers: autocompleteEnabled,
                            showWords: autocompleteEnabled,
                          },
                        })
                      }}
                      options={{
                        // Basic editor settings
                        minimap: { enabled: false },
                        fontSize: 18,
                        wordWrap: "on",
                        automaticLayout: true,
                        scrollBeyondLastLine: false,
                        smoothScrolling: true,
                        lineNumbers: "on",
                        renderLineHighlight: "all",
                        cursorBlinking: "blink",
                        cursorSmoothCaretAnimation: "on",
                        padding: { top: 20, bottom: 20 },
                        folding: true,
                        foldingStrategy: "indentation",
                        showFoldingControls: "always",
                        lineHeight: 1.6,

                        // Syntax and error detection
                        glyphMargin: true,
                        lightbulb: {},
                        codeLens: true,
                        occurrencesHighlight: "singleFile",
                        selectionHighlight: true,
                        bracketPairColorization: { enabled: true },
                        guides: {
                          bracketPairs: true,
                          indentation: true,
                          highlightActiveIndentation: true,
                        },

                        // Error detection and validation
                        // Validation is handled by language services

                        // Autocomplete and suggestions
                        quickSuggestions: autocompleteEnabled
                          ? {
                              other: true,
                              comments: true,
                              strings: true,
                            }
                          : false,
                        suggestOnTriggerCharacters: autocompleteEnabled,
                        acceptSuggestionOnEnter: autocompleteEnabled ? "on" : "off",
                        tabCompletion: autocompleteEnabled ? "on" : "off",
                        wordBasedSuggestions: autocompleteEnabled ? "currentDocument" : "off",

                        // Language-specific autocomplete
                        suggest: {
                          showKeywords: autocompleteEnabled,
                          showSnippets: autocompleteEnabled,
                          showFunctions: autocompleteEnabled,
                          showConstructors: autocompleteEnabled,
                          showFields: autocompleteEnabled,
                          showVariables: autocompleteEnabled,
                          showClasses: autocompleteEnabled,
                          showStructs: autocompleteEnabled,
                          showInterfaces: autocompleteEnabled,
                          showModules: autocompleteEnabled,
                          showProperties: autocompleteEnabled,
                          showEvents: autocompleteEnabled,
                          showOperators: autocompleteEnabled,
                          showUnits: autocompleteEnabled,
                          showValues: autocompleteEnabled,
                          showConstants: autocompleteEnabled,
                          showEnums: autocompleteEnabled,
                          showEnumMembers: autocompleteEnabled,
                          showColors: autocompleteEnabled,
                          showFiles: autocompleteEnabled,
                          showReferences: autocompleteEnabled,
                          showFolders: autocompleteEnabled,
                          showTypeParameters: autocompleteEnabled,
                          showIssues: autocompleteEnabled,
                          showUsers: autocompleteEnabled,
                          showWords: autocompleteEnabled,
                        },

                        // Parameter hints
                        parameterHints: {
                          enabled: autocompleteEnabled,
                          cycle: true,
                        },

                        // Hover information
                        hover: {
                          enabled: true,
                          delay: 300,
                        },

                        // Formatting
                        formatOnPaste: true,
                        formatOnType: true,

                        // Accessibility
                        accessibilitySupport: "auto",

                        // Multi-cursor
                        multiCursorModifier: "ctrlCmd",

                        // Find and replace
                        find: {
                          seedSearchStringFromSelection: "always",
                          autoFindInSelection: "multiline",
                        },
                      }}
                    />
                  </div>

                  {/* Test Results */}
                  {testResults.length > 0 && (
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="mt-6 bg-purple-900/20 rounded-lg p-4 border border-purple-500/30"
                    >
                      <div className="flex items-center justify-between mb-4">
                        <h4 className="text-lg font-semibold text-purple-200 flex items-center">
                          <span className="mr-2">🧪</span>
                          Test Results
                        </h4>
                        <div className="flex items-center space-x-4">
                          <div
                            className={`px-3 py-1 rounded-full text-sm font-medium ${
                              testResults.filter((r) => r.passed).length === testResults.length
                                ? "bg-green-900/30 text-green-300 border border-green-500/30"
                                : "bg-red-900/30 text-red-300 border border-red-500/30"
                            }`}
                          >
                            {testResults.filter((r) => r.passed).length}/{testResults.length} passed
                          </div>
                          <button
                            onClick={() => setExpandedTests(new Set(testResults.map((_, i) => i)))}
                            className="text-xs text-purple-400 hover:text-purple-300 transition-colors"
                          >
                            {expandedTests.size === testResults.length ? "Collapse All" : "Expand All"}
                          </button>
                        </div>
                      </div>
                      <div className="space-y-3">
                        {testResults.map((result, index) => {
                          const isExpanded = expandedTests.has(index)
                          return (
                            <div
                              key={index}
                              className={`p-4 rounded-lg border transition-all duration-200 ${
                                result.passed
                                  ? "bg-green-900/20 border-green-500/30 hover:bg-green-900/30"
                                  : "bg-red-900/20 border-red-500/30 hover:bg-red-900/30"
                              }`}
                            >
                              <div className="flex items-center justify-between mb-3">
                                <button
                                  onClick={() => toggleTestExpansion(index)}
                                  className="font-medium flex items-center space-x-3 hover:opacity-80 transition-opacity group"
                                >
                                  <div className="flex items-center space-x-2">
                                    <span className="text-sm font-medium text-purple-300">Test {index + 1}:</span>
                                    <span
                                      className={`font-semibold ${result.passed ? "text-green-400" : "text-red-400"}`}
                                    >
                                      {result.passed ? "✅ Passed" : "❌ Failed"}
                                    </span>
                                  </div>
                                  <div className="flex items-center space-x-2">
                                    <span className="text-xs text-purple-400">{result.execution_time || 0}ms</span>
                                    <span className="text-lg group-hover:scale-110 transition-transform">
                                      {isExpanded ? "▼" : "▶"}
                                    </span>
                                  </div>
                                </button>
                              </div>

                              {/* Expandable Test Details */}
                              {isExpanded && (
                                <motion.div
                                  initial={{ opacity: 0, height: 0 }}
                                  animate={{ opacity: 1, height: "auto" }}
                                  exit={{ opacity: 0, height: 0 }}
                                  className="space-y-4 mt-4 pt-4 border-t border-purple-500/20"
                                >
                                  {/* Test Case Input */}
                                  <div>
                                    <div className="flex items-center space-x-2 mb-2">
                                      <span className="text-sm font-medium text-purple-300">Input:</span>
                                    </div>
                                    <div className="p-3 bg-black/30 rounded-lg border border-purple-500/20 font-mono text-sm">
                                      {result.input ? (
                                        typeof result.input === "string" ? (
                                          result.input
                                        ) : (
                                          JSON.stringify(result.input, null, 2)
                                        )
                                      ) : (
                                        <span className="text-purple-400 opacity-75">No input data</span>
                                      )}
                                    </div>
                                  </div>

                                  {!result.passed && (
                                    <div className="space-y-4">
                                      {/* Error Message */}
                                      {result.error && (
                                        <div>
                                          <div className="flex items-center space-x-2 mb-2">
                                            <span className="text-sm font-medium text-red-300">Error:</span>
                                          </div>
                                          <div className="p-3 bg-red-900/30 rounded-lg border border-red-500/30 text-red-200 text-sm font-mono">
                                            {typeof result.error === "string"
                                              ? result.error
                                              : JSON.stringify(result.error)}
                                          </div>
                                        </div>
                                      )}

                                      {/* Expected vs Actual Output */}
                                      {!result.error && (
                                        <div className="space-y-4">
                                          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                                            <div>
                                              <div className="flex items-center space-x-2 mb-2">
                                                <span className="text-sm font-medium text-green-300">Expected:</span>
                                              </div>
                                              <div className="p-3 bg-green-900/20 rounded-lg border border-green-500/30 text-green-200 text-sm font-mono">
                                                {typeof result.expected === "string"
                                                  ? result.expected
                                                  : JSON.stringify(result.expected, null, 2)}
                                              </div>
                                            </div>
                                            <div>
                                              <div className="flex items-center space-x-2 mb-2">
                                                <span className="text-sm font-medium text-red-300">Got:</span>
                                              </div>
                                              <div className="p-3 bg-red-900/20 rounded-lg border border-red-500/30 text-red-200 text-sm font-mono">
                                                {typeof result.output === "string"
                                                  ? result.output
                                                  : JSON.stringify(result.output, null, 2)}
                                              </div>
                                            </div>
                                          </div>
                                          
                                          {/* Debug Information */}
                                          {result.debug_info && (
                                            <div className="mt-4 p-4 bg-gray-900/30 rounded-lg border border-gray-500/30">
                                              <div className="flex items-center space-x-2 mb-3">
                                                <span className="text-sm font-medium text-yellow-300">Debug Analysis:</span>
                                              </div>
                                              <div className="space-y-3 text-sm">
                                                <div>
                                                  <span className="text-yellow-300">Status: </span>
                                                  <span className="text-yellow-200">{result.debug_info.status}</span>
                                                </div>
                                                <div>
                                                  <span className="text-yellow-300">Comparison: </span>
                                                  <span className="text-yellow-200">{result.debug_info.comparison?.message}</span>
                                                </div>
                                                {result.debug_info.comparison?.type === "different" && result.debug_info.comparison?.line_analysis?.first_difference && (
                                                  <div className="mt-3 p-3 bg-gray-800/50 rounded border border-gray-600/30">
                                                    <div className="text-yellow-300 mb-2">First Difference at Line {result.debug_info.comparison.line_analysis.first_difference.line_number}:</div>
                                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                                      <div>
                                                        <div className="text-red-300 text-xs mb-1">Your Output:</div>
                                                        <div className="p-2 bg-red-900/20 rounded text-red-200 font-mono text-xs">
                                                          {result.debug_info.comparison.line_analysis.first_difference.actual_line || "No output"}
                                                        </div>
                                                      </div>
                                                      <div>
                                                        <div className="text-green-300 text-xs mb-1">Expected:</div>
                                                        <div className="p-2 bg-green-900/20 rounded text-green-200 font-mono text-xs">
                                                          {result.debug_info.comparison.line_analysis.first_difference.expected_line || "No output"}
                                                        </div>
                                                      </div>
                                                    </div>
                                                  </div>
                                                )}
                                                {result.debug_info.execution_details && (
                                                  <div className="mt-3 p-3 bg-gray-800/50 rounded border border-gray-600/30">
                                                    <div className="text-yellow-300 mb-2">Execution Details:</div>
                                                    <div className="grid grid-cols-2 gap-4 text-xs">
                                                      <div>
                                                        <span className="text-gray-400">Time: </span>
                                                        <span className="text-white">{result.debug_info.execution_details.time}s</span>
                                                      </div>
                                                      <div>
                                                        <span className="text-gray-400">Memory: </span>
                                                        <span className="text-white">{result.debug_info.execution_details.memory}KB</span>
                                                      </div>
                                                      <div>
                                                        <span className="text-gray-400">Exit Code: </span>
                                                        <span className="text-white">{result.debug_info.execution_details.exit_code}</span>
                                                      </div>
                                                      <div>
                                                        <span className="text-gray-400">Wall Time: </span>
                                                        <span className="text-white">{result.debug_info.execution_details.wall_time}s</span>
                                                      </div>
                                                    </div>
                                                  </div>
                                                )}
                                              </div>
                                            </div>
                                          )}
                                        </div>
                                      )}
                                    </div>
                                  )}

                                  {/* Success Message */}
                                  {result.passed && (
                                    <div className="flex items-center space-x-2 p-3 bg-green-900/20 rounded-lg border border-green-500/30">
                                      <span className="text-green-400">✅</span>
                                      <span className="text-green-300 text-sm font-medium">
                                        Output matches expected result
                                      </span>
                                    </div>
                                  )}
                                </motion.div>
                              )}
                            </div>
                          )
                        })}
                      </div>
                    </motion.div>
                  )}
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </PageShell>
  )
}

export default CodingProblemPage
