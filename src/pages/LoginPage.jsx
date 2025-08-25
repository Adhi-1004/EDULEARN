"use client"

import { useState } from "react"
import { Link, useNavigate } from "react-router-dom"

const LoginPage = ({ onLogin }) => {
  const [userType, setUserType] = useState("student")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const [isLoading, setIsLoading] = useState(false)

  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError("")
    setIsLoading(true)

    try {
      await new Promise((resolve) => setTimeout(resolve, 800))
      if (!email || !password) throw new Error("Please enter both email and password")

      const userData = {
        id: Math.random().toString(36).slice(2),
        name: userType === "student" ? "Student User" : "Teacher User",
        email,
        role: userType,
      }
      onLogin(userData)
      navigate(`/${userType}/dashboard`)
    } catch (err) {
      setError(err.message || "Failed to login. Please try again.")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-violet-500 via-fuchsia-500 to-indigo-500 flex items-center justify-center p-6">
      <div className="w-full max-w-md">
        <div className="rounded-2xl p-[2px] bg-gradient-to-br from-violet-400 via-fuchsia-400 to-indigo-400 shadow-[0_10px_40px_rgba(0,0,0,0.2)]">
          <div className="rounded-2xl bg-white p-8">
            {/* Brand */}
            <div className="mb-8 text-center">
              <Link to="/" className="inline-flex items-center justify-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-7 w-7 text-indigo-600" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M10.394 2.08a1 1 0 00-.788 0l-7 3a1 1 0 000 1.84L5.25 8.051a.999.999 0 01.356-.257l4-1.714a1 1 0 11.788 1.838L7.667 9.088l1.94.831a1 1 0 00.787 0l7-3a1 1 0 000-1.838l-7-3z" />
                </svg>
                <span className="text-xl font-bold text-indigo-600">EduGrade AI</span>
              </Link>
              <h1 className="mt-6 text-2xl font-bold text-gray-900">Welcome back</h1>
              <p className="mt-1 text-gray-600">Sign in to your account</p>
            </div>

            {error && <div className="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-600">{error}</div>}

            {/* Role toggle */}
            <div className="mb-6 grid grid-cols-2 gap-0 rounded-lg border border-gray-200">
              <button
                type="button"
                className={`py-3 text-center text-sm font-semibold ${userType === "student" ? "bg-indigo-600 text-white" : "bg-white text-gray-700 hover:bg-gray-50"}`}
                onClick={() => setUserType("student")}
              >
                Student
              </button>
              <button
                type="button"
                className={`py-3 text-center text-sm font-semibold ${userType === "teacher" ? "bg-indigo-600 text-white" : "bg-white text-gray-700 hover:bg-gray-50"}`}
                onClick={() => setUserType("teacher")}
              >
                Teacher
              </button>
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label htmlFor="email" className="mb-1 block text-sm font-medium text-gray-700">Email</label>
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-gray-900 placeholder:text-gray-400 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  placeholder="Enter your email"
                  required
                />
              </div>
              <div>
                <div className="mb-1 flex items-center justify-between">
                  <label htmlFor="password" className="block text-sm font-medium text-gray-700">Password</label>
                  <a href="#" className="text-sm font-medium text-indigo-600 hover:text-indigo-700">Forgot password?</a>
                </div>
                <input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-gray-900 placeholder:text-gray-400 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  placeholder="Enter your password"
                  required
                />
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full rounded-lg bg-indigo-600 py-2.5 font-semibold text-white transition-colors hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {isLoading ? (
                  <span className="flex items-center justify-center">
                    <svg className="-ml-1 mr-2 h-4 w-4 animate-spin text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Signing in...
                  </span>
                ) : (
                  "Sign in"
                )}
              </button>
            </form>

            <div className="mt-6 text-center text-sm text-gray-600">
              Don't have an account?{" "}
              <Link to="/register" className="font-semibold text-indigo-600 hover:text-indigo-700">Sign up</Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default LoginPage
