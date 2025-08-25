import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { BookOpen, Users, FileText, TrendingUp, Award, Clock, Target, Brain, Calendar, Bell, Search, Filter, MoreVertical, Eye, MessageSquare, CheckCircle, AlertTriangle, Star, BarChart3, PieChart, Activity, Settings, Mail, Lock, Globe, User as UserIcon } from 'lucide-react';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { User, StudentProgress } from '../../types';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart as RechartsPieChart, Cell } from 'recharts';

interface TeacherDashboardProps {
  user: User;
  onLogout: () => void;
}

export const TeacherDashboard: React.FC<TeacherDashboardProps> = ({ user, onLogout }) => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedSection, setSelectedSection] = useState('Section A');
  const [searchQuery, setSearchQuery] = useState('');
  const [showSettings, setShowSettings] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [notifications, setNotifications] = useState([
    { id: 't1', title: 'Review queue updated', detail: '3 new submissions awaiting review', read: false },
    { id: 't2', title: 'Announcement scheduled', detail: 'Midterm details posted', read: true },
    { id: 't3', title: 'At-risk students', detail: '2 students flagged for low activity', read: false },
  ]);
  const notifRef = useRef<HTMLDivElement | null>(null);
  const bellBtnRef = useRef<HTMLButtonElement | null>(null);
  const settingsRef = useRef<HTMLDivElement | null>(null);
  const handleLogout = () => {
    navigate('/', { replace: true });
    setTimeout(() => {
      try {
        onLogout();
      } catch {}
    }, 0);
  };

  // Close dropdowns/modals on outside click or Escape
  useEffect(() => {
    function onDocMouseDown(e: MouseEvent) {
      const target = e.target as Node;
      // notifications
      if (
        showNotifications &&
        notifRef.current &&
        !notifRef.current.contains(target) &&
        bellBtnRef.current &&
        !bellBtnRef.current.contains(target)
      ) {
        setShowNotifications(false);
      }
      // settings modal
      if (
        showSettings &&
        settingsRef.current &&
        !settingsRef.current.contains(target)
      ) {
        setShowSettings(false);
      }
    }
    function onKey(e: KeyboardEvent) {
      if (e.key === 'Escape') {
        setShowNotifications(false);
        setShowSettings(false);
      }
    }
    document.addEventListener('mousedown', onDocMouseDown);
    document.addEventListener('keydown', onKey);
    return () => {
      document.removeEventListener('mousedown', onDocMouseDown);
      document.removeEventListener('keydown', onKey);
    };
  }, [showNotifications, showSettings]);

  // Mock data
  const [sections] = useState(['Section A', 'Section B', 'Section C', 'Section D']);
  
  const [studentsProgress] = useState<StudentProgress[]>([
    {
      studentId: '1',
      studentName: 'John Smith',
      averageGrade: 92,
      completedAssignments: 8,
      totalAssignments: 10,
      weakAreas: ['Algorithm Complexity', 'Recursion'],
      strengths: ['Data Structures', 'Problem Solving'],
      lastActivity: '2 hours ago'
    },
    {
      studentId: '2',
      studentName: 'Emily Johnson',
      averageGrade: 88,
      completedAssignments: 9,
      totalAssignments: 10,
      weakAreas: ['Database Design', 'SQL Optimization'],
      strengths: ['Web Development', 'JavaScript'],
      lastActivity: '5 hours ago'
    },
    {
      studentId: '3',
      studentName: 'Michael Brown',
      averageGrade: 85,
      completedAssignments: 7,
      totalAssignments: 10,
      weakAreas: ['Machine Learning', 'Statistics'],
      strengths: ['Python Programming', 'Data Analysis'],
      lastActivity: '1 day ago'
    }
  ]);

  const [classStats] = useState({
    totalStudents: 120,
    activeStudents: 98,
    averageGrade: 84,
    completionRate: 87,
    pendingReviews: 15,
    totalAssignments: 45
  });

  const [performanceData] = useState([
    { month: 'Jan', average: 78, section: 82 },
    { month: 'Feb', average: 82, section: 85 },
    { month: 'Mar', average: 79, section: 83 },
    { month: 'Apr', average: 85, section: 88 },
    { month: 'May', average: 84, section: 87 },
    { month: 'Jun', average: 87, section: 90 }
  ]);

  const [gradeDistribution] = useState([
    { grade: 'A', count: 35, color: '#10B981' },
    { grade: 'B', count: 45, color: '#3B82F6' },
    { grade: 'C', count: 25, color: '#F59E0B' },
    { grade: 'D', count: 10, color: '#EF4444' },
    { grade: 'F', count: 5, color: '#6B7280' }
  ]);

  const [recentSubmissions] = useState([
    {
      id: '1',
      studentName: 'John Smith',
      assignment: 'Data Structures Essay',
      submittedAt: '2 hours ago',
      status: 'pending',
      aiGraded: true
    },
    {
      id: '2',
      studentName: 'Emily Johnson',
      assignment: 'Algorithm Analysis',
      submittedAt: '4 hours ago',
      status: 'reviewed',
      aiGraded: true
    },
    {
      id: '3',
      studentName: 'Michael Brown',
      assignment: 'Database Project',
      submittedAt: '1 day ago',
      status: 'pending',
      aiGraded: false
    }
  ]);

  const [upcomingDeadlines] = useState([
    {
      id: '1',
      title: 'Machine Learning Project',
      dueDate: '2024-01-25',
      submissions: 45,
      totalStudents: 60
    },
    {
      id: '2',
      title: 'Database Design Assignment',
      dueDate: '2024-01-28',
      submissions: 12,
      totalStudents: 60
    }
  ]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'reviewed':
        return 'bg-green-100 text-green-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'overdue':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getGradeColor = (grade: number) => {
    if (grade >= 90) return 'text-green-600';
    if (grade >= 80) return 'text-blue-600';
    if (grade >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  const filteredStudents = studentsProgress.filter(student =>
    student.studentName.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.5 }
    }
  };

  return (
    <div className="min-h-screen overflow-hidden bg-[radial-gradient(40rem_40rem_at_10%_10%,rgba(249,115,22,0.16),transparent_60%),radial-gradient(35rem_35rem_at_90%_15%,rgba(168,85,247,0.16),transparent_60%),radial-gradient(32rem_32rem_at_15%_85%,rgba(249,115,22,0.16),transparent_60%),radial-gradient(30rem_30rem_at_85%_85%,rgba(168,85,247,0.16),transparent_60%),linear-gradient(180deg,#0b0a12_0%,#140e19_45%,#1e1524_100%)]">
      {/* Header */}
      <header className="border-b border-white/10 bg-gradient-to-r from-[#0e0a12]/80 to-[#221628]/80 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gradient-to-r from-orange-500 to-purple-600 rounded-lg flex items-center justify-center ring-1 ring-white/10">
                  <BookOpen className="h-5 w-5 text-white" />
                </div>
                <span className="text-xl font-bold bg-gradient-to-r from-orange-500 to-purple-600 bg-clip-text text-transparent">
                  EduLearn AI
                </span>
              </div>
              <div className="hidden md:block h-6 w-px bg-white/10" />
              <h1 className="hidden md:block text-lg font-semibold text-white">Teacher Dashboard</h1>
            </div>

            <div className="flex items-center space-x-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-white/40" />
                <input
                  type="text"
                  placeholder="Search students..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 pr-4 py-2 bg-white/5 text-white placeholder-white/50 border border-white/10 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500/40 w-64"
                />
              </div>

              <div className="relative">
                <button ref={bellBtnRef} onClick={() => setShowNotifications(v=>!v)} className="relative p-2 text-white/70 hover:text-white transition-colors rounded-lg bg-white/5 hover:bg-white/10">
                  <Bell className="h-6 w-6" />
                  {notifications.some(n=>!n.read) && (
                    <span className="absolute -top-0.5 -right-0.5 h-2.5 w-2.5 bg-red-500 rounded-full" />
                  )}
                </button>
                {showNotifications && (
                  <div ref={notifRef} className="absolute right-0 mt-2 w-80 bg-[#0f0b14] border border-white/10 rounded-xl shadow-xl z-50">
                    <div className="p-3 border-b border-white/10 flex items-center justify-between">
                      <span className="text-sm font-semibold text-white">Notifications</span>
                      <button onClick={() => setNotifications(n=>n.map(x=>({ ...x, read: true })))} className="text-xs text-orange-400 hover:text-orange-300">Mark all read</button>
                    </div>
                    <div className="max-h-64 overflow-y-auto">
                      {notifications.map(n => (
                        <div key={n.id} className={`px-3 py-3 border-b border-white/5 ${n.read ? 'bg-transparent' : 'bg-white/5'}`}>
                          <div className="text-sm text-white">{n.title}</div>
                          <div className="text-xs text-white/60">{n.detail}</div>
                        </div>
                      ))}
                      {notifications.length === 0 && (
                        <div className="p-4 text-sm text-white/60">No notifications</div>
                      )}
                    </div>
                  </div>
                )}
              </div>

              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-white/10 rounded-full flex items-center justify-center ring-1 ring-white/10">
                  <span className="text-white font-medium text-sm">
                    {user.name.split(' ').map(n => n[0]).join('')}
                  </span>
                </div>
                <div className="hidden md:block">
                  <p className="text-sm font-medium text-white">{user.name}</p>
                  <p className="text-xs text-white/60">Teacher</p>
                </div>
              </div>

              <Button variant="ghost" onClick={() => setShowSettings(true)}>
                <Settings className="h-4 w-4 mr-2" />
                Settings
              </Button>
              <Button variant="ghost" onClick={handleLogout}>Logout</Button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="rounded-2xl p-6 text-white bg-gradient-to-r from-orange-500/20 to-purple-600/20 ring-1 ring-white/10">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center">
              <div>
                <h2 className="text-2xl font-bold mb-2">Welcome back, {user.name}! 👨‍🏫</h2>
                <p className="text-white/80">
                  You have {classStats.pendingReviews} assignments to review and {classStats.activeStudents} active students across all sections.
                </p>
              </div>
              <div className="mt-4 md:mt-0 flex space-x-3">
                <Button variant="secondary" size="sm">
                  <Calendar className="h-4 w-4 mr-2" />
                  Schedule
                </Button>
                <Button variant="outline" size="sm" className="border-white/20 text-white hover:bg-white/10">
                  <BarChart3 className="h-4 w-4 mr-2" />
                  Analytics
                </Button>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Section Selector */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6"
        >
          <Card className="p-4 bg-white/5 border border-white/10 text-white">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-white">Class Sections</h3>
              <div className="flex space-x-2">
                {sections.map((section) => (
                  <button
                    key={section}
                    onClick={() => setSelectedSection(section)}
                    className={`px-4 py-2 rounded-lg font-medium text-sm transition-colors ${
                      selectedSection === section
                        ? 'bg-gradient-to-r from-orange-500 to-purple-600 text-white'
                        : 'bg-white/10 text-white/80 hover:bg-white/20'
                    }`}
                  >
                    {section}
                  </button>
                ))}
              </div>
            </div>
          </Card>
        </motion.div>

        {/* Stats Grid */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
        >
          {[
            {
              title: 'Total Students',
              value: classStats.totalStudents.toString(),
              icon: Users,
              color: 'from-orange-500 to-purple-600',
              change: '+5 this month'
            },
            {
              title: 'Average Grade',
              value: `${classStats.averageGrade}%`,
              icon: TrendingUp,
              color: 'from-green-500 to-emerald-600',
              change: '+3% from last month'
            },
            {
              title: 'Completion Rate',
              value: `${classStats.completionRate}%`,
              icon: Target,
              color: 'from-purple-500 to-pink-600',
              change: '+2% improvement'
            },
            {
              title: 'Pending Reviews',
              value: classStats.pendingReviews.toString(),
              icon: Clock,
              color: 'from-orange-500 to-red-500',
              change: '5 urgent'
            }
          ].map((stat, index) => (
            <motion.div key={index} variants={itemVariants}>
              <Card className="p-6 bg-white/5 border border-white/10 text-white hover:bg-white/10 transition-all duration-300">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-white/70">{stat.title}</p>
                    <p className="text-2xl font-bold text-white mt-1">{stat.value}</p>
                    <p className="text-sm text-emerald-400 mt-1">{stat.change}</p>
                  </div>
                  <div className={`w-12 h-12 bg-gradient-to-r ${stat.color} rounded-lg flex items-center justify-center ring-1 ring-white/10`}>
                    <stat.icon className="h-6 w-6 text-white" />
                  </div>
                </div>
              </Card>
            </motion.div>
          ))}
        </motion.div>

        {/* Navigation Tabs */}
        <div className="mb-6">
          <nav className="flex space-x-8 border-b border-white/10">
            {[
              { id: 'overview', label: 'Overview', icon: BarChart3 },
              { id: 'students', label: 'Student Progress', icon: Users },
              { id: 'assignments', label: 'Assignments', icon: FileText },
              { id: 'analytics', label: 'Analytics', icon: PieChart },
              { id: 'submissions', label: 'Recent Submissions', icon: Clock }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab.id
                    ? 'border-orange-500 text-white'
                    : 'border-transparent text-white/60 hover:text-white hover:border-white/20'
                }`}
              >
                <tab.icon className="h-4 w-4" />
                <span>{tab.label}</span>
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Content */}
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
          >
            {activeTab === 'overview' && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Performance Chart */}
                <Card className="p-6 bg-white/5 border border-white/10 text-white">
                  <h3 className="text-lg font-semibold text-white mb-4">Class Performance Trend</h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={performanceData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="month" />
                      <YAxis />
                      <Tooltip />
                      <Line type="monotone" dataKey="average" stroke="#8884d8" strokeWidth={2} />
                      <Line type="monotone" dataKey="section" stroke="#82ca9d" strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                </Card>

                {/* Grade Distribution */}
                <Card className="p-6 bg-white/5 border border-white/10 text-white">
                  <h3 className="text-lg font-semibold text-white mb-4">Grade Distribution</h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={gradeDistribution}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="grade" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="count" fill="#8884d8" />
                    </BarChart>
                  </ResponsiveContainer>
                </Card>

                {/* Upcoming Deadlines */}
                <Card className="p-6 bg-white/5 border border-white/10 text-white">
                  <h3 className="text-lg font-semibold text-white mb-4">Upcoming Deadlines</h3>
                  <div className="space-y-4">
                    {upcomingDeadlines.map((deadline) => (
                      <div key={deadline.id} className="flex items-center justify-between p-4 bg-white/5 rounded-lg border border-white/10">
                        <div>
                          <p className="font-medium text-white">{deadline.title}</p>
                          <p className="text-sm text-white/60">Due: {new Date(deadline.dueDate).toLocaleDateString()}</p>
                        </div>
                        <div className="text-right">
                          <p className="text-sm font-medium text-white">
                            {deadline.submissions}/{deadline.totalStudents}
                          </p>
                          <p className="text-xs text-white/60">submissions</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </Card>

                {/* Quick Actions */}
                <Card className="p-6 bg-white/5 border border-white/10 text-white">
                  <h3 className="text-lg font-semibold text-white mb-4">Quick Actions</h3>
                  <div className="space-y-3">
                    <Button variant="outline" className="w-full justify-start">
                      <FileText className="h-4 w-4 mr-2" />
                      Create New Assignment
                    </Button>
                    <Button variant="outline" className="w-full justify-start">
                      <Users className="h-4 w-4 mr-2" />
                      View All Students
                    </Button>
                    <Button variant="outline" className="w-full justify-start">
                      <BarChart3 className="h-4 w-4 mr-2" />
                      Generate Report
                    </Button>
                    <Button variant="outline" className="w-full justify-start">
                      <MessageSquare className="h-4 w-4 mr-2" />
                      Send Announcement
                    </Button>
                  </div>
                </Card>
              </div>
            )}

            {activeTab === 'students' && (
              <div>
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-xl font-semibold text-white">Student Progress - {selectedSection}</h2>
                  <div className="flex items-center space-x-3">
                    <Button size="sm">
                      <Filter className="h-4 w-4 mr-2" />
                      Filter
                    </Button>
                    <Button size="sm">
                      Export Data
                    </Button>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {filteredStudents.map((student) => (
                    <motion.div
                      key={student.studentId}
                      whileHover={{ y: -4 }}
                      transition={{ duration: 0.2 }}
                    >
                      <Card className="p-6 cursor-pointer bg-white/5 border border-white/10 text-white hover:bg-white/10 transition-all duration-300">
                        <div className="flex items-center justify-between mb-4">
                          <div className="flex items-center space-x-3">
                            <div className="w-10 h-10 bg-white/10 rounded-full flex items-center justify-center ring-1 ring-white/10">
                              <span className="text-white font-medium text-sm">
                                {student.studentName.split(' ').map(n => n[0]).join('')}
                              </span>
                            </div>
                            <div>
                              <h3 className="font-semibold text-white">{student.studentName}</h3>
                              <p className="text-sm text-white/60">Last active: {student.lastActivity}</p>
                            </div>
                          </div>
                          <Button variant="ghost" size="sm">
                            <MoreVertical className="h-4 w-4" />
                          </Button>
                        </div>

                        <div className="space-y-3">
                          <div className="flex justify-between items-center">
                            <span className="text-sm text-white/70">Average Grade</span>
                            <span className={`font-semibold ${getGradeColor(student.averageGrade)}`}>
                              {student.averageGrade}%
                            </span>
                          </div>

                          <div className="flex justify-between items-center">
                            <span className="text-sm text-white/70">Completion</span>
                            <span className="font-semibold text-white">
                              {student.completedAssignments}/{student.totalAssignments}
                            </span>
                          </div>

                          <div className="w-full bg-white/10 rounded-full h-2">
                            <div
                              className="bg-gradient-to-r from-orange-500 to-purple-600 h-2 rounded-full"
                              style={{ width: `${(student.completedAssignments / student.totalAssignments) * 100}%` }}
                            ></div>
                          </div>

                          <div>
                            <p className="text-sm text-white/70 mb-1">Strengths:</p>
                            <div className="flex flex-wrap gap-1">
                              {student.strengths.slice(0, 2).map((strength, index) => (
                                <span key={index} className="px-2 py-1 bg-green-500/20 text-green-300 border border-green-500/20 text-xs rounded-full">
                                  {strength}
                                </span>
                              ))}
                            </div>
                          </div>

                          <div>
                            <p className="text-sm text-white/70 mb-1">Needs Improvement:</p>
                            <div className="flex flex-wrap gap-1">
                              {student.weakAreas.slice(0, 2).map((area, index) => (
                                <span key={index} className="px-2 py-1 bg-red-500/20 text-red-300 border border-red-500/20 text-xs rounded-full">
                                  {area}
                                </span>
                              ))}
                            </div>
                          </div>
                        </div>

                        <div className="mt-4 flex space-x-2">
                          <Button size="sm" variant="outline" className="flex-1">
                            <Eye className="h-4 w-4 mr-1" />
                            View Details
                          </Button>
                          <Button size="sm" variant="outline" className="flex-1">
                            <MessageSquare className="h-4 w-4 mr-1" />
                            Message
                          </Button>
                        </div>
                      </Card>
                    </motion.div>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'submissions' && (
              <div>
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-xl font-semibold text-white">Recent Submissions</h2>
                  <Button>
                    <CheckCircle className="h-4 w-4 mr-2" />
                    Review All
                  </Button>
                </div>

                <Card className="overflow-hidden bg-white/5 border border-white/10 text-white">
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-white/10">
                      <thead className="bg-white/5">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-white/60 uppercase tracking-wider">
                            Student
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-white/60 uppercase tracking-wider">
                            Assignment
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-white/60 uppercase tracking-wider">
                            Submitted
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-white/60 uppercase tracking-wider">
                            Status
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-white/60 uppercase tracking-wider">
                            AI Graded
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-white/60 uppercase tracking-wider">
                            Actions
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-transparent divide-y divide-white/10">
                        {recentSubmissions.map((submission) => (
                          <tr key={submission.id} className="hover:bg-white/5">
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="flex items-center">
                                <div className="w-8 h-8 bg-white/10 rounded-full flex items-center justify-center mr-3 ring-1 ring-white/10">
                                  <span className="text-white font-medium text-xs">
                                    {submission.studentName.split(' ').map(n => n[0]).join('')}
                                  </span>
                                </div>
                                <div className="text-sm font-medium text-white">
                                  {submission.studentName}
                                </div>
                              </div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="text-sm text-white">{submission.assignment}</div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="text-sm text-white/60">{submission.submittedAt}</div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(submission.status)} bg-white/10 text-white` }>
                                {submission.status}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              {submission.aiGraded ? (
                                <CheckCircle className="h-5 w-5 text-green-400" />
                              ) : (
                                <AlertTriangle className="h-5 w-5 text-yellow-400" />
                              )}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                              <div className="flex space-x-2">
                                <Button size="sm" variant="outline">
                                  Review
                                </Button>
                                <Button size="sm" variant="ghost">
                                  <MoreVertical className="h-4 w-4" />
                                </Button>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </Card>
              </div>
            )}
          </motion.div>
        </AnimatePresence>
        {/* Settings Modal */}
        <AnimatePresence>
          {showSettings && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 z-50 flex items-center justify-center bg-black/60"
            >
              <motion.div
                ref={settingsRef}
                initial={{ scale: 0.98, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.98, opacity: 0 }}
                transition={{ duration: 0.15 }}
                className="w-full max-w-3xl bg-[#0f0b14] border border-white/10 rounded-2xl shadow-2xl overflow-hidden text-white"
              >
                <div className="p-4 border-b border-white/10 bg-gradient-to-r from-[#0e0a12]/80 to-[#221628]/80">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <div className="w-8 h-8 bg-gradient-to-r from-orange-500 to-purple-600 rounded-lg flex items-center justify-center ring-1 ring-white/10">
                        <Settings className="h-4 w-4 text-white" />
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold">Settings</h3>
                        <p className="text-xs text-white/60">Manage profile, preferences and security</p>
                      </div>
                    </div>
                    <Button variant="ghost" onClick={() => setShowSettings(false)}>Close</Button>
                  </div>
                </div>
                <div className="p-6 space-y-6">
                  {/* Profile */}
                  <div className="bg-white/5 border border-white/10 rounded-xl p-5">
                    <div className="flex items-center mb-4">
                      <UserIcon className="h-5 w-5 text-white/70 mr-2" />
                      <h4 className="text-white font-semibold">Profile</h4>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <label className="text-xs text-white/60">Name</label>
                        <input defaultValue={user.name} className="mt-1 w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-orange-500/40" />
                      </div>
                      <div>
                        <label className="text-xs text-white/60">Email</label>
                        <input defaultValue={user.email} className="mt-1 w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-orange-500/40" />
                      </div>
                      <div>
                        <label className="text-xs text-white/60">Section</label>
                        <input defaultValue={(user as any).section || selectedSection} className="mt-1 w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-orange-500/40" />
                      </div>
                    </div>
                  </div>

                  {/* Preferences */}
                  <div className="bg-white/5 border border-white/10 rounded-xl p-5">
                    <div className="flex items-center mb-4">
                      <Globe className="h-5 w-5 text-white/70 mr-2" />
                      <h4 className="text-white font-semibold">Preferences</h4>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <label className="text-xs text-white/60">Language</label>
                        <select defaultValue="en" className="mt-1 w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white focus:outline-none focus:ring-2 focus:ring-orange-500/40">
                          <option value="en">English</option>
                          <option value="hi">Hindi</option>
                          <option value="ta">Tamil</option>
                        </select>
                      </div>
                      <div className="flex items-end">
                        <label className="flex items-center space-x-2 text-white/80">
                          <input type="checkbox" defaultChecked className="form-checkbox h-4 w-4 text-orange-500" />
                          <span>Email notifications</span>
                        </label>
                      </div>
                      <div className="flex items-end">
                        <label className="flex items-center space-x-2 text-white/80">
                          <input type="checkbox" className="form-checkbox h-4 w-4 text-orange-500" />
                          <span>Dark theme</span>
                        </label>
                      </div>
                    </div>
                  </div>

                  {/* Security */}
                  <div className="bg-white/5 border border-white/10 rounded-xl p-5">
                    <div className="flex items-center mb-4">
                      <Lock className="h-5 w-5 text-white/70 mr-2" />
                      <h4 className="text-white font-semibold">Security</h4>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <label className="text-xs text-white/60">Current Password</label>
                        <input type="password" placeholder="••••••••" className="mt-1 w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-orange-500/40" />
                      </div>
                      <div>
                        <label className="text-xs text-white/60">New Password</label>
                        <input type="password" placeholder="••••••••" className="mt-1 w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-orange-500/40" />
                      </div>
                      <div>
                        <label className="text-xs text-white/60">Confirm Password</label>
                        <input type="password" placeholder="••••••••" className="mt-1 w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-orange-500/40" />
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <Button variant="outline" onClick={handleLogout}>Logout</Button>
                    <div className="space-x-3">
                      <Button variant="ghost" onClick={() => setShowSettings(false)}>Cancel</Button>
                      <Button>Save Changes</Button>
                    </div>
                  </div>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};
