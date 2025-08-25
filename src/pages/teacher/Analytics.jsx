"use client"

import { useState } from "react"
import { Link } from "react-router-dom"
import { BarChart2, TrendingUp, Users, Award, Download } from "react-feather"

const Analytics = ({ user }) => {
  const [selectedTimeframe, setSelectedTimeframe] = useState("semester")
  const [selectedCourse, setSelectedCourse] = useState("all")
  
  const courses = [
    { id: "all", name: "All Courses" },
    { id: "cs101", name: "Introduction to Computer Science" },
    { id: "ds201", name: "Data Structures and Algorithms" },
    { id: "web301", name: "Web Development" },
    { id: "db401", name: "Database Systems" }
  ]
  
  // Mock data
  const overviewStats = [
    { id: 1, title: "Average Grade", value: "82%", trend: "+3%", color: "purple" },
    { id: 2, title: "Submission Rate", value: "94%", trend: "+5%", color: "emerald" },
    { id: 3, title: "Active Students", value: "118", trend: "+2", color: "blue" },
    { id: 4, title: "Top Performers", value: "35", trend: "30%", color: "amber" }
  ]
  
  const gradeDistribution = [
    { range: "90-100", count: 22, label: "A" },
    { range: "80-89", count: 38, label: "B" },
    { range: "70-79", count: 45, label: "C" },
    { range: "60-69", count: 12, label: "D" },
    { range: "0-59", count: 3, label: "F" }
  ]
  
  const assignmentPerformance = [
    { name: "Assignment 1", avgScore: 85 },
    { name: "Assignment 2", avgScore: 78 },
    { name: "Assignment 3", avgScore: 82 },
    { name: "Midterm Exam", avgScore: 76 },
    { name: "Assignment 4", avgScore: 88 },
    { name: "Assignment 5", avgScore: 90 }
  ]
  
  const topicMastery = [
    { name: "Data Structures", mastery: 85 },
    { name: "Algorithms", mastery: 72 },
    { name: "Programming Fundamentals", mastery: 92 },
    { name: "Database Design", mastery: 68 },
    { name: "Web Technologies", mastery: 78 }
  ]
  
  // Helper functions
  const renderBarChart = (data, valueKey, labelKey) => {
    const max = Math.max(...data.map(item => item[valueKey]))
    
    return (
      <div className="space-y-3">
        {data.map((item, index) => (
          <div key={index} className="flex items-center">
            <div className="w-32 text-sm text-gray-600">{item[labelKey]}</div>
            <div className="flex-1">
              <div className="h-7 bg-gray-100 rounded-lg overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-purple-500 to-indigo-600 rounded-lg"
                  style={{ width: `${(item[valueKey] / max) * 100}%` }}
                ></div>
              </div>
            </div>
            <div className="w-16 text-right text-sm text-gray-800 font-medium">
              {typeof item[valueKey] === 'number' && valueKey === 'mastery' ? `${item[valueKey]}%` : item[valueKey]}
            </div>
          </div>
        ))}
      </div>
    )
  }
  
  const handleExportData = () => {
    alert("This would export analytics data as CSV/Excel")
  }
  
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-md">
        <div className="container mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold">EduAssist AI</h1>
              <span className="hidden md:inline-block px-3 py-1 bg-white/20 rounded-full text-sm">
                Analytics
              </span>
            </div>
            <div className="flex items-center">
              <Link to="/teacher/dashboard" className="text-white hover:text-purple-200">
                Back to Dashboard
              </Link>
            </div>
          </div>
        </div>
      </header>
      
      <main className="container mx-auto px-4 py-8">
        <div className="mb-6 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <h2 className="text-2xl font-bold text-gray-800">Student Performance Analytics</h2>
          
          <div className="flex flex-wrap gap-2">
            <select
              className="px-3 py-2 border border-gray-300 rounded-md text-sm"
              value={selectedCourse}
              onChange={(e) => setSelectedCourse(e.target.value)}
            >
              {courses.map(course => (
                <option key={course.id} value={course.id}>{course.name}</option>
              ))}
            </select>
            
            <select
              className="px-3 py-2 border border-gray-300 rounded-md text-sm"
              value={selectedTimeframe}
              onChange={(e) => setSelectedTimeframe(e.target.value)}
            >
              <option value="semester">Current Semester</option>
              <option value="year">Academic Year</option>
              <option value="custom">Custom Range</option>
            </select>
            
            <button 
              className="flex items-center px-3 py-2 bg-gray-800 text-white rounded-md text-sm font-medium hover:bg-gray-700 transition-colors"
              onClick={handleExportData}
            >
              <Download className="h-4 w-4 mr-2" />
              Export Data
            </button>
          </div>
        </div>
        
        {/* Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          {overviewStats.map(stat => (
            <div key={stat.id} className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
              <div className="flex justify-between items-center mb-4">
                <div className={`p-2 rounded-lg bg-${stat.color}-100`}>
                  {stat.id === 1 && <BarChart2 className={`h-6 w-6 text-${stat.color}-600`} />}
                  {stat.id === 2 && <TrendingUp className={`h-6 w-6 text-${stat.color}-600`} />}
                  {stat.id === 3 && <Users className={`h-6 w-6 text-${stat.color}-600`} />}
                  {stat.id === 4 && <Award className={`h-6 w-6 text-${stat.color}-600`} />}
                </div>
                <div className={`text-sm font-medium ${stat.trend.startsWith('+') ? 'text-green-600' : 'text-red-600'}`}>
                  {stat.trend}
                </div>
              </div>
              <h3 className="text-gray-500 text-sm">{stat.title}</h3>
              <p className="text-3xl font-bold text-gray-800 mt-1">{stat.value}</p>
            </div>
          ))}
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Grade Distribution */}
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Grade Distribution</h3>
            {renderBarChart(gradeDistribution, 'count', 'range')}
          </div>
          
          {/* Assignment Performance */}
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Assignment Performance</h3>
            {renderBarChart(assignmentPerformance, 'avgScore', 'name')}
          </div>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Topic Mastery */}
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Topic Mastery</h3>
            {renderBarChart(topicMastery, 'mastery', 'name')}
          </div>
          
          {/* Improvement Suggestions */}
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">AI-Generated Insights</h3>
            <div className="space-y-4">
              <div className="p-4 bg-purple-50 rounded-lg border border-purple-100">
                <h4 className="font-medium text-purple-800 mb-1">Performance Trend</h4>
                <p className="text-gray-700 text-sm">
                  Class average has improved by 3% over the semester. Top performing areas include Programming Fundamentals and Data Structures.
                </p>
              </div>
              
              <div className="p-4 bg-amber-50 rounded-lg border border-amber-100">
                <h4 className="font-medium text-amber-800 mb-1">Areas Needing Attention</h4>
                <p className="text-gray-700 text-sm">
                  Students are struggling with Database Design concepts. Consider providing additional resources or review sessions.
                </p>
              </div>
              
              <div className="p-4 bg-emerald-50 rounded-lg border border-emerald-100">
                <h4 className="font-medium text-emerald-800 mb-1">Engagement Metrics</h4>
                <p className="text-gray-700 text-sm">
                  Assignment submission rates are high at 94%. Student participation in online discussions has increased by 12%.
                </p>
              </div>
              
              <button className="w-full mt-2 py-2 bg-indigo-100 text-indigo-800 rounded-lg text-sm font-medium hover:bg-indigo-200 transition-colors">
                Generate Comprehensive Report
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default Analytics
