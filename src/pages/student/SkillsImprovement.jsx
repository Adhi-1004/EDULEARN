"use client"

import { useState } from "react"
import { Link } from "react-router-dom"
import Sidebar from "../../components/Sidebar"
import Header from "../../components/Header"
import Chatbot from "../../components/Chatbot"

const SkillsImprovement = ({ user, onLogout }) => {
  const [activeTab, setActiveTab] = useState("improvement")

  // Mock data
  const skillsToImprove = [
    {
      id: 1,
      name: "Data Structures",
      description: "Improve your understanding of advanced data structures like trees, graphs, and hash tables.",
      level: "Intermediate",
      progress: 65,
      resources: [
        { type: "video", title: "Data Structures Crash Course", url: "https://www.youtube.com/watch?v=DuDz6B4cqVc" },
        {
          type: "course",
          title: "Advanced Data Structures",
          url: "https://www.coursera.org/learn/advanced-data-structures",
        },
        {
          type: "article",
          title: "Understanding Time Complexity",
          url: "https://www.freecodecamp.org/news/time-complexity-explained/",
        },
      ],
    },
    {
      id: 2,
      name: "Algorithm Design",
      description: "Learn how to design efficient algorithms for solving complex problems.",
      level: "Advanced",
      progress: 40,
      resources: [
        { type: "video", title: "Algorithm Design Techniques", url: "https://www.youtube.com/watch?v=0JUN9aDxVmI" },
        {
          type: "course",
          title: "Algorithms Specialization",
          url: "https://www.coursera.org/specializations/algorithms",
        },
        {
          type: "article",
          title: "Dynamic Programming for Beginners",
          url: "https://www.freecodecamp.org/news/demystifying-dynamic-programming-3efafb8d4296/",
        },
      ],
    },
    {
      id: 3,
      name: "Database Design",
      description: "Improve your skills in designing efficient and scalable database schemas.",
      level: "Intermediate",
      progress: 30,
      resources: [
        { type: "video", title: "Database Design Course", url: "https://www.youtube.com/watch?v=ztHopE5Wnpc" },
        {
          type: "course",
          title: "Database Systems Concepts & Design",
          url: "https://www.udacity.com/course/database-systems-concepts-design--ud150",
        },
        {
          type: "article",
          title: "Normalization in Database Design",
          url: "https://www.guru99.com/database-normalization.html",
        },
      ],
    },
  ]

  const trendingSkills = [
    {
      id: 1,
      name: "Machine Learning",
      description: "Learn the fundamentals of machine learning algorithms and their applications.",
      level: "Beginner to Advanced",
      resources: [
        { type: "video", title: "Machine Learning Crash Course", url: "https://www.youtube.com/watch?v=GwIo3gDZCVQ" },
        {
          type: "course",
          title: "Machine Learning by Stanford",
          url: "https://www.coursera.org/learn/machine-learning",
        },
        {
          type: "article",
          title: "Introduction to Machine Learning",
          url: "https://www.freecodecamp.org/news/machine-learning-for-beginners/",
        },
      ],
    },
    {
      id: 2,
      name: "Cloud Computing",
      description: "Develop skills in cloud platforms like AWS, Azure, and Google Cloud.",
      level: "Intermediate",
      resources: [
        {
          type: "video",
          title: "AWS Certified Cloud Practitioner",
          url: "https://www.youtube.com/watch?v=3hLmDS179YE",
        },
        {
          type: "course",
          title: "Cloud Computing Specialization",
          url: "https://www.coursera.org/specializations/cloud-computing",
        },
        {
          type: "article",
          title: "Getting Started with Cloud Computing",
          url: "https://www.freecodecamp.org/news/get-started-with-cloud-computing/",
        },
      ],
    },
    {
      id: 3,
      name: "DevOps",
      description: "Learn about CI/CD pipelines, containerization, and infrastructure as code.",
      level: "Intermediate to Advanced",
      resources: [
        { type: "video", title: "DevOps Crash Course", url: "https://www.youtube.com/watch?v=OXE2a8dqIAI" },
        {
          type: "course",
          title: "DevOps on AWS Specialization",
          url: "https://www.coursera.org/specializations/aws-devops",
        },
        {
          type: "article",
          title: "DevOps for Beginners",
          url: "https://www.freecodecamp.org/news/devops-for-beginners/",
        },
      ],
    },
  ]

  const practiceProblems = [
    {
      id: 1,
      title: "Two Sum",
      difficulty: "Easy",
      platform: "LeetCode",
      url: "https://leetcode.com/problems/two-sum/",
      tags: ["Array", "Hash Table"],
    },
    {
      id: 2,
      title: "Valid Parentheses",
      difficulty: "Easy",
      platform: "LeetCode",
      url: "https://leetcode.com/problems/valid-parentheses/",
      tags: ["Stack", "String"],
    },
    {
      id: 3,
      title: "Merge Two Sorted Lists",
      difficulty: "Easy",
      platform: "LeetCode",
      url: "https://leetcode.com/problems/merge-two-sorted-lists/",
      tags: ["Linked List", "Recursion"],
    },
    {
      id: 4,
      title: "Maximum Subarray",
      difficulty: "Medium",
      platform: "LeetCode",
      url: "https://leetcode.com/problems/maximum-subarray/",
      tags: ["Array", "Divide and Conquer", "Dynamic Programming"],
    },
    {
      id: 5,
      title: "Binary Tree Level Order Traversal",
      difficulty: "Medium",
      platform: "LeetCode",
      url: "https://leetcode.com/problems/binary-tree-level-order-traversal/",
      tags: ["Tree", "BFS", "Binary Tree"],
    },
    {
      id: 6,
      title: "Watermelon",
      difficulty: "Easy",
      platform: "Codeforces",
      url: "https://codeforces.com/problemset/problem/4/A",
      tags: ["Math", "Brute Force"],
    },
  ]

  const renderContent = () => {
    switch (activeTab) {
      case "improvement":
        return (
          <div className="space-y-8">
            <h2 className="text-xl font-semibold text-gray-900">Skills to Improve</h2>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {skillsToImprove.map((skill) => (
                <div key={skill.id} className="bg-white rounded-xl shadow-md overflow-hidden">
                  <div className="p-6">
                    <div className="flex justify-between items-start mb-4">
                      <h3 className="text-lg font-semibold text-gray-900">{skill.name}</h3>
                      <span className="px-2 py-1 text-xs rounded-full bg-indigo-100 text-indigo-800">
                        {skill.level}
                      </span>
                    </div>

                    <p className="text-gray-600 mb-4">{skill.description}</p>

                    <div className="mb-4">
                      <div className="flex justify-between items-center mb-1">
                        <span className="text-sm text-gray-500">Progress</span>
                        <span className="text-sm font-medium text-indigo-600">{skill.progress}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div className="bg-indigo-600 h-2 rounded-full" style={{ width: `${skill.progress}%` }}></div>
                      </div>
                    </div>

                    <div className="space-y-2">
                      <h4 className="text-sm font-medium text-gray-900">Learning Resources</h4>
                      {skill.resources.map((resource, index) => (
                        <a
                          key={index}
                          href={resource.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center text-sm text-indigo-600 hover:text-indigo-800"
                        >
                          {resource.type === "video" && (
                            <svg
                              xmlns="http://www.w3.org/2000/svg"
                              className="h-4 w-4 mr-2"
                              fill="none"
                              viewBox="0 0 24 24"
                              stroke="currentColor"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
                              />
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                              />
                            </svg>
                          )}
                          {resource.type === "course" && (
                            <svg
                              xmlns="http://www.w3.org/2000/svg"
                              className="h-4 w-4 mr-2"
                              fill="none"
                              viewBox="0 0 24 24"
                              stroke="currentColor"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
                              />
                            </svg>
                          )}
                          {resource.type === "article" && (
                            <svg
                              xmlns="http://www.w3.org/2000/svg"
                              className="h-4 w-4 mr-2"
                              fill="none"
                              viewBox="0 0 24 24"
                              stroke="currentColor"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z"
                              />
                            </svg>
                          )}
                          {resource.title}
                        </a>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <h2 className="text-xl font-semibold text-gray-900 mt-12">Trending Skills</h2>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {trendingSkills.map((skill) => (
                <div key={skill.id} className="bg-white rounded-xl shadow-md overflow-hidden">
                  <div className="p-6">
                    <div className="flex justify-between items-start mb-4">
                      <h3 className="text-lg font-semibold text-gray-900">{skill.name}</h3>
                      <span className="px-2 py-1 text-xs rounded-full bg-pink-100 text-pink-800">Trending</span>
                    </div>

                    <p className="text-gray-600 mb-4">{skill.description}</p>

                    <div className="mb-4">
                      <span className="text-sm text-gray-500">Level: {skill.level}</span>
                    </div>

                    <div className="space-y-2">
                      <h4 className="text-sm font-medium text-gray-900">Learning Resources</h4>
                      {skill.resources.map((resource, index) => (
                        <a
                          key={index}
                          href={resource.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center text-sm text-indigo-600 hover:text-indigo-800"
                        >
                          {resource.type === "video" && (
                            <svg
                              xmlns="http://www.w3.org/2000/svg"
                              className="h-4 w-4 mr-2"
                              fill="none"
                              viewBox="0 0 24 24"
                              stroke="currentColor"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
                              />
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                              />
                            </svg>
                          )}
                          {resource.type === "course" && (
                            <svg
                              xmlns="http://www.w3.org/2000/svg"
                              className="h-4 w-4 mr-2"
                              fill="none"
                              viewBox="0 0 24 24"
                              stroke="currentColor"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
                              />
                            </svg>
                          )}
                          {resource.type === "article" && (
                            <svg
                              xmlns="http://www.w3.org/2000/svg"
                              className="h-4 w-4 mr-2"
                              fill="none"
                              viewBox="0 0 24 24"
                              stroke="currentColor"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z"
                              />
                            </svg>
                          )}
                          {resource.title}
                        </a>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )

      case "practice":
        return (
          <div className="space-y-8">
            <h2 className="text-xl font-semibold text-gray-900">Practice Problems</h2>

            <div className="bg-white rounded-xl shadow-md overflow-hidden">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th
                        scope="col"
                        className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                      >
                        Problem
                      </th>
                      <th
                        scope="col"
                        className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                      >
                        Difficulty
                      </th>
                      <th
                        scope="col"
                        className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                      >
                        Platform
                      </th>
                      <th
                        scope="col"
                        className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                      >
                        Tags
                      </th>
                      <th
                        scope="col"
                        className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider"
                      >
                        Action
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {practiceProblems.map((problem) => (
                      <tr key={problem.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">{problem.title}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span
                            className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                              problem.difficulty === "Easy"
                                ? "bg-green-100 text-green-800"
                                : problem.difficulty === "Medium"
                                  ? "bg-yellow-100 text-yellow-800"
                                  : "bg-red-100 text-red-800"
                            }`}
                          >
                            {problem.difficulty}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">{problem.platform}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex flex-wrap gap-1">
                            {problem.tags.map((tag, index) => (
                              <span key={index} className="px-2 py-1 text-xs bg-gray-100 text-gray-800 rounded-full">
                                {tag}
                              </span>
                            ))}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <a
                            href={problem.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-indigo-600 hover:text-indigo-900"
                          >
                            Solve
                          </a>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )

      default:
        return null
    }
  }

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar user={user} onLogout={onLogout} />

      <div className="flex-1 flex flex-col overflow-hidden">
        <Header user={user} onLogout={onLogout} />

        <main className="flex-1 overflow-y-auto p-6">
          <div className="max-w-6xl mx-auto">
            {/* Header */}
            <div className="bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 rounded-xl p-6 mb-8 text-white">
              <div className="flex flex-col md:flex-row justify-between items-center">
                <div>
                  <h1 className="text-2xl font-bold mb-2">Skills Improvement</h1>
                  <p className="text-white/80">Enhance your skills and stay ahead with personalized recommendations.</p>
                </div>
                <div className="mt-4 md:mt-0">
                  <Link
                    to="/student/dashboard"
                    className="inline-flex items-center px-4 py-2 bg-white text-indigo-600 rounded-lg font-medium hover:bg-opacity-90 transition-colors"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      className="h-5 w-5 mr-2"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                    </svg>
                    Back to Dashboard
                  </Link>
                </div>
              </div>
            </div>

            {/* Tabs */}
            <div className="mb-6 border-b border-gray-200">
              <nav className="flex space-x-8">
                <button
                  onClick={() => setActiveTab("improvement")}
                  className={`py-4 px-1 text-sm font-medium border-b-2 ${
                    activeTab === "improvement"
                      ? "border-indigo-600 text-indigo-600"
                      : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                  }`}
                >
                  Skills Improvement
                </button>

                <button
                  onClick={() => setActiveTab("practice")}
                  className={`py-4 px-1 text-sm font-medium border-b-2 ${
                    activeTab === "practice"
                      ? "border-indigo-600 text-indigo-600"
                      : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                  }`}
                >
                  Practice Problems
                </button>
              </nav>
            </div>

            {/* Content */}
            {renderContent()}
          </div>
        </main>
      </div>

      <Chatbot />
    </div>
  )
}

export default SkillsImprovement
