"use client"

import { useLocation, useNavigate } from "react-router-dom"
import Chatbot from "../../components/Chatbot"
import { CheckCircle, XCircle, TrendingUp, Lightbulb, BookOpen, Target, Clock } from "lucide-react"

const ResultsPage = ({ user, onLogout }) => {
  const location = useLocation()
  const navigate = useNavigate()

  const { 
    score, 
    total, 
    answers, 
    questions, 
    scoreList, 
    type, 
    feedback, 
    subject, 
    topic, 
    difficulty 
  } = location.state || {}

  const percentage = Math.round((score / total) * 100)

  const getGrade = (percentage) => {
    if (percentage >= 90) return { grade: "A+", color: "text-green-600", bgColor: "bg-green-100", borderColor: "border-green-200" }
    if (percentage >= 80) return { grade: "A", color: "text-green-600", bgColor: "bg-green-100", borderColor: "border-green-200" }
    if (percentage >= 70) return { grade: "B", color: "text-blue-600", bgColor: "bg-blue-100", borderColor: "border-blue-200" }
    if (percentage >= 60) return { grade: "C", color: "text-yellow-600", bgColor: "bg-yellow-100", borderColor: "border-yellow-200" }
    if (percentage >= 50) return { grade: "D", color: "text-orange-600", bgColor: "bg-orange-100", borderColor: "border-orange-200" }
    return { grade: "F", color: "text-red-600", bgColor: "bg-red-100", borderColor: "border-red-200" }
  }

  const { grade, color, bgColor, borderColor } = getGrade(percentage)

  const getPerformanceMessage = (percentage) => {
    if (percentage >= 90) return "Excellent! You've mastered this topic."
    if (percentage >= 80) return "Great job! You have a solid understanding."
    if (percentage >= 70) return "Good work! You're on the right track."
    if (percentage >= 60) return "Not bad! Keep practicing to improve."
    if (percentage >= 50) return "You need more practice with this topic."
    return "This topic needs more attention. Don't give up!"
  }

  const renderMCQResults = () => (
    <div className="space-y-8">
      {/* Score Summary */}
      <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl shadow-2xl overflow-hidden">
        <div className="p-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-white mb-2">Assessment Results</h1>
            <p className="text-white/60">
              {subject} • {topic} • {difficulty?.charAt(0).toUpperCase() + difficulty?.slice(1)} Level
              </p>
            </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="text-center">
              <div className="text-4xl font-bold text-white mb-2">{score}</div>
              <div className="text-sm text-white/60">Correct Answers</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-white mb-2">{total}</div>
              <div className="text-sm text-white/60">Total Questions</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-orange-400 mb-2">{percentage}%</div>
              <div className="text-sm text-white/60">Score</div>
            </div>
            <div className="text-center">
              <div className={`text-4xl font-bold ${color} mb-2`}>{grade}</div>
              <div className="text-sm text-white/60">Grade</div>
            </div>
          </div>

          <div className="w-full bg-white/10 rounded-full h-3 mb-6">
            <div
              className={`h-3 rounded-full transition-all duration-1000 ${
                percentage >= 90 ? "bg-gradient-to-r from-green-500 to-green-400" : 
                percentage >= 80 ? "bg-gradient-to-r from-green-400 to-blue-400" : 
                percentage >= 70 ? "bg-gradient-to-r from-blue-500 to-purple-500" : 
                percentage >= 60 ? "bg-gradient-to-r from-yellow-500 to-orange-500" : 
                percentage >= 50 ? "bg-gradient-to-r from-orange-500 to-red-500" : "bg-gradient-to-r from-red-500 to-red-600"
              }`}
              style={{ width: `${percentage}%` }}
            ></div>
          </div>

          <div className="text-center">
            <p className="text-lg text-white/80 mb-6">{getPerformanceMessage(percentage)}</p>
            <button
              onClick={() => navigate("/student/dashboard")}
              className="px-8 py-4 bg-gradient-to-r from-orange-500 to-purple-600 text-white rounded-xl font-medium hover:opacity-90 transition-all shadow-2xl"
            >
              Return to Dashboard
            </button>
          </div>
        </div>
      </div>

      {/* AI Feedback and Suggestions */}
      {feedback && (
        <div className="bg-gradient-to-r from-orange-500/10 to-purple-600/10 rounded-2xl shadow-2xl border border-orange-500/20">
          <div className="p-6">
            <div className="flex items-center mb-6">
              <div className="w-12 h-12 bg-gradient-to-r from-orange-500 to-purple-600 rounded-xl flex items-center justify-center mr-4">
                <Lightbulb className="h-6 w-6 text-white" />
              </div>
              <h2 className="text-xl font-semibold text-white">AI Analysis & Recommendations</h2>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-white/5 backdrop-blur-md rounded-xl p-4 border border-white/10">
                <h3 className="font-semibold text-white mb-3 flex items-center">
                  <TrendingUp className="h-4 w-4 mr-2 text-orange-400" />
                  Performance Summary
                </h3>
                <p className="text-white/80 text-sm">{feedback.score_summary || "You completed the assessment successfully."}</p>
              </div>
              
              <div className="bg-white/5 backdrop-blur-md rounded-xl p-4 border border-white/10">
                <h3 className="font-semibold text-white mb-3 flex items-center">
                  <Target className="h-4 w-4 mr-2 text-green-400" />
                  Areas for Improvement
                </h3>
                <p className="text-white/80 text-sm">{feedback.weak_topics_summary || "Focus on strengthening your understanding of the core concepts."}</p>
              </div>
            </div>

            {feedback.suggestions && feedback.suggestions.length > 0 && (
              <div className="mt-6 bg-white/5 backdrop-blur-md rounded-xl p-4 border border-white/10">
                <h3 className="font-semibold text-white mb-3 flex items-center">
                  <BookOpen className="h-4 w-4 mr-2 text-purple-400" />
                  Study Recommendations
                </h3>
                <ul className="space-y-2">
                  {feedback.suggestions.map((suggestion, index) => (
                    <li key={index} className="flex items-start">
                      <div className="w-2 h-2 bg-purple-400 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                      <span className="text-white/80 text-sm">{suggestion}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Detailed Question Analysis */}
      <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl shadow-2xl overflow-hidden">
        <div className="p-6">
          <h2 className="text-xl font-semibold text-white mb-6 flex items-center">
            <Clock className="h-5 w-5 mr-2 text-white/60" />
            Detailed Question Analysis
          </h2>

          <div className="space-y-6">
            {questions?.map((question, index) => {
              const isCorrect = question.isCorrect
              const userAnswer = question.userAnswer
              const correctAnswer = question.correctAnswer

              return (
                <div key={index} className={`border-2 rounded-xl p-6 transition-all ${
                  isCorrect 
                    ? 'border-green-500/30 bg-green-500/5' 
                    : 'border-red-500/30 bg-red-500/5'
                }`}>
                  <div className="flex items-start mb-4">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center mr-4 flex-shrink-0 ${
                        isCorrect ? "bg-green-500/20 text-green-400" : "bg-red-500/20 text-red-400"
                    }`}>
                      {isCorrect ? (
                        <CheckCircle className="h-5 w-5" />
                      ) : (
                        <XCircle className="h-5 w-5" />
                      )}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center mb-2">
                        <span className="text-sm font-medium text-white/60 mr-3">Question {index + 1}</span>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          isCorrect 
                            ? 'bg-green-500/20 text-green-400 border border-green-500/30' 
                            : 'bg-red-500/20 text-red-400 border border-red-500/30'
                        }`}>
                          {isCorrect ? 'Correct' : 'Incorrect'}
                        </span>
                      </div>
                      <p className="font-medium text-white mb-3">{question.question}</p>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                        <div className="bg-white/5 backdrop-blur-md rounded-lg p-3 border border-white/10">
                          <div className="text-xs font-medium text-white/60 mb-1">Your Answer</div>
                          <div className={`font-medium ${
                            isCorrect ? 'text-green-400' : 'text-red-400'
                          }`}>
                            {userAnswer || "Not answered"}
                          </div>
                        </div>
                        <div className="bg-white/5 backdrop-blur-md rounded-lg p-3 border border-white/10">
                          <div className="text-xs font-medium text-white/60 mb-1">Correct Answer</div>
                          <div className="font-medium text-green-400">{correctAnswer}</div>
                        </div>
                      </div>

                      {question.explanation && (
                        <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-3">
                          <div className="text-xs font-medium text-blue-400 mb-1">Explanation</div>
                          <p className="text-blue-300 text-sm">{question.explanation}</p>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>

      {/* Study Plan */}
      <div className="bg-gradient-to-r from-green-500/10 to-blue-500/10 rounded-2xl shadow-2xl border border-green-500/20">
        <div className="p-6">
          <h2 className="text-xl font-semibold text-white mb-4 flex items-center">
            <Target className="h-5 w-5 mr-2 text-green-400" />
            Personalized Study Plan
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white/5 backdrop-blur-md rounded-xl p-4 border border-white/10">
              <h3 className="font-semibold text-white mb-2">Immediate Actions</h3>
              <ul className="space-y-2 text-sm text-white/80">
                <li>• Review incorrect answers</li>
                <li>• Read explanations carefully</li>
                <li>• Identify weak areas</li>
              </ul>
            </div>
            
            <div className="bg-white/5 backdrop-blur-md rounded-xl p-4 border border-white/10">
              <h3 className="font-semibold text-white mb-2">This Week</h3>
              <ul className="space-y-2 text-sm text-white/80">
                <li>• Practice similar questions</li>
                <li>• Study related concepts</li>
                <li>• Take practice tests</li>
              </ul>
            </div>
            
            <div className="bg-white/5 backdrop-blur-md rounded-xl p-4 border border-white/10">
              <h3 className="font-semibold text-white mb-2">Long Term</h3>
              <ul className="space-y-2 text-sm text-white/80">
                <li>• Build strong foundation</li>
                <li>• Regular practice sessions</li>
                <li>• Track progress</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  )

  return (
    <div className="flex flex-col min-h-screen bg-gradient-to-br from-[#0e0a12] via-[#160f1c] to-[#221628]">
      <div className="flex-1">
        <main className="max-w-6xl mx-auto p-6">
          {type === "mcq" && renderMCQResults()}
        </main>
        <Chatbot />
      </div>
    </div>
  )
}

export default ResultsPage
