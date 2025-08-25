"use client"

import { useState } from "react"
import { Link } from "react-router-dom"
import { BookOpen, File, Folder, PlusCircle, Upload } from "react-feather"

const CourseMaterials = ({ user }) => {
  const [activeCourse, setActiveCourse] = useState("Introduction to Computer Science")
  
  const courses = [
    "Introduction to Computer Science",
    "Data Structures and Algorithms",
    "Web Development",
    "Database Systems"
  ]
  
  const materials = [
    { 
      id: 1, 
      name: "Week 1 - Introduction", 
      type: "folder", 
      items: [
        { id: 101, name: "Course Overview.pdf", type: "file", size: "2.4 MB", uploaded: "2023-09-01" },
        { id: 102, name: "Syllabus.pdf", type: "file", size: "1.2 MB", uploaded: "2023-09-01" }
      ]
    },
    {
      id: 2,
      name: "Week 2 - Programming Basics",
      type: "folder",
      items: [
        { id: 201, name: "Variables and Types.pdf", type: "file", size: "3.1 MB", uploaded: "2023-09-08" },
        { id: 202, name: "Control Structures.pdf", type: "file", size: "2.8 MB", uploaded: "2023-09-08" },
        { id: 203, name: "Practice Problems.zip", type: "file", size: "5.6 MB", uploaded: "2023-09-09" }
      ]
    },
    {
      id: 3,
      name: "Week 3 - Functions",
      type: "folder",
      items: [
        { id: 301, name: "Functions Overview.pdf", type: "file", size: "2.2 MB", uploaded: "2023-09-15" },
        { id: 302, name: "Recursion.pdf", type: "file", size: "1.9 MB", uploaded: "2023-09-15" }
      ]
    }
  ]
  
  const [expandedFolders, setExpandedFolders] = useState({})
  
  const toggleFolder = (folderId) => {
    setExpandedFolders(prev => ({
      ...prev,
      [folderId]: !prev[folderId]
    }))
  }
  
  const handleUploadClick = () => {
    alert("Upload functionality would be implemented here")
  }
  
  const handleCreateClick = () => {
    alert("Create new material functionality would be implemented here")
  }
  
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-md">
        <div className="container mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold">EduAssist AI</h1>
              <span className="hidden md:inline-block px-3 py-1 bg-white/20 rounded-full text-sm">
                Course Materials
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
        <div className="bg-white rounded-xl shadow-md overflow-hidden">
          <div className="p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold text-gray-800">Course Materials</h2>
              <div className="flex space-x-2">
                <button 
                  className="flex items-center px-3 py-2 bg-purple-600 text-white rounded-md text-sm font-medium hover:bg-purple-700 transition-colors"
                  onClick={handleUploadClick}
                >
                  <Upload className="h-4 w-4 mr-2" />
                  Upload Material
                </button>
                <button 
                  className="flex items-center px-3 py-2 bg-indigo-600 text-white rounded-md text-sm font-medium hover:bg-indigo-700 transition-colors"
                  onClick={handleCreateClick}
                >
                  <PlusCircle className="h-4 w-4 mr-2" />
                  Create New
                </button>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="md:col-span-1 bg-gray-50 p-4 rounded-lg">
                <h3 className="font-medium text-gray-700 mb-3">My Courses</h3>
                <ul className="space-y-2">
                  {courses.map((course, index) => (
                    <li key={index}>
                      <button
                        className={`w-full text-left px-3 py-2 rounded-lg ${
                          activeCourse === course 
                            ? "bg-purple-100 text-purple-700 font-medium" 
                            : "text-gray-600 hover:bg-gray-200"
                        }`}
                        onClick={() => setActiveCourse(course)}
                      >
                        <div className="flex items-center">
                          <BookOpen className="h-4 w-4 mr-2" />
                          <span className="truncate">{course}</span>
                        </div>
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
              
              <div className="md:col-span-3">
                <h3 className="font-medium text-gray-700 mb-3">{activeCourse}</h3>
                <div className="border border-gray-200 rounded-lg overflow-hidden">
                  <div className="bg-gray-50 px-4 py-2 border-b border-gray-200">
                    <div className="grid grid-cols-12 text-sm font-medium text-gray-500">
                      <div className="col-span-6">Name</div>
                      <div className="col-span-2">Size</div>
                      <div className="col-span-3">Uploaded</div>
                      <div className="col-span-1">Actions</div>
                    </div>
                  </div>
                  
                  <div className="divide-y divide-gray-200">
                    {materials.map((material) => (
                      <div key={material.id}>
                        <div 
                          className="px-4 py-3 hover:bg-gray-50 cursor-pointer"
                          onClick={() => toggleFolder(material.id)}
                        >
                          <div className="grid grid-cols-12">
                            <div className="col-span-6 flex items-center">
                              <Folder className="h-5 w-5 text-amber-500 mr-2" />
                              <span className="font-medium text-gray-700">{material.name}</span>
                            </div>
                            <div className="col-span-2">—</div>
                            <div className="col-span-3">—</div>
                            <div className="col-span-1 text-right">
                              <button className="text-gray-400 hover:text-gray-600">
                                ⋮
                              </button>
                            </div>
                          </div>
                        </div>
                        
                        {expandedFolders[material.id] && material.items && (
                          <div className="bg-gray-50 pl-8">
                            {material.items.map((item) => (
                              <div key={item.id} className="px-4 py-2 hover:bg-gray-100">
                                <div className="grid grid-cols-12">
                                  <div className="col-span-6 flex items-center">
                                    <File className="h-4 w-4 text-indigo-400 mr-2" />
                                    <span className="text-gray-700">{item.name}</span>
                                  </div>
                                  <div className="col-span-2 text-gray-500 text-sm">{item.size}</div>
                                  <div className="col-span-3 text-gray-500 text-sm">{item.uploaded}</div>
                                  <div className="col-span-1 text-right">
                                    <button className="text-gray-400 hover:text-gray-600">
                                      ⋮
                                    </button>
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default CourseMaterials
