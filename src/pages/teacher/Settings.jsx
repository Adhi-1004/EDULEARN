"use client"

import { useState } from "react"
import { Link } from "react-router-dom"
import { Settings as SettingsIcon, User, Bell, Lock, Shield, Monitor, Save } from "react-feather"

const Settings = ({ user }) => {
  const [activeTab, setActiveTab] = useState("profile")
  const [formData, setFormData] = useState({
    // Profile settings
    name: "Dr. Sarah Johnson",
    email: "sarah.johnson@university.edu",
    phone: "+1 (555) 123-4567",
    department: "Computer Science",
    bio: "Professor of Computer Science with 10+ years of experience teaching data structures, algorithms, and web development.",
    
    // Notification settings
    emailNotifications: true,
    assignmentReminders: true,
    studentMessages: true,
    systemUpdates: false,
    
    // Privacy settings
    showEmail: false,
    showPhone: false,
    
    // AI Assistant settings
    enableAIGrading: true,
    enableAIFeedback: true,
    enableAIAnalytics: true,
    shareDataForImprovement: true,
    
    // Display settings
    theme: "light",
    fontSize: "medium",
    highContrast: false,
    reducedMotion: false
  })
  
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }
  
  const handleSaveSettings = () => {
    alert("Settings would be saved to the backend")
  }
  
  const renderProfileSettings = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
          <input 
            type="text" 
            name="name"
            value={formData.name}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Email Address</label>
          <input 
            type="email" 
            name="email"
            value={formData.email}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Phone Number</label>
          <input 
            type="tel" 
            name="phone"
            value={formData.phone}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Department</label>
          <input 
            type="text" 
            name="department"
            value={formData.department}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
          />
        </div>
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Professional Bio</label>
        <textarea 
          name="bio"
          value={formData.bio}
          onChange={handleChange}
          rows="4"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
        ></textarea>
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Profile Photo</label>
        <div className="flex items-center space-x-4">
          <img 
            src="/placeholder.svg?height=80&width=80" 
            alt="Profile" 
            className="h-20 w-20 rounded-full border border-gray-300"
          />
          <button className="px-4 py-2 bg-gray-100 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-200">
            Change Photo
          </button>
        </div>
      </div>
    </div>
  )
  
  const renderNotificationSettings = () => (
    <div className="space-y-6">
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-sm font-medium text-gray-900">Email Notifications</h4>
            <p className="text-sm text-gray-500">Receive email notifications for important updates</p>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input 
              type="checkbox" 
              name="emailNotifications"
              checked={formData.emailNotifications}
              onChange={handleChange}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
          </label>
        </div>
        
        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-sm font-medium text-gray-900">Assignment Reminders</h4>
            <p className="text-sm text-gray-500">Get reminders about upcoming assignment deadlines</p>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input 
              type="checkbox" 
              name="assignmentReminders"
              checked={formData.assignmentReminders}
              onChange={handleChange}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
          </label>
        </div>
        
        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-sm font-medium text-gray-900">Student Messages</h4>
            <p className="text-sm text-gray-500">Get notified when students send you messages</p>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input 
              type="checkbox" 
              name="studentMessages"
              checked={formData.studentMessages}
              onChange={handleChange}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
          </label>
        </div>
        
        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-sm font-medium text-gray-900">System Updates</h4>
            <p className="text-sm text-gray-500">Receive notifications about system updates and maintenance</p>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input 
              type="checkbox" 
              name="systemUpdates"
              checked={formData.systemUpdates}
              onChange={handleChange}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
          </label>
        </div>
      </div>
    </div>
  )
  
  const renderPrivacySettings = () => (
    <div className="space-y-6">
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-sm font-medium text-gray-900">Show Email to Students</h4>
            <p className="text-sm text-gray-500">Make your email address visible to enrolled students</p>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input 
              type="checkbox" 
              name="showEmail"
              checked={formData.showEmail}
              onChange={handleChange}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
          </label>
        </div>
        
        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-sm font-medium text-gray-900">Show Phone Number</h4>
            <p className="text-sm text-gray-500">Make your phone number visible to enrolled students</p>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input 
              type="checkbox" 
              name="showPhone"
              checked={formData.showPhone}
              onChange={handleChange}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
          </label>
        </div>
      </div>
      
      <div className="p-4 bg-yellow-50 border border-yellow-100 rounded-lg">
        <h4 className="text-sm font-medium text-yellow-800 mb-1">Privacy Notice</h4>
        <p className="text-sm text-yellow-700">
          Your privacy is important. Information you choose to share will only be visible to students enrolled in your courses.
        </p>
      </div>
    </div>
  )
  
  const renderAISettings = () => (
    <div className="space-y-6">
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-sm font-medium text-gray-900">AI-Assisted Grading</h4>
            <p className="text-sm text-gray-500">Use AI to help grade assignments and provide initial feedback</p>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input 
              type="checkbox" 
              name="enableAIGrading"
              checked={formData.enableAIGrading}
              onChange={handleChange}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
          </label>
        </div>
        
        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-sm font-medium text-gray-900">AI-Generated Feedback</h4>
            <p className="text-sm text-gray-500">Allow AI to generate detailed feedback on student submissions</p>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input 
              type="checkbox" 
              name="enableAIFeedback"
              checked={formData.enableAIFeedback}
              onChange={handleChange}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
          </label>
        </div>
        
        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-sm font-medium text-gray-900">AI Analytics</h4>
            <p className="text-sm text-gray-500">Use AI to analyze student performance and identify improvement areas</p>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input 
              type="checkbox" 
              name="enableAIAnalytics"
              checked={formData.enableAIAnalytics}
              onChange={handleChange}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
          </label>
        </div>
        
        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-sm font-medium text-gray-900">Data Sharing for AI Improvement</h4>
            <p className="text-sm text-gray-500">Share anonymized data to help improve AI capabilities</p>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input 
              type="checkbox" 
              name="shareDataForImprovement"
              checked={formData.shareDataForImprovement}
              onChange={handleChange}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
          </label>
        </div>
      </div>
      
      <div className="p-4 bg-blue-50 border border-blue-100 rounded-lg">
        <h4 className="text-sm font-medium text-blue-800 mb-1">AI Assistant Information</h4>
        <p className="text-sm text-blue-700">
          All AI-generated content is provided as a suggestion and can be reviewed and modified before being shared with students.
        </p>
      </div>
    </div>
  )
  
  const renderDisplaySettings = () => (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Theme</label>
        <select 
          name="theme" 
          value={formData.theme}
          onChange={handleChange}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
        >
          <option value="light">Light</option>
          <option value="dark">Dark</option>
          <option value="system">System Default</option>
        </select>
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Font Size</label>
        <select 
          name="fontSize" 
          value={formData.fontSize}
          onChange={handleChange}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
        >
          <option value="small">Small</option>
          <option value="medium">Medium</option>
          <option value="large">Large</option>
        </select>
      </div>
      
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-sm font-medium text-gray-900">High Contrast Mode</h4>
            <p className="text-sm text-gray-500">Increase contrast for better readability</p>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input 
              type="checkbox" 
              name="highContrast"
              checked={formData.highContrast}
              onChange={handleChange}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
          </label>
        </div>
        
        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-sm font-medium text-gray-900">Reduced Motion</h4>
            <p className="text-sm text-gray-500">Minimize animations throughout the interface</p>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input 
              type="checkbox" 
              name="reducedMotion"
              checked={formData.reducedMotion}
              onChange={handleChange}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
          </label>
        </div>
      </div>
    </div>
  )
  
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-md">
        <div className="container mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold">EduAssist AI</h1>
              <span className="hidden md:inline-block px-3 py-1 bg-white/20 rounded-full text-sm">
                Settings
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
              <h2 className="text-xl font-bold text-gray-800">Account Settings</h2>
              <button 
                className="flex items-center px-4 py-2 bg-purple-600 text-white rounded-md font-medium hover:bg-purple-700 transition-colors"
                onClick={handleSaveSettings}
              >
                <Save className="h-4 w-4 mr-2" />
                Save Changes
              </button>
            </div>
            
            <div className="flex flex-col md:flex-row gap-6">
              <div className="md:w-1/4">
                <nav className="space-y-1">
                  <button
                    className={`w-full flex items-center px-4 py-3 rounded-lg text-left ${
                      activeTab === "profile" 
                        ? "bg-purple-50 text-purple-700 font-medium"
                        : "text-gray-700 hover:bg-gray-50"
                    }`}
                    onClick={() => setActiveTab("profile")}
                  >
                    <User className={`h-5 w-5 mr-3 ${activeTab === "profile" ? "text-purple-500" : "text-gray-400"}`} />
                    <span>Profile Information</span>
                  </button>
                  
                  <button
                    className={`w-full flex items-center px-4 py-3 rounded-lg text-left ${
                      activeTab === "notifications" 
                        ? "bg-purple-50 text-purple-700 font-medium"
                        : "text-gray-700 hover:bg-gray-50"
                    }`}
                    onClick={() => setActiveTab("notifications")}
                  >
                    <Bell className={`h-5 w-5 mr-3 ${activeTab === "notifications" ? "text-purple-500" : "text-gray-400"}`} />
                    <span>Notifications</span>
                  </button>
                  
                  <button
                    className={`w-full flex items-center px-4 py-3 rounded-lg text-left ${
                      activeTab === "privacy" 
                        ? "bg-purple-50 text-purple-700 font-medium"
                        : "text-gray-700 hover:bg-gray-50"
                    }`}
                    onClick={() => setActiveTab("privacy")}
                  >
                    <Lock className={`h-5 w-5 mr-3 ${activeTab === "privacy" ? "text-purple-500" : "text-gray-400"}`} />
                    <span>Privacy</span>
                  </button>
                  
                  <button
                    className={`w-full flex items-center px-4 py-3 rounded-lg text-left ${
                      activeTab === "ai" 
                        ? "bg-purple-50 text-purple-700 font-medium"
                        : "text-gray-700 hover:bg-gray-50"
                    }`}
                    onClick={() => setActiveTab("ai")}
                  >
                    <Shield className={`h-5 w-5 mr-3 ${activeTab === "ai" ? "text-purple-500" : "text-gray-400"}`} />
                    <span>AI Assistant</span>
                  </button>
                  
                  <button
                    className={`w-full flex items-center px-4 py-3 rounded-lg text-left ${
                      activeTab === "display" 
                        ? "bg-purple-50 text-purple-700 font-medium"
                        : "text-gray-700 hover:bg-gray-50"
                    }`}
                    onClick={() => setActiveTab("display")}
                  >
                    <Monitor className={`h-5 w-5 mr-3 ${activeTab === "display" ? "text-purple-500" : "text-gray-400"}`} />
                    <span>Display</span>
                  </button>
                </nav>
              </div>
              
              <div className="md:w-3/4 bg-gray-50 p-6 rounded-lg">
                <div className="flex items-center mb-4">
                  <SettingsIcon className="h-6 w-6 text-purple-600 mr-2" />
                  <h3 className="text-lg font-semibold text-gray-800">
                    {activeTab === "profile" && "Profile Information"}
                    {activeTab === "notifications" && "Notification Preferences"}
                    {activeTab === "privacy" && "Privacy Settings"}
                    {activeTab === "ai" && "AI Assistant Settings"}
                    {activeTab === "display" && "Display Settings"}
                  </h3>
                </div>
                
                {activeTab === "profile" && renderProfileSettings()}
                {activeTab === "notifications" && renderNotificationSettings()}
                {activeTab === "privacy" && renderPrivacySettings()}
                {activeTab === "ai" && renderAISettings()}
                {activeTab === "display" && renderDisplaySettings()}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default Settings
