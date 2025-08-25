"use client"

import { useState } from "react"
import { Link } from "react-router-dom"
import { Mail, Phone, MapPin, Book, Award, Edit, ArrowLeft } from "react-feather"

const TeacherProfile = ({ user }) => {
  const [isEditing, setIsEditing] = useState(false)
  const [profileData, setProfileData] = useState({
    name: user?.name || "Dr. Sarah Johnson",
    email: user?.email || "sarah.johnson@university.edu",
    phone: "+1 (555) 123-4567",
    address: "Computer Science Department, University of Technology",
    bio: "Professor of Computer Science with 15 years of experience in teaching and research. Specializing in Artificial Intelligence, Machine Learning, and Data Structures.",
    education: [
      { id: 1, degree: "Ph.D. in Computer Science", institution: "Stanford University", year: "2008" },
      { id: 2, degree: "M.S. in Computer Science", institution: "MIT", year: "2004" },
      { id: 3, degree: "B.S. in Computer Engineering", institution: "UC Berkeley", year: "2002" },
    ],
    courses: [
      { id: 1, code: "CS101", name: "Introduction to Programming", students: 45 },
      { id: 2, code: "CS202", name: "Data Structures and Algorithms", students: 38 },
      { id: 3, code: "CS350", name: "Artificial Intelligence", students: 25 },
      { id: 4, code: "CS405", name: "Machine Learning", students: 12 },
    ],
  })

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setProfileData({
      ...profileData,
      [name]: value,
    })
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    setIsEditing(false)
    // Here you would typically save the data to your backend
    alert("Profile updated successfully!")
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-md">
        <div className="container mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-4">
              <Link to="/teacher/dashboard" className="flex items-center space-x-2">
                <ArrowLeft className="h-5 w-5" />
                <span>Back to Dashboard</span>
              </Link>
            </div>
            <h1 className="text-2xl font-bold">Teacher Profile</h1>
            <div className="w-24"></div> {/* Spacer for centering */}
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-xl shadow-md overflow-hidden mb-6">
            <div className="p-6 bg-gradient-to-r from-purple-600 to-indigo-600 text-white relative">
              <button
                className="absolute top-4 right-4 bg-white/20 p-2 rounded-full hover:bg-white/30 transition-colors"
                onClick={() => setIsEditing(!isEditing)}
              >
                <Edit className="h-5 w-5" />
              </button>

              <div className="flex flex-col md:flex-row items-center md:items-start space-y-4 md:space-y-0 md:space-x-6">
                <img
                  src={user?.avatar || "/placeholder.svg?height=120&width=120"}
                  alt="Profile"
                  className="h-32 w-32 rounded-full border-4 border-white/30"
                />

                {isEditing ? (
                  <form onSubmit={handleSubmit} className="flex-1">
                    <div className="mb-4">
                      <label className="block text-white/80 text-sm mb-1">Full Name</label>
                      <input
                        type="text"
                        name="name"
                        value={profileData.name}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-md text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-white/50"
                      />
                    </div>

                    <div className="mb-4">
                      <label className="block text-white/80 text-sm mb-1">Email</label>
                      <input
                        type="email"
                        name="email"
                        value={profileData.email}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-md text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-white/50"
                      />
                    </div>

                    <div className="flex space-x-2">
                      <button
                        type="submit"
                        className="px-4 py-2 bg-white text-purple-600 rounded-md font-medium hover:bg-white/90 transition-colors"
                      >
                        Save Changes
                      </button>
                      <button
                        type="button"
                        onClick={() => setIsEditing(false)}
                        className="px-4 py-2 bg-white/20 text-white rounded-md font-medium hover:bg-white/30 transition-colors"
                      >
                        Cancel
                      </button>
                    </div>
                  </form>
                ) : (
                  <div className="flex-1">
                    <h2 className="text-3xl font-bold">{profileData.name}</h2>
                    <p className="text-xl text-purple-100">Professor of Computer Science</p>

                    <div className="mt-4 space-y-2">
                      <div className="flex items-center space-x-2">
                        <Mail className="h-5 w-5 text-purple-200" />
                        <span>{profileData.email}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Phone className="h-5 w-5 text-purple-200" />
                        <span>{profileData.phone}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <MapPin className="h-5 w-5 text-purple-200" />
                        <span>{profileData.address}</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>

            <div className="p-6">
              <h3 className="text-xl font-semibold text-gray-800 mb-4">Biography</h3>
              {isEditing ? (
                <textarea
                  name="bio"
                  value={profileData.bio}
                  onChange={handleInputChange}
                  rows="4"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-600 focus:border-transparent"
                ></textarea>
              ) : (
                <p className="text-gray-600">{profileData.bio}</p>
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white rounded-xl shadow-md overflow-hidden">
              <div className="p-6">
                <div className="flex items-center space-x-2 mb-4">
                  <Book className="h-5 w-5 text-purple-600" />
                  <h3 className="text-xl font-semibold text-gray-800">Current Courses</h3>
                </div>

                <div className="space-y-4">
                  {profileData.courses.map((course) => (
                    <div key={course.id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex justify-between items-start">
                        <div>
                          <h4 className="font-medium text-gray-800">{course.name}</h4>
                          <p className="text-sm text-gray-500">Course Code: {course.code}</p>
                        </div>
                        <span className="bg-purple-100 text-purple-800 text-xs font-medium px-2.5 py-0.5 rounded-full">
                          {course.students} Students
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-md overflow-hidden">
              <div className="p-6">
                <div className="flex items-center space-x-2 mb-4">
                  <Award className="h-5 w-5 text-purple-600" />
                  <h3 className="text-xl font-semibold text-gray-800">Education</h3>
                </div>

                <div className="space-y-4">
                  {profileData.education.map((edu) => (
                    <div key={edu.id} className="border border-gray-200 rounded-lg p-4">
                      <h4 className="font-medium text-gray-800">{edu.degree}</h4>
                      <p className="text-sm text-gray-500">
                        {edu.institution}, {edu.year}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default TeacherProfile
