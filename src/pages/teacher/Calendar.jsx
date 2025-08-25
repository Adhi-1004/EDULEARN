"use client"

import { useState } from "react"
import { Link } from "react-router-dom"
import { Calendar as CalendarIcon, ChevronLeft, ChevronRight, Plus, Edit2, Trash2 } from "react-feather"

const Calendar = ({ user }) => {
  const [currentMonth, setCurrentMonth] = useState(new Date())
  const [selectedDate, setSelectedDate] = useState(new Date())
  const [showEventModal, setShowEventModal] = useState(false)
  
  // Mock data
  const events = [
    { 
      id: 1, 
      title: "Lecture: Data Structures", 
      date: new Date(2023, 5, 12), 
      startTime: "10:00 AM", 
      endTime: "11:30 AM",
      type: "lecture",
      location: "Room 301"
    },
    { 
      id: 2, 
      title: "Office Hours", 
      date: new Date(2023, 5, 12), 
      startTime: "2:00 PM", 
      endTime: "4:00 PM",
      type: "office-hours",
      location: "Office 210"
    },
    { 
      id: 3, 
      title: "Assignment Due: Algorithm Analysis", 
      date: new Date(2023, 5, 15), 
      type: "deadline"
    },
    { 
      id: 4, 
      title: "Department Meeting", 
      date: new Date(2023, 5, 18), 
      startTime: "1:00 PM", 
      endTime: "2:30 PM",
      type: "meeting",
      location: "Conference Room B"
    },
    { 
      id: 5, 
      title: "Midterm Exam", 
      date: new Date(2023, 5, 22), 
      startTime: "9:00 AM", 
      endTime: "11:00 AM",
      type: "exam",
      location: "Main Hall"
    }
  ]
  
  const daysInMonth = (date) => {
    return new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate()
  }
  
  const firstDayOfMonth = (date) => {
    return new Date(date.getFullYear(), date.getMonth(), 1).getDay()
  }
  
  const getMonthName = (date) => {
    return date.toLocaleString('default', { month: 'long' })
  }
  
  const getPrevMonth = () => {
    return new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1)
  }
  
  const getNextMonth = () => {
    return new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1)
  }
  
  const handlePrevMonth = () => {
    setCurrentMonth(getPrevMonth())
  }
  
  const handleNextMonth = () => {
    setCurrentMonth(getNextMonth())
  }
  
  const handleDateClick = (day) => {
    const newDate = new Date(currentMonth.getFullYear(), currentMonth.getMonth(), day)
    setSelectedDate(newDate)
  }
  
  const handleNewEvent = () => {
    setShowEventModal(true)
  }
  
  const handleCloseModal = () => {
    setShowEventModal(false)
  }
  
  const getEventsForDate = (date) => {
    return events.filter(event => 
      event.date.getDate() === date.getDate() && 
      event.date.getMonth() === date.getMonth() && 
      event.date.getFullYear() === date.getFullYear()
    )
  }
  
  const getEventsForDay = (day) => {
    const date = new Date(currentMonth.getFullYear(), currentMonth.getMonth(), day)
    return getEventsForDate(date)
  }
  
  const renderCalendarDays = () => {
    const days = []
    const totalDays = daysInMonth(currentMonth)
    const firstDay = firstDayOfMonth(currentMonth)
    
    // Empty cells for days before the first day of the month
    for (let i = 0; i < firstDay; i++) {
      days.push(<div key={`empty-${i}`} className="h-24 border border-gray-200 bg-gray-50"></div>)
    }
    
    // Cells for days of the month
    for (let day = 1; day <= totalDays; day++) {
      const date = new Date(currentMonth.getFullYear(), currentMonth.getMonth(), day)
      const isToday = date.toDateString() === new Date().toDateString()
      const isSelected = date.toDateString() === selectedDate.toDateString()
      const dayEvents = getEventsForDay(day)
      
      days.push(
        <div 
          key={day} 
          className={`h-24 border border-gray-200 p-1 overflow-hidden ${isToday ? 'bg-blue-50' : ''}`}
          onClick={() => handleDateClick(day)}
        >
          <div className="flex justify-between">
            <span className={`inline-flex items-center justify-center w-6 h-6 text-sm ${
              isSelected 
                ? 'bg-purple-600 text-white rounded-full' 
                : isToday 
                  ? 'bg-blue-100 text-blue-800 rounded-full' 
                  : ''
            }`}>{day}</span>
            {dayEvents.length > 0 && (
              <span className="text-xs font-medium text-gray-500">{dayEvents.length} event{dayEvents.length > 1 ? 's' : ''}</span>
            )}
          </div>
          <div className="mt-1 space-y-1 overflow-y-auto max-h-16">
            {dayEvents.slice(0, 2).map(event => (
              <div 
                key={event.id} 
                className={`text-xs truncate px-1 py-0.5 rounded ${
                  event.type === 'lecture' ? 'bg-blue-100 text-blue-800' :
                  event.type === 'office-hours' ? 'bg-green-100 text-green-800' :
                  event.type === 'meeting' ? 'bg-purple-100 text-purple-800' :
                  event.type === 'exam' ? 'bg-red-100 text-red-800' :
                  'bg-amber-100 text-amber-800'
                }`}
              >
                {event.title}
              </div>
            ))}
            {dayEvents.length > 2 && (
              <div className="text-xs text-gray-500 pl-1">+{dayEvents.length - 2} more</div>
            )}
          </div>
        </div>
      )
    }
    
    return days
  }
  
  const eventTypeColorClasses = {
    'lecture': 'bg-blue-100 text-blue-800 border-blue-200',
    'office-hours': 'bg-green-100 text-green-800 border-green-200',
    'deadline': 'bg-amber-100 text-amber-800 border-amber-200',
    'meeting': 'bg-purple-100 text-purple-800 border-purple-200',
    'exam': 'bg-red-100 text-red-800 border-red-200'
  }
  
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-md">
        <div className="container mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold">EduAssist AI</h1>
              <span className="hidden md:inline-block px-3 py-1 bg-white/20 rounded-full text-sm">
                Calendar
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
              <h2 className="text-xl font-bold text-gray-800">Academic Calendar</h2>
              <button 
                className="flex items-center px-4 py-2 bg-purple-600 text-white rounded-md font-medium hover:bg-purple-700 transition-colors"
                onClick={handleNewEvent}
              >
                <Plus className="h-4 w-4 mr-2" />
                New Event
              </button>
            </div>
            
            <div className="flex flex-col md:flex-row gap-6">
              <div className="md:w-3/4">
                {/* Calendar Header */}
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-2">
                    <CalendarIcon className="h-5 w-5 text-gray-500" />
                    <h3 className="text-lg font-semibold text-gray-800">
                      {getMonthName(currentMonth)} {currentMonth.getFullYear()}
                    </h3>
                  </div>
                  <div className="flex space-x-2">
                    <button 
                      className="p-2 rounded-md hover:bg-gray-100" 
                      onClick={handlePrevMonth}
                    >
                      <ChevronLeft className="h-5 w-5 text-gray-600" />
                    </button>
                    <button 
                      className="p-2 rounded-md hover:bg-gray-100" 
                      onClick={handleNextMonth}
                    >
                      <ChevronRight className="h-5 w-5 text-gray-600" />
                    </button>
                  </div>
                </div>
                
                {/* Calendar Grid */}
                <div className="grid grid-cols-7 gap-px">
                  {/* Day headers */}
                  {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
                    <div key={day} className="py-2 text-center text-sm font-medium text-gray-500">
                      {day}
                    </div>
                  ))}
                  
                  {/* Calendar days */}
                  {renderCalendarDays()}
                </div>
              </div>
              
              <div className="md:w-1/4">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="font-medium text-gray-800 mb-3 flex items-center">
                    <span className="mr-2">Selected Date</span>
                    <span className="text-sm text-purple-600 font-normal">
                      {selectedDate.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })}
                    </span>
                  </h3>
                  
                  <div className="space-y-3">
                    {getEventsForDate(selectedDate).length > 0 ? (
                      getEventsForDate(selectedDate).map(event => (
                        <div 
                          key={event.id} 
                          className={`p-3 rounded-lg border ${eventTypeColorClasses[event.type]}`}
                        >
                          <div className="flex justify-between items-start">
                            <h4 className="font-medium">{event.title}</h4>
                            <div className="flex space-x-1">
                              <button className="p-1 rounded hover:bg-white/50">
                                <Edit2 className="h-3.5 w-3.5" />
                              </button>
                              <button className="p-1 rounded hover:bg-white/50">
                                <Trash2 className="h-3.5 w-3.5" />
                              </button>
                            </div>
                          </div>
                          {event.startTime && (
                            <div className="mt-1 text-sm">
                              {event.startTime} - {event.endTime}
                            </div>
                          )}
                          {event.location && (
                            <div className="mt-1 text-sm">
                              {event.location}
                            </div>
                          )}
                        </div>
                      ))
                    ) : (
                      <div className="text-center py-6 text-gray-500">No events scheduled</div>
                    )}
                  </div>
                  
                  <button 
                    className="w-full mt-4 py-2 text-center text-sm font-medium text-purple-600 border border-purple-200 rounded-lg hover:bg-purple-50"
                    onClick={handleNewEvent}
                  >
                    Add Event to {selectedDate.getDate()} {getMonthName(selectedDate)}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
      
      {/* Event Modal */}
      {showEventModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6 relative">
            <button 
              className="absolute top-3 right-3 text-gray-400 hover:text-gray-600"
              onClick={handleCloseModal}
            >
              ×
            </button>
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Add New Event</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Event Title</label>
                <input 
                  type="text" 
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                  placeholder="Enter event title"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Event Type</label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500">
                  <option value="lecture">Lecture</option>
                  <option value="office-hours">Office Hours</option>
                  <option value="deadline">Deadline</option>
                  <option value="meeting">Meeting</option>
                  <option value="exam">Exam</option>
                </select>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Date</label>
                  <input 
                    type="date" 
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Time</label>
                  <input 
                    type="time" 
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Location</label>
                <input 
                  type="text" 
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                  placeholder="Enter location (optional)"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea 
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                  rows="3"
                  placeholder="Enter description (optional)"
                ></textarea>
              </div>
              <div className="flex justify-end space-x-2 pt-2">
                <button 
                  className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                  onClick={handleCloseModal}
                >
                  Cancel
                </button>
                <button 
                  className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700"
                  onClick={() => {
                    alert("Event would be saved");
                    handleCloseModal();
                  }}
                >
                  Save Event
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Calendar
