"use client"

import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import Chatbot from "../../components/Chatbot"
import { useBackend } from "../../contexts/BackendContext"

const MCQAssessment = () => {
  const navigate = useNavigate()
  const { makeApiCall, isOnline } = useBackend()

  const [questions, setQuestions] = useState([])
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [answers, setAnswers] = useState({})
  const [timeLeft, setTimeLeft] = useState(1800)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [showSetup, setShowSetup] = useState(true)
  
  // MCQ Setup Form
  const [mcqSetup, setMcqSetup] = useState({
    topic: 'Science',
    difficulty: 'easy',
    numberOfQuestions: 8
  })

  const difficulties = [
    { value: 'very_easy', label: 'Very Easy' },
    { value: 'easy', label: 'Easy' },
    { value: 'medium', label: 'Medium' },
    { value: 'hard', label: 'Hard' },
    { value: 'very_hard', label: 'Very Hard' }
  ]

  const handleSetupSubmit = async () => {
    const topicToUse = (mcqSetup.topic || '').trim() || 'General Knowledge'

    try {
      setLoading(true)
      setError(null)
      
      if (!isOnline) {
        throw new Error("Backend is offline. Please check your connection.")
      }

      const data = await makeApiCall('/getQuestions', {
        method: "POST",
        body: JSON.stringify({
          Topic: topicToUse,
          Type: "MCQ",
          Quantity: mcqSetup.numberOfQuestions,
          Difficulty: mcqSetup.difficulty
        })
      })

      const list = (data && (data.Questions || data.questions)) || []
      const formatted = list.map((q, idx) => {
        const optionsRaw = q.Options ?? q.options ?? []
        const options = Array.isArray(optionsRaw) ? optionsRaw : Object.values(optionsRaw || {})
        const questionText = q.Question ?? q.question ?? q.prompt ?? ''
        let answerRaw = q.Answer ?? q.answer
        let correctIndex = -1
        if (typeof answerRaw === 'number') {
          correctIndex = answerRaw
        } else if (typeof answerRaw === 'string') {
          const parsed = parseInt(answerRaw, 10)
          if (!Number.isNaN(parsed)) correctIndex = parsed
          else {
            const lowered = answerRaw.trim().toLowerCase()
            correctIndex = Math.max(0, options.findIndex(o => (o || '').toString().trim().toLowerCase() === lowered))
          }
        }
        if (correctIndex < 0) correctIndex = 0
        return {
          id: idx,
          Question: questionText,
          Options: options,
          correctAnswer: correctIndex,
          explanation: q.explanation ?? q.Explanation ?? ''
        }
      })

      if (formatted.length === 0) {
        throw new Error("No questions received from the server.")
      }

      setQuestions(formatted)
      setShowSetup(false)
      setLoading(false)
    } catch (error) {
      console.error("Error fetching questions:", error)
      setError(error.message || "Failed to fetch questions")
      setLoading(false)
    }
  }

  useEffect(() => {
    if (loading || showSetup) return

    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          clearInterval(timer)
          handleSubmit()
          return 0
        }
        return prev - 1
      })
    }, 1000)

    return () => clearInterval(timer)
  }, [loading, showSetup])

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs < 10 ? "0" : ""}${secs}`
  }

  const handleAnswerSelect = (qIndex, optionIndex) => {
    setAnswers((prev) => ({ ...prev, [qIndex]: optionIndex }))
  }

  const handleNext = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1)
    }
  }

  const handlePrev = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1)
    }
  }

  const handleSubmit = async () => {
    if (isSubmitting || loading) return
    setIsSubmitting(true)
  
    let correct = 0
    const scoreList = []
    const questionAnalysis = []
  
    questions.forEach((q, index) => {
      const isCorrect = answers[index] === q.correctAnswer
      if (isCorrect) correct++
      scoreList.push(isCorrect ? 1 : 0)
      
      questionAnalysis.push({
        question: q.Question,
        userAnswer: q.Options[answers[index] || 0],
        correctAnswer: q.Options[q.correctAnswer],
        isCorrect,
        explanation: q.explanation
      })
    })

    // Get AI feedback
    try {
      const feedbackData = await makeApiCall('/getQuizFeedback', {
        method: "POST",
        body: JSON.stringify({
          Questions: questionAnalysis,
          Score: scoreList
        })
      })

      // Save to leaderboard
      try {
        await makeApiCall('/results/mcq', {
          method: 'POST',
          body: JSON.stringify({
            user_id: 'student',
            user_name: 'Student',
            topic: mcqSetup.topic,
            difficulty: mcqSetup.difficulty,
            score: correct,
            total: questions.length,
            duration_ms: (1800 - timeLeft) * 1000
          })
        })
      } catch {}

      setTimeout(() => {
        navigate("/student/results", {
          state: {
            score: correct,
            total: questions.length,
            answers: answers,
            scoreList,
            questions: questionAnalysis,
            type: "mcq",
            feedback: feedbackData,
            topic: mcqSetup.topic,
            difficulty: mcqSetup.difficulty
          }
        })
      }, 1500)
    } catch (error) {
      console.error("Error getting feedback:", error)
      // Navigate without feedback if API fails
      setTimeout(() => {
        navigate("/student/results", {
          state: {
            score: correct,
            total: questions.length,
            answers: answers,
            scoreList,
            questions: questionAnalysis,
            type: "mcq",
            subject: mcqSetup.subject,
            topic: mcqSetup.topic,
            difficulty: mcqSetup.difficulty
          }
        })
      }, 1500)
    }
  }

  if (showSetup) {
    return (
      <div className="relative min-h-screen bg-gradient-to-br from-[#0e0a12] via-[#160f1c] to-[#221628] flex items-center justify-center p-4 text-white">
        <div className="relative w-full max-w-3xl bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-8 shadow-2xl">
          <h1 className="text-2xl font-semibold mb-6">MCQ Assessments</h1>

          {/* Topic */}
          <div className="mb-6">
            <label className="block text-sm text-white/80 mb-2">Topic</label>
            <input
              type="text"
              value={mcqSetup.topic}
              onChange={(e) => setMcqSetup({ ...mcqSetup, topic: e.target.value })}
              placeholder="e.g., Science, Operating Systems, Algebra"
              className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-orange-500/50"
            />
          </div>

          {/* Number slider */}
          <div className="mb-6">
            <div className="flex items-center justify-between text-sm text-white/80 mb-2">
              <span>Number of Questions</span>
              <span>{mcqSetup.numberOfQuestions} questions</span>
            </div>
            <input
              type="range"
              min={1}
              max={50}
              value={mcqSetup.numberOfQuestions}
              onChange={(e) => setMcqSetup({ ...mcqSetup, numberOfQuestions: Number(e.target.value) })}
              className="w-full accent-orange-500"
            />
            <div className="flex justify-between text-xs text-white/50 mt-1">
              <span>1</span>
              <span>50</span>
            </div>
          </div>

          {/* Difficulty */}
          <div className="mb-8">
            <label className="block text-sm text-white/80 mb-3">Difficulty Level</label>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {difficulties.map((d) => (
                <button
                  key={d.value}
                  onClick={() => setMcqSetup({ ...mcqSetup, difficulty: d.value })}
                  className={`px-6 py-4 rounded-xl border transition-all ${
                    mcqSetup.difficulty === d.value
                      ? 'bg-gradient-to-r from-orange-500 to-purple-600 border-transparent shadow-lg'
                      : 'bg-white/5 border-white/10 hover:bg-white/10'
                  }`}
                >
                  {d.label}
                </button>
              ))}
            </div>
          </div>

          {error && (
            <div className="p-3 bg-red-500/10 text-red-300 border border-red-500/30 rounded-lg mb-4 text-sm">{error}</div>
          )}

          <button
            onClick={handleSetupSubmit}
            disabled={loading}
            className="w-full py-4 rounded-xl text-white font-medium bg-gradient-to-r from-orange-500 to-purple-600 hover:opacity-95 disabled:opacity-50"
          >
            {loading ? 'Generating Questions...' : 'Start Assessment'}
          </button>
        </div>
      </div>
    )
  }
  
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#0e0a12] via-[#160f1c] to-[#221628] flex items-center justify-center text-white">
        <div className="text-center">
          <div className="text-xl font-semibold mb-2">Loading Questions...</div>
          <div className="text-white/60">Please wait while we generate your assessment</div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#0e0a12] via-[#160f1c] to-[#221628] flex items-center justify-center text-white">
        <div className="text-center max-w-md mx-auto p-6 bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl">
          <div className="text-red-400 text-xl font-semibold mb-4">Error Loading Questions</div>
          <div className="text-white/60 mb-6">{error}</div>
          <button 
            onClick={() => setShowSetup(true)} 
            className="bg-gradient-to-r from-orange-500 to-purple-600 text-white px-6 py-3 rounded-xl hover:opacity-90 transition-all"
          >
            Try Again
          </button>
        </div>
      </div>
    )
  }

  if (questions.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#0e0a12] via-[#160f1c] to-[#221628] flex items-center justify-center text-white">
        <div className="text-center max-w-md mx-auto p-6 bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl">
          <div className="text-white/80 text-xl font-semibold mb-4">No Questions Available</div>
          <div className="text-white/60 mb-6">No questions were generated. Please try again.</div>
          <button 
            onClick={() => setShowSetup(true)} 
            className="bg-gradient-to-r from-orange-500 to-purple-600 text-white px-6 py-3 rounded-xl hover:opacity-90 transition-all"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  const current = questions[currentQuestion]
  const progress = ((currentQuestion + 1) / questions.length) * 100

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-[#0e0a12] via-[#160f1c] to-[#221628] text-white">
      <header className="bg-white/5 backdrop-blur-md border-b border-white/10 px-6 py-4 flex justify-between items-center">
        <div>
          <h1 className="text-xl font-bold text-white">MCQ Assessment</h1>
          <div className="text-sm text-white/60">{mcqSetup.topic} • {mcqSetup.difficulty.replace('_',' ').replace(/^./, c => c.toUpperCase())}</div>
        </div>
        <div className="flex items-center gap-4">
          <div className={`px-3 py-2 rounded-lg text-sm font-medium ${
            timeLeft < 300 
              ? "bg-red-500/20 text-red-300 border border-red-500/30" 
              : "bg-white/10 text-white border border-white/20"
          }`}>
            ⏳ Time Left: {formatTime(timeLeft)}
          </div>
          <button
            onClick={handleSubmit}
            disabled={isSubmitting}
            className="bg-gradient-to-r from-orange-500 to-purple-600 text-white px-6 py-2 rounded-lg hover:opacity-90 disabled:opacity-50 transition-all"
          >
            {isSubmitting ? "Submitting..." : "Submit"}
          </button>
        </div>
      </header>

      <div className="h-1 bg-white/10">
        <div className="h-1 bg-gradient-to-r from-orange-500 to-purple-600 transition-all duration-300" style={{ width: `${progress}%` }} />
      </div>

      <main className="flex-1 overflow-y-auto p-6">
        <div className="max-w-2xl mx-auto bg-white/5 backdrop-blur-md border border-white/10 p-8 rounded-2xl shadow-2xl">
          <h2 className="text-lg font-semibold mb-6 text-white">
            Question {currentQuestion + 1} of {questions.length}
          </h2>
          <p className="text-white/90 whitespace-pre-wrap mb-8 text-lg leading-relaxed">{current.Question}</p>

          <div className="space-y-4 mb-8">
            {current.Options.map((opt, i) => (
              <div
                key={i}
                onClick={() => handleAnswerSelect(currentQuestion, i)}
                className={`p-4 border rounded-xl cursor-pointer transition-all ${
                  answers[currentQuestion] === i
                    ? "bg-gradient-to-r from-orange-500/20 to-purple-600/20 border-orange-500/50 shadow-lg"
                    : "bg-white/5 border-white/10 hover:bg-white/10 hover:border-white/20"
                }`}
              >
                <span className="font-medium text-orange-400 mr-3">{String.fromCharCode(65 + i)}.</span> 
                <span className="text-white/90">{opt}</span>
              </div>
            ))}
          </div>

          <div className="flex justify-between">
            <button
              onClick={handlePrev}
              disabled={currentQuestion === 0}
              className="px-6 py-3 bg-white/10 border border-white/20 rounded-lg hover:bg-white/20 disabled:opacity-50 disabled:cursor-not-allowed transition-all text-white"
            >
              Previous
            </button>
            <button
              onClick={handleNext}
              disabled={currentQuestion === questions.length - 1}
              className="px-6 py-3 bg-gradient-to-r from-orange-500 to-purple-600 text-white rounded-lg hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              Next
            </button>
          </div>
        </div>
      </main>

      <Chatbot />
    </div>
  )
}

export default MCQAssessment
