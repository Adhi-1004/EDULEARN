"use client"

import { useState, useRef, useEffect } from "react"
import { MessageSquare, X, Send } from "react-feather"

const Chatbot = ({ isOpen, toggleChatbot }) => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hello! I'm your AI teaching assistant. How can I help you today?",
      sender: "bot",
    },
  ])
  const [inputValue, setInputValue] = useState("")
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, isOpen])

  const handleInputChange = (e) => {
    setInputValue(e.target.value)
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!inputValue.trim()) return

    // Add user message
    const userMessage = {
      id: messages.length + 1,
      text: inputValue,
      sender: "user",
    }
    setMessages([...messages, userMessage])
    setInputValue("")

    // Simulate AI response
    setTimeout(() => {
      const botResponses = {
        hello: "Hi there! How can I assist you with your teaching today?",
        help: "I can help you with grading assignments, generating feedback, analyzing student performance, and creating lesson plans. What would you like assistance with?",
        feedback:
          "I can help you generate personalized feedback for your students. Would you like me to analyze recent submissions?",
        grade:
          "I can assist with grading assignments. Would you like me to show you the AI-graded assignments that need your review?",
        improvement:
          "Based on the current data, I recommend focusing on Algorithm Complexity with Section A. Would you like me to generate a detailed improvement plan?",
        plan: "I'll create a comprehensive improvement plan for the weak areas identified in the current section. This will include targeted exercises, additional resources, and personalized learning paths for struggling students.",
      }

      // Check for keywords in the user's message
      const userMessageLower = inputValue.toLowerCase()
      let botReply =
        "I'm not sure how to help with that. Could you try asking about feedback, grading, or improvement plans?"

      for (const [keyword, response] of Object.entries(botResponses)) {
        if (userMessageLower.includes(keyword)) {
          botReply = response
          break
        }
      }

      const botMessage = {
        id: messages.length + 2,
        text: botReply,
        sender: "bot",
      }
      setMessages((prevMessages) => [...prevMessages, botMessage])
    }, 1000)
  }

  return (
    <>
      {/* Chatbot Button */}
      <div className="fixed bottom-6 right-6 z-10">
        <button
          className="w-14 h-14 rounded-full bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-lg flex items-center justify-center hover:from-purple-700 hover:to-indigo-700 transition-all"
          onClick={toggleChatbot}
        >
          <MessageSquare className="h-6 w-6" />
        </button>
      </div>

      {/* Chatbot Panel */}
      {isOpen && (
        <div className="fixed bottom-24 right-6 w-80 md:w-96 bg-white rounded-xl shadow-xl z-10 overflow-hidden flex flex-col border border-gray-200">
          <div className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white p-4 flex justify-between items-center">
            <h3 className="font-bold">AI Teaching Assistant</h3>
            <button className="text-white hover:bg-white/10 rounded-full p-1" onClick={toggleChatbot}>
              <X className="h-5 w-5" />
            </button>
          </div>

          <div className="flex-1 p-4 overflow-y-auto max-h-96">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`mb-4 flex ${message.sender === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-3/4 rounded-lg px-4 py-2 ${
                    message.sender === "user" ? "bg-purple-600 text-white" : "bg-gray-100 text-gray-800"
                  }`}
                >
                  {message.text}
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>

          <form onSubmit={handleSubmit} className="border-t border-gray-200 p-4 flex">
            <input
              type="text"
              value={inputValue}
              onChange={handleInputChange}
              placeholder="Type your message..."
              className="flex-1 border border-gray-300 rounded-l-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-purple-600 focus:border-transparent"
            />
            <button
              type="submit"
              className="bg-purple-600 text-white rounded-r-lg px-4 py-2 hover:bg-purple-700 transition-colors"
            >
              <Send className="h-5 w-5" />
            </button>
          </form>
        </div>
      )}
    </>
  )
}

export default Chatbot
