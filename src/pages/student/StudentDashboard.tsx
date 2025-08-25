import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { BookOpen, Code, FileText, TrendingUp, Award, Clock, Target, Brain, Users, Calendar, Bell, Search, Filter, MoreVertical, Play, CheckCircle, AlertCircle, Star, GraduationCap, Microscope, MessageSquare, Library, Briefcase, UserCheck, Notebook, Video, Headphones, Globe, Zap, Trophy, Medal, Crown, Sparkles, ChevronRight, Plus, Download, Share, Eye, Heart, ThumbsUp, Coffee, Moon, Sun, Settings, HelpCircle, LogOut } from 'lucide-react';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Scene3D } from '../../components/3D/Scene3D';
import { User, Assignment, StudyMaterial, VirtualLab, Discussion, Attendance, Grade, StudyGroup, Certificate, Project, Internship, CalendarEvent, Note, LibraryBook } from '../../types';
import CodingEnvironment from './CodingEnvironment';

interface StudentDashboardProps {
  user: User;
  onLogout: () => void;
}

export const StudentDashboard: React.FC<StudentDashboardProps> = ({ user, onLogout }) => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('overview');
  const [showSettings, setShowSettings] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [notifications, setNotifications] = useState([
    { id: 'n1', title: 'Assignment due tomorrow', detail: 'Data Structures Implementation', read: false },
    { id: 'n2', title: 'New announcement', detail: 'AI lecture slides uploaded', read: false },
    { id: 'n3', title: 'Study group', detail: 'Algorithm Masters meeting today 6 PM', read: true },
  ]);
  const notifRef = useRef<HTMLDivElement | null>(null);
  const bellBtnRef = useRef<HTMLButtonElement | null>(null);
  const [profileForm, setProfileForm] = useState({
    name: user.name || '',
    email: user.email || '',
    role: user.role || 'student',
    section: user.section || 'A',
  });
  const [prefsForm, setPrefsForm] = useState({ theme: 'dark', language: 'en', notifications: true });
  const [securityForm, setSecurityForm] = useState({ current: '', next: '', confirm: '' });
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [currentTime, setCurrentTime] = useState(new Date());
  const [showCodingEnvironment, setShowCodingEnvironment] = useState(false);
  const [selectedProblem, setSelectedProblem] = useState<any>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedProblems, setGeneratedProblems] = useState<any[]>([]);
  const [topicInput, setTopicInput] = useState('algorithms');
  const [genDifficulty, setGenDifficulty] = useState<'easy' | 'medium' | 'hard'>('easy');
  const API_BASE = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000';
  const BACKEND = 'http://localhost:5003';
  const [leaderboard, setLeaderboard] = useState<any[]>([]);
  const fetchLeaderboard = async () => {
    try {
      const res = await fetch(`${BACKEND}/leaderboard?limit=10`);
      const data = await res.json();
      setLeaderboard(data?.items || []);
    } catch (e) {
      console.error('Failed to load leaderboard', e);
      setLeaderboard([]);
    }
  };
  useEffect(() => {
    if (activeTab === 'leaderboard') fetchLeaderboard();
  }, [activeTab]);

  // Update time every minute
  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 60000);
    return () => clearInterval(timer);
  }, []);

  // Close dropdowns/modals on outside click or Escape
  useEffect(() => {
    function onDocMouseDown(e: MouseEvent) {
      if (!showNotifications) return;
      const target = e.target as Node;
      if (
        notifRef.current &&
        !notifRef.current.contains(target) &&
        bellBtnRef.current &&
        !bellBtnRef.current.contains(target)
      ) {
        setShowNotifications(false);
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
  }, [showNotifications]);

  // Mock comprehensive data
  const [assignments] = useState<Assignment[]>([
    {
      id: '1',
      title: 'Data Structures Implementation',
      subject: 'Computer Science',
      description: 'Implement various data structures including linked lists, stacks, and queues with comprehensive testing.',
      dueDate: '2024-01-20',
      status: 'pending',
      maxGrade: 100,
      attachments: ['requirements.pdf', 'starter_code.zip']
    },
    {
      id: '2',
      title: 'Machine Learning Project',
      subject: 'Artificial Intelligence',
      description: 'Build a classification model using supervised learning techniques with real-world dataset.',
      dueDate: '2024-01-25',
      status: 'pending',
      maxGrade: 100
    },
    {
      id: '3',
      title: 'Database Design Assignment',
      subject: 'Database Systems',
      description: 'Design and implement a normalized database schema for an e-commerce platform.',
      dueDate: '2024-01-15',
      status: 'completed',
      grade: 92,
      maxGrade: 100,
      feedback: 'Excellent work on normalization! Consider adding more indexes for performance.'
    }
  ]);

  const [studyMaterials] = useState<StudyMaterial[]>([
    {
      id: '1',
      title: 'Advanced Algorithms Lecture Series',
      subject: 'Computer Science',
      type: 'video',
      url: '#',
      description: 'Comprehensive video series covering advanced algorithmic concepts',
      uploadDate: '2024-01-10',
      duration: '4h 30m',
      tags: ['algorithms', 'complexity', 'optimization']
    },
    {
      id: '2',
      title: 'Machine Learning Fundamentals',
      subject: 'AI',
      type: 'pdf',
      url: '#',
      description: 'Complete guide to machine learning concepts and implementations',
      uploadDate: '2024-01-08',
      size: '15.2 MB',
      tags: ['ml', 'python', 'statistics']
    }
  ]);

  const [virtualLabs] = useState<VirtualLab[]>([
    {
      id: '1',
      title: 'Chemistry Virtual Lab',
      subject: 'Chemistry',
      description: 'Interactive chemistry experiments in a safe virtual environment',
      type: 'simulation',
      difficulty: 'Intermediate',
      estimatedTime: 120,
      prerequisites: ['Basic Chemistry', 'Lab Safety'],
      learningOutcomes: ['Chemical Reactions', 'Lab Techniques', 'Safety Protocols']
    },
    {
      id: '2',
      title: 'Physics Mechanics Lab',
      subject: 'Physics',
      description: 'Explore Newtonian mechanics through interactive simulations',
      type: 'simulation',
      difficulty: 'Beginner',
      estimatedTime: 90,
      prerequisites: ['Basic Physics'],
      learningOutcomes: ['Force Analysis', 'Motion Equations', 'Energy Conservation']
    }
  ]);

  const [discussions] = useState<Discussion[]>([
    {
      id: '1',
      title: 'Best practices for algorithm optimization',
      subject: 'Computer Science',
      author: 'Dr. Smith',
      participants: 24,
      lastActivity: '2 hours ago',
      tags: ['algorithms', 'optimization', 'performance']
    },
    {
      id: '2',
      title: 'Understanding neural network architectures',
      subject: 'AI',
      author: 'Prof. Johnson',
      participants: 18,
      lastActivity: '1 day ago',
      tags: ['neural networks', 'deep learning', 'architecture']
    }
  ]);

  const [studyGroups] = useState<StudyGroup[]>([
    {
      id: '1',
      name: 'Algorithm Masters',
      subject: 'Computer Science',
      members: 12,
      maxMembers: 15,
      description: 'Advanced algorithm study group focusing on competitive programming',
      meetingTime: 'Every Tuesday 6 PM',
      status: 'active'
    },
    {
      id: '2',
      name: 'AI Enthusiasts',
      subject: 'Artificial Intelligence',
      members: 8,
      maxMembers: 10,
      description: 'Machine learning and AI discussion group',
      meetingTime: 'Every Thursday 7 PM',
      status: 'active'
    }
  ]);

  const [grades] = useState<Grade[]>([
    { id: '1', subject: 'Computer Science', assignment: 'Data Structures', grade: 92, maxGrade: 100, date: '2024-01-10' },
    { id: '2', subject: 'AI', assignment: 'Neural Networks', grade: 88, maxGrade: 100, date: '2024-01-08' },
    { id: '3', subject: 'Database Systems', assignment: 'SQL Project', grade: 95, maxGrade: 100, date: '2024-01-05' }
  ]);

  const [attendance] = useState<Attendance[]>([
    { id: '1', subject: 'Computer Science', date: '2024-01-15', status: 'present' },
    { id: '2', subject: 'AI', date: '2024-01-14', status: 'present' },
    { id: '3', subject: 'Database Systems', date: '2024-01-13', status: 'absent' }
  ]);

  const [certificates] = useState<Certificate[]>([
    { id: '1', name: 'Python Programming', issuer: 'Coursera', date: '2024-01-10', status: 'completed' },
    { id: '2', name: 'Machine Learning Basics', issuer: 'edX', date: '2024-01-05', status: 'completed' }
  ]);

  const [projects] = useState<Project[]>([
    { id: '1', title: 'E-commerce Platform', description: 'Full-stack web application', status: 'in-progress', progress: 75 },
    { id: '2', title: 'AI Chatbot', description: 'Natural language processing project', status: 'completed', progress: 100 }
  ]);

  const [internships] = useState<Internship[]>([
    { id: '1', company: 'Tech Corp', position: 'Software Developer Intern', status: 'applied', deadline: '2024-02-01' },
    { id: '2', company: 'AI Startup', position: 'ML Engineer Intern', status: 'interview', deadline: '2024-01-30' }
  ]);

  const [notes] = useState<Note[]>([
    { id: '1', title: 'Algorithm Complexity Notes', subject: 'Computer Science', lastModified: '2024-01-15', tags: ['algorithms', 'complexity'] },
    { id: '2', title: 'Neural Network Architecture', subject: 'AI', lastModified: '2024-01-12', tags: ['neural networks', 'architecture'] }
  ]);

  const [libraryBooks] = useState<LibraryBook[]>([
    { id: '1', title: 'Introduction to Algorithms', author: 'Cormen et al.', subject: 'Computer Science', status: 'available' },
    { id: '2', title: 'Pattern Recognition', author: 'Bishop', subject: 'AI', status: 'borrowed' }
  ]);

  const [calendarEvents] = useState<CalendarEvent[]>([
    { id: '1', title: 'Assignment Due: Data Structures', date: '2024-01-20', type: 'assignment' },
    { id: '2', title: 'Study Group: Algorithm Masters', date: '2024-01-21', type: 'group' },
    { id: '3', title: 'Virtual Lab: Chemistry', date: '2024-01-22', type: 'lab' }
  ]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'pending':
        return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
      case 'overdue':
        return 'bg-red-500/20 text-red-400 border-red-500/30';
      default:
        return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'Beginner':
        return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'Intermediate':
        return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
      case 'Advanced':
        return 'bg-red-500/20 text-red-400 border-red-500/30';
      default:
        return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  const filteredAssignments = assignments.filter(assignment => {
    const matchesSearch = assignment.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         assignment.subject.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesFilter = filterStatus === 'all' || assignment.status === filterStatus;
    return matchesSearch && matchesFilter;
  });

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

  const tabItems = [
    { id: 'overview', label: 'Overview', icon: BookOpen },
    { id: 'assignments', label: 'Assignments', icon: FileText },
    { id: 'coding', label: 'Coding Tests', icon: Code },
    { id: 'mcq', label: 'MCQ Tests', icon: Brain },
    { id: 'leaderboard', label: 'Leaderboard', icon: Trophy },
    { id: 'materials', label: 'Study Materials', icon: Library },
    { id: 'labs', label: 'Virtual Labs', icon: Microscope },
    { id: 'discussions', label: 'Discussions', icon: MessageSquare },
    { id: 'groups', label: 'Study Groups', icon: Users },
    { id: 'projects', label: 'Projects', icon: Briefcase },
    { id: 'internships', label: 'Internships', icon: UserCheck },
    { id: 'notes', label: 'My Notes', icon: Notebook },
    { id: 'library', label: 'Library', icon: Library },
    { id: 'certificates', label: 'Certificates', icon: Award }
  ];

  // Derived UI data
  const pendingAssignments = assignments.filter(a => a.status === 'pending');
  const upcomingTasks = pendingAssignments
    .map(a => ({ id: a.id, title: a.title, due: new Date(a.dueDate) }))
    .sort((a, b) => a.due.getTime() - b.due.getTime())
    .slice(0, 5);

  const coursesProgress = [
    { id: 'cs', name: 'Computer Science', completion: 72 },
    { id: 'ai', name: 'Artificial Intelligence', completion: 58 },
    { id: 'db', name: 'Database Systems', completion: 83 },
  ];

  const recentGrades = grades.slice(0, 5);

  const earnedSkills = [
    { id: 'algo', name: 'Algorithms', level: 'Intermediate' },
    { id: 'python', name: 'Python', level: 'Advanced' },
    { id: 'ds', name: 'Data Structures', level: 'Advanced' },
  ];

  const aiStudyPlanner = [
    ...upcomingTasks.map(t => ({
      type: 'Assignment',
      text: `Focus 45 mins on "${t.title}"`,
    })),
    { type: 'Practice', text: 'Solve 3 DP questions (easy → medium)' },
    { type: 'Review', text: 'Revisit Virtual Lab notes for Physics simulation' },
  ].slice(0, 6);

  const adaptiveRecommendations = [
    'Strengthen database indexing strategies (from past feedback)',
    'Practice recursion patterns (tree + backtracking)',
    'Review algorithm complexity cheatsheet',
  ];

  const knowledgeSummaries = studyMaterials.slice(0, 3).map(m => ({
    id: m.id,
    title: m.title,
    bullets: [
      `Subject: ${m.subject}`,
      `Type: ${m.type}`,
      'Key concepts: highlighted in notes',
    ],
  }));

  const handleStartPractice = (problem: any) => {
    setSelectedProblem(problem);
    setShowCodingEnvironment(true);
  };

  const handleCloseCodingEnvironment = () => {
    setShowCodingEnvironment(false);
    setSelectedProblem(null);
  };

  const generateNewProblems = async (difficulty: 'easy' | 'medium' | 'hard' = 'easy', topic: string = 'algorithms') => {
    try {
      setIsGenerating(true);
      const res = await fetch(`${API_BASE}/coding/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: user.id || user.email || 'student',
          topic,
          difficulty,
          count: 1,
          preferred_languages: ['javascript', 'python']
        })
      });
      const data = await res.json();
      const mapped = (data?.problems || []).map((p: any) => ({
        id: p.id,
        title: p.title,
        difficulty: (p.difficulty || 'easy').charAt(0).toUpperCase() + (p.difficulty || 'easy').slice(1),
        category: (p.tags && p.tags[0]) || topic,
        description: p.statement,
        examples: (p.examples || []).map((e: any) => ({ input: e.input, output: e.output, explanation: e.explanation })),
        constraints: p.constraints || [],
        starterCode: {
          javascript: '// Write your solution here\n',
          python: '# Write your solution here\n',
        },
        testCases: (p.test_cases || []).map((t: any) => ({ input: t.input, output: t.output, isHidden: false })),
      }));
      setGeneratedProblems(mapped);
      if (mapped[0]) {
        handleStartPractice(mapped[0]);
      }
    } catch (e) {
      console.error('Problem generation failed', e);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleLogout = () => {
    navigate('/', { replace: true });
    // Defer state change to avoid route guard redirecting to /login
    setTimeout(() => {
      try {
        onLogout();
      } catch {}
    }, 0);
  };

  return (
    <div className="relative min-h-screen bg-gradient-to-br from-[#0e0a12] via-[#160f1c] to-[#221628] text-white overflow-hidden">
      {/* Decorative gradient mesh background */}
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -top-32 -left-24 w-[38rem] h-[38rem] rounded-full blur-3xl bg-orange-500/10" />
        <div className="absolute -bottom-40 -right-24 w-[36rem] h-[36rem] rounded-full blur-3xl bg-purple-500/10" />
        <div className="absolute top-1/3 -right-20 w-[28rem] h-[28rem] rounded-full blur-3xl bg-orange-500/8" />
      </div>

      {/* Enhanced Header */}
      <header className="relative z-10 bg-black/20 backdrop-blur-md border-b border-white/10 shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gradient-to-r from-orange-500 to-purple-600 rounded-lg flex items-center justify-center shadow-lg">
                  <GraduationCap className="h-5 w-5 text-white" />
                </div>
                <span className="text-xl font-bold bg-gradient-to-r from-orange-300 via-yellow-300 to-purple-300 bg-clip-text text-transparent">
                  EduLearn AI
                </span>
              </div>
              <div className="hidden md:block h-6 w-px bg-white/20" />
              <h1 className="hidden md:block text-lg font-semibold text-white/90">Student Dashboard</h1>
            </div>

            <div className="flex items-center space-x-4">
              <div className="hidden md:flex items-center space-x-2 text-sm text-white/70">
                <Clock className="h-4 w-4" />
                <span>{currentTime.toLocaleTimeString()}</span>
              </div>

              <div className="flex items-center space-x-2">
                <div className="relative">
                  <button ref={bellBtnRef} onClick={() => setShowNotifications(v=>!v)} className="relative p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors text-white/70 hover:text-white">
                    <Bell className="h-5 w-5" />
                    {notifications.some(n=>!n.read) && (
                      <span className="absolute -top-0.5 -right-0.5 h-2.5 w-2.5 rounded-full bg-red-500"></span>
                    )}
              </button>
                  {showNotifications && (
                    <div ref={notifRef} className="absolute right-0 mt-2 w-80 bg-[#0f0b14] border border-white/10 rounded-xl shadow-xl z-50">
                      <div className="p-3 border-b border-white/10 flex items-center justify-between">
                        <span className="text-sm font-semibold text-white">Notifications</span>
                        <button onClick={() => { setNotifications(n=>n.map(x=>({ ...x, read: true }))); }} className="text-xs text-orange-400 hover:text-orange-300">Mark all read</button>
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
                <button onClick={() => setShowSettings(true)} className="p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors text-white/70 hover:text-white">
                  <Settings className="h-5 w-5" />
                </button>
              <button
                  onClick={handleLogout}
                  className="p-2 rounded-lg bg-gradient-to-r from-orange-500 to-purple-600 hover:from-orange-600 hover:to-purple-700 transition-all text-white shadow-lg hover:shadow-xl"
              >
                  <LogOut className="h-5 w-5" />
              </button>
                </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-3xl font-bold text-white mb-2">
                Welcome back, {user.name}! 👋
              </h2>
              <p className="text-white/70">
                Ready to continue your learning journey? Here's what's happening today.
              </p>
                  </div>
            <div className="hidden md:flex items-center space-x-4">
              <div className="text-right">
                <div className="text-sm text-white/50">Current Progress</div>
                <div className="text-2xl font-bold bg-gradient-to-r from-orange-400 to-purple-400 bg-clip-text text-transparent">
                  78%
                  </div>
                  </div>
              <div className="w-16 h-16 rounded-full bg-gradient-to-r from-orange-500 to-purple-600 flex items-center justify-center shadow-lg">
                <TrendingUp className="h-8 w-8 text-white" />
                </div>
            </div>
          </div>
        </motion.div>

        {/* Navigation Tabs */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="mb-8"
        >
          <div className="flex flex-wrap gap-2">
              {tabItems.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-xl font-medium transition-all duration-200 ${
                    activeTab === tab.id
                    ? 'bg-gradient-to-r from-orange-500 to-purple-600 text-white shadow-lg'
                    : 'bg-white/5 text-white/70 hover:bg-white/10 hover:text-white border border-white/10'
                  }`}
                >
                  <tab.icon className="h-4 w-4" />
                  <span>{tab.label}</span>
                </button>
              ))}
          </div>
        </motion.div>

        {/* Search and Filter */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="mb-8 flex flex-col sm:flex-row gap-4"
        >
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-white/50" />
            <input
              type="text"
              placeholder="Search assignments, materials, or topics..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-orange-500/50 focus:border-orange-500/50 transition-all"
            />
                  </div>
                    <select
                      value={filterStatus}
                      onChange={(e) => setFilterStatus(e.target.value)}
            className="px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-orange-500/50 focus:border-orange-500/50 transition-all"
          >
            <option value="all" className="bg-gray-800">All Status</option>
            <option value="pending" className="bg-gray-800">Pending</option>
            <option value="completed" className="bg-gray-800">Completed</option>
            <option value="overdue" className="bg-gray-800">Overdue</option>
                    </select>
        </motion.div>

        {/* Content Area */}
                    <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="grid grid-cols-1 lg:grid-cols-3 gap-8"
        >
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            {/* Overview Tab */}
            {activeTab === 'overview' && (
              <motion.div variants={itemVariants} className="space-y-8">
                {/* Quick Stats */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-sm">
                    <div className="flex items-center justify-between mb-4">
                      <div className="w-12 h-12 rounded-xl bg-gradient-to-r from-orange-500 to-purple-600 flex items-center justify-center">
                        <FileText className="h-6 w-6 text-white" />
                        </div>
                      <span className="text-2xl font-bold text-white">{pendingAssignments.length}</span>
                          </div>
                    <h3 className="text-white/90 font-medium">Pending Assignments</h3>
                    <p className="text-white/50 text-sm mt-1">Due this week</p>
                            </div>

                  <div className="bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-sm">
                    <div className="flex items-center justify-between mb-4">
                      <div className="w-12 h-12 rounded-xl bg-gradient-to-r from-orange-500 to-purple-600 flex items-center justify-center">
                        <Trophy className="h-6 w-6 text-white" />
                        </div>
                      <span className="text-2xl font-bold text-white">92%</span>
                        </div>
                    <h3 className="text-white/90 font-medium">Average Grade</h3>
                    <p className="text-white/50 text-sm mt-1">This semester</p>
                </div>

                  <div className="bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-sm">
                    <div className="flex items-center justify-between mb-4">
                      <div className="w-12 h-12 rounded-xl bg-gradient-to-r from-orange-500 to-purple-600 flex items-center justify-center">
                        <Users className="h-6 w-6 text-white" />
                </div>
                      <span className="text-2xl font-bold text-white">{studyGroups.length}</span>
                            </div>
                    <h3 className="text-white/90 font-medium">Study Groups</h3>
                    <p className="text-white/50 text-sm mt-1">Active participation</p>
                            </div>
                        </div>
                        
                {/* Recent Assignments */}
                <div className="bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-sm">
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="text-xl font-semibold text-white">Recent Assignments</h3>
                    <button className="text-orange-400 hover:text-orange-300 transition-colors">
                      View All
                    </button>
                        </div>
                  <div className="space-y-4">
                    {assignments.slice(0, 3).map((assignment) => (
                      <div key={assignment.id} className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/10">
                        <div className="flex-1">
                          <h4 className="font-medium text-white">{assignment.title}</h4>
                          <p className="text-white/60 text-sm">{assignment.subject}</p>
                          </div>
                        <div className="flex items-center space-x-4">
                          <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(assignment.status)}`}>
                            {assignment.status}
                          </span>
                          <button className="p-2 rounded-lg bg-gradient-to-r from-orange-500 to-purple-600 hover:from-orange-600 hover:to-purple-700 transition-all text-white">
                            <Eye className="h-4 w-4" />
                          </button>
                          </div>
                        </div>
                  ))}
                </div>
              </div>

                {/* Course Progress */}
                <div className="bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-sm">
                  <h3 className="text-xl font-semibold text-white mb-6">Course Progress</h3>
                  <div className="space-y-4">
                    {coursesProgress.map((course) => (
                      <div key={course.id} className="space-y-2">
                          <div className="flex justify-between text-sm">
                          <span className="text-white/90">{course.name}</span>
                          <span className="text-white/70">{course.completion}%</span>
                          </div>
                        <div className="w-full bg-white/10 rounded-full h-2">
                          <div 
                            className="h-2 rounded-full bg-gradient-to-r from-orange-500 to-purple-600 transition-all duration-500"
                            style={{ width: `${course.completion}%` }}
                          />
                          </div>
                        </div>
                  ))}
                </div>
              </div>
              </motion.div>
            )}

            {/* Assignments Tab */}
            {activeTab === 'assignments' && (
              <motion.div variants={itemVariants} className="space-y-6">
                <div className="bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-sm">
                  <h3 className="text-xl font-semibold text-white mb-6">All Assignments</h3>
                <div className="space-y-4">
                    {filteredAssignments.map((assignment) => (
                      <div key={assignment.id} className="p-6 bg-white/5 rounded-xl border border-white/10 hover:bg-white/10 transition-all">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex-1">
                            <h4 className="text-lg font-semibold text-white mb-2">{assignment.title}</h4>
                            <p className="text-white/70 mb-2">{assignment.description}</p>
                            <div className="flex items-center space-x-4 text-sm text-white/60">
                              <span>{assignment.subject}</span>
                              <span>Due: {new Date(assignment.dueDate).toLocaleDateString()}</span>
                              {assignment.grade && (
                                <span className="text-green-400">Grade: {assignment.grade}/{assignment.maxGrade}</span>
                              )}
                          </div>
                        </div>
                          <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(assignment.status)}`}>
                            {assignment.status}
                          </span>
                      </div>
                        <div className="flex items-center space-x-3">
                          <button className="px-4 py-2 bg-gradient-to-r from-orange-500 to-purple-600 hover:from-orange-600 hover:to-purple-700 rounded-lg text-white font-medium transition-all">
                            {assignment.status === 'completed' ? 'View Details' : 'Start Assignment'}
                          </button>
                          {assignment.attachments && (
                            <button className="px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg text-white/90 transition-colors">
                              <Download className="h-4 w-4 inline mr-2" />
                              Attachments
                          </button>
                          )}
                        </div>
                      </div>
                  ))}
                </div>
              </div>
              </motion.div>
            )}

            {/* Coding Tests Tab */}
            {activeTab === 'coding' && (
              <motion.div variants={itemVariants} className="space-y-6">
                <div className="bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-sm">
                  <div className="flex items-center justify-between mb-6">
              <div>
                      <h3 className="text-xl font-semibold text-white mb-2">Coding Practice Problems</h3>
                      <p className="text-white/70">Generate personalized problems via AI and practice</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <input value={topicInput} onChange={(e)=>setTopicInput(e.target.value)} placeholder="topic (e.g., arrays)" className="px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white placeholder-white/50 w-40" />
                      <select value={genDifficulty} onChange={(e)=>setGenDifficulty(e.target.value as any)} className="px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white">
                        <option className="bg-[#0f0b14]" value="easy">Easy</option>
                        <option className="bg-[#0f0b14]" value="medium">Medium</option>
                        <option className="bg-[#0f0b14]" value="hard">Hard</option>
                      </select>
                      <button onClick={() => generateNewProblems(genDifficulty, topicInput)} className="px-4 py-2 bg-gradient-to-r from-orange-500 to-purple-600 hover:from-orange-600 hover:to-purple-700 rounded-lg text-white font-medium transition-all disabled:opacity-60" disabled={isGenerating}>
                        <Plus className="h-4 w-4 inline mr-2" />
                        {isGenerating ? 'Generating...' : 'New Problem'}
                      </button>
                    </div>
                </div>

                  {/* Problem Categories */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                    <div className="p-4 bg-white/5 rounded-xl border border-white/10 hover:bg-white/10 transition-all cursor-pointer">
                      <div className="flex items-center space-x-3 mb-3">
                        <div className="w-10 h-10 rounded-lg bg-green-500/20 flex items-center justify-center">
                          <Target className="h-5 w-5 text-green-400" />
                              </div>
                        <div>
                          <div className="text-sm font-medium text-white">Easy</div>
                          <div className="text-xs text-white/60">15 problems</div>
                              </div>
                          </div>
                      <div className="text-xs text-white/70">Basic algorithms and data structures</div>
                        </div>
                        
                    <div className="p-4 bg-white/5 rounded-xl border border-white/10 hover:bg-white/10 transition-all cursor-pointer">
                      <div className="flex items-center space-x-3 mb-3">
                        <div className="w-10 h-10 rounded-lg bg-orange-500/20 flex items-center justify-center">
                          <Target className="h-5 w-5 text-orange-400" />
                        </div>
                        <div>
                          <div className="text-sm font-medium text-white">Medium</div>
                          <div className="text-xs text-white/60">23 problems</div>
                </div>
              </div>
                      <div className="text-xs text-white/70">Advanced algorithms and optimization</div>
                </div>

                    <div className="p-4 bg-white/5 rounded-xl border border-white/10 hover:bg-white/10 transition-all cursor-pointer">
                      <div className="flex items-center space-x-3 mb-3">
                        <div className="w-10 h-10 rounded-lg bg-red-500/20 flex items-center justify-center">
                          <Target className="h-5 w-5 text-red-400" />
                        </div>
              <div>
                          <div className="text-sm font-medium text-white">Hard</div>
                          <div className="text-xs text-white/60">8 problems</div>
                          </div>
                      </div>
                      <div className="text-xs text-white/70">Complex algorithms and system design</div>
                          </div>
                </div>

                  {/* Practice Problems List */}
                  <div className="space-y-4">
                    {[
                      {
                        id: '1',
                        title: 'Two Sum',
                        difficulty: 'Easy',
                        category: 'Arrays',
                        description: 'Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.',
                        solved: true,
                        timeLimit: '2s',
                        memoryLimit: '256MB'
                      },
                      {
                        id: '2',
                        title: 'Valid Parentheses',
                        difficulty: 'Easy',
                        category: 'Stack',
                        description: 'Given a string s containing just the characters \'(\', \')\', \'{\', \'}\', \'[\' and \']\', determine if the input string is valid.',
                        solved: false,
                        timeLimit: '1s',
                        memoryLimit: '128MB'
                      },
                      {
                        id: '3',
                        title: 'Merge Two Sorted Lists',
                        difficulty: 'Easy',
                        category: 'Linked Lists',
                        description: 'Merge two sorted linked lists and return it as a sorted list.',
                        solved: true,
                        timeLimit: '1s',
                        memoryLimit: '128MB'
                      },
                      {
                        id: '4',
                        title: 'Binary Tree Inorder Traversal',
                        difficulty: 'Medium',
                        category: 'Trees',
                        description: 'Given the root of a binary tree, return the inorder traversal of its nodes\' values.',
                        solved: false,
                        timeLimit: '1s',
                        memoryLimit: '128MB'
                      },
                      {
                        id: '5',
                        title: 'Longest Substring Without Repeating Characters',
                        difficulty: 'Medium',
                        category: 'Strings',
                        description: 'Given a string s, find the length of the longest substring without repeating characters.',
                        solved: false,
                        timeLimit: '2s',
                        memoryLimit: '256MB'
                      }
                    ].map((problem) => (
                      <div key={problem.id} className="p-6 bg-white/5 rounded-xl border border-white/10 hover:bg-white/10 transition-all">
                        <div className="flex items-start justify-between mb-4">
                          <div className="flex-1">
                            <div className="flex items-center space-x-3 mb-2">
                              <h4 className="text-lg font-semibold text-white">{problem.title}</h4>
                              <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                problem.difficulty === 'Easy' ? 'bg-green-500/20 text-green-400 border border-green-500/30' :
                                problem.difficulty === 'Medium' ? 'bg-orange-500/20 text-orange-400 border border-orange-500/30' :
                                'bg-red-500/20 text-red-400 border border-red-500/30'
                              }`}>
                                {problem.difficulty}
                          </span>
                              <span className="px-2 py-1 rounded-full text-xs font-medium bg-purple-500/20 text-purple-400 border border-purple-500/30">
                                {problem.category}
                              </span>
                              {problem.solved && (
                                <div className="flex items-center space-x-1 text-green-400">
                                  <CheckCircle className="h-4 w-4" />
                                  <span className="text-xs">Solved</span>
                        </div>
                              )}
                          </div>
                            <p className="text-white/70 text-sm mb-3">{problem.description}</p>
                            <div className="flex items-center space-x-4 text-xs text-white/60">
                              <span>Time: {problem.timeLimit}</span>
                              <span>Memory: {problem.memoryLimit}</span>
                          </div>
                        </div>
                              </div>
                        <div className="flex items-center space-x-3">
                          <button 
                            onClick={() => handleStartPractice(problem)}
                            className="px-4 py-2 bg-gradient-to-r from-orange-500 to-purple-600 hover:from-orange-600 hover:to-purple-700 rounded-lg text-white font-medium transition-all"
                          >
                            {problem.solved ? 'View Solution' : 'Start Practice'}
                          </button>
                          {problem.solved && (
                            <button className="px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg text-white/90 transition-colors">
                              <Eye className="h-4 w-4 inline mr-2" />
                              View Code
                            </button>
                          )}
                          <button className="px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg text-white/90 transition-colors">
                            <Share className="h-4 w-4 inline mr-2" />
                            Share
                          </button>
                          </div>
                        </div>
                  ))}
                </div>
              </div>
                    </motion.div>
            )}

            {/* MCQ Tests Tab */}
            {activeTab === 'mcq' && (
              <motion.div variants={itemVariants} className="space-y-6">
                <div className="bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-sm">
                  <div className="flex items-center justify-between mb-6">
                    <div>
                      <h3 className="text-xl font-semibold text-white mb-2">MCQ Assessments</h3>
                      <p className="text-white/70">Test your knowledge with AI-generated questions</p>
                    </div>
                    <button
                      onClick={() => navigate('/student/mcq')}
                      className="px-6 py-3 bg-gradient-to-r from-orange-500 to-purple-600 hover:from-orange-600 hover:to-purple-700 rounded-lg text-white font-medium transition-all shadow-lg"
                    >
                      Start New Assessment
                    </button>
                  </div>

                  {/* Assessment Categories */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                    <div className="p-4 bg-white/5 rounded-xl border border-white/10 hover:bg-white/10 transition-all cursor-pointer">
                      <div className="flex items-center space-x-3 mb-3">
                        <div className="w-10 h-10 rounded-lg bg-green-500/20 flex items-center justify-center">
                          <Target className="h-5 w-5 text-green-400" />
                        </div>
                        <div>
                          <div className="text-sm font-medium text-white">Easy</div>
                          <div className="text-xs text-white/60">Basic concepts</div>
                        </div>
                      </div>
                      <div className="text-xs text-white/70">Perfect for beginners</div>
                    </div>
                    
                    <div className="p-4 bg-white/5 rounded-xl border border-white/10 hover:bg-white/10 transition-all cursor-pointer">
                      <div className="flex items-center space-x-3 mb-3">
                        <div className="w-10 h-10 rounded-lg bg-orange-500/20 flex items-center justify-center">
                          <Target className="h-5 w-5 text-orange-400" />
                        </div>
                        <div>
                          <div className="text-sm font-medium text-white">Medium</div>
                          <div className="text-xs text-white/60">Intermediate level</div>
                        </div>
                      </div>
                      <div className="text-xs text-white/70">For students with some experience</div>
                    </div>

                    <div className="p-4 bg-white/5 rounded-xl border border-white/10 hover:bg-white/10 transition-all cursor-pointer">
                      <div className="flex items-center space-x-3 mb-3">
                        <div className="w-10 h-10 rounded-lg bg-red-500/20 flex items-center justify-center">
                          <Target className="h-5 w-5 text-red-400" />
                        </div>
                        <div>
                          <div className="text-sm font-medium text-white">Hard</div>
                          <div className="text-xs text-white/60">Advanced concepts</div>
                        </div>
                      </div>
                      <div className="text-xs text-white/70">Challenge yourself</div>
                    </div>
                  </div>

                  {/* Recent Assessments */}
                  <div className="space-y-4">
                    <h4 className="text-lg font-semibold text-white mb-4">Recent Assessments</h4>
                    {[
                      {
                        id: '1',
                        subject: 'Computer Science',
                        topic: 'Operating Systems',
                        difficulty: 'Medium',
                        score: 85,
                        date: '2024-01-15'
                      },
                      {
                        id: '2',
                        subject: 'Mathematics',
                        topic: 'Calculus',
                        difficulty: 'Hard',
                        score: 72,
                        date: '2024-01-12'
                      },
                      {
                        id: '3',
                        subject: 'Physics',
                        topic: 'Mechanics',
                        difficulty: 'Easy',
                        score: 94,
                        date: '2024-01-10'
                      }
                    ].map((assessment) => (
                      <div key={assessment.id} className="p-4 bg-white/5 rounded-xl border border-white/10 hover:bg-white/10 transition-all">
                        <div className="flex items-center justify-between">
                          <div className="flex-1">
                            <div className="flex items-center space-x-3 mb-2">
                              <h5 className="font-medium text-white">{assessment.subject}</h5>
                              <span className="px-2 py-1 rounded-full text-xs font-medium bg-purple-500/20 text-purple-400 border border-purple-500/30">
                                {assessment.topic}
                              </span>
                              <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                assessment.difficulty === 'Easy' ? 'bg-green-500/20 text-green-400 border border-green-500/30' :
                                assessment.difficulty === 'Medium' ? 'bg-orange-500/20 text-orange-400 border border-orange-500/30' :
                                'bg-red-500/20 text-red-400 border border-red-500/30'
                              }`}>
                                {assessment.difficulty}
                              </span>
                            </div>
                            <div className="text-sm text-white/60">Completed on {assessment.date}</div>
                          </div>
                          <div className="text-right">
                            <div className="text-2xl font-bold text-white">{assessment.score}%</div>
                            <div className="text-xs text-white/60">Score</div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </motion.div>
            )}

            {activeTab === 'leaderboard' && (
              <motion.div variants={itemVariants} className="space-y-6">
                <div className="bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-sm">
                  <div className="flex items-center justify-between mb-6">
                    <div>
                      <h3 className="text-xl font-semibold text-white mb-2">Leaderboard</h3>
                      <p className="text-white/70">Top scores across recent MCQ assessments</p>
                    </div>
                    <button onClick={fetchLeaderboard} className="px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg text-white/90">Refresh</button>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="min-w-full text-sm text-white/90">
                      <thead>
                        <tr className="text-left text-white/60 border-b border-white/10">
                          <th className="py-2 pr-4">Rank</th>
                          <th className="py-2 pr-4">Name</th>
                          <th className="py-2 pr-4">Subject</th>
                          <th className="py-2 pr-4">Topic</th>
                          <th className="py-2 pr-4">Difficulty</th>
                          <th className="py-2 pr-4">Score</th>
                          <th className="py-2 pr-4">Date</th>
                        </tr>
                      </thead>
                      <tbody>
                        {leaderboard.map((e, idx) => (
                          <tr key={e.id || idx} className="border-b border-white/5">
                            <td className="py-2 pr-4">{idx + 1}</td>
                            <td className="py-2 pr-4">{e.user_name}</td>
                            <td className="py-2 pr-4">{e.subject}</td>
                            <td className="py-2 pr-4">{e.topic}</td>
                            <td className="py-2 pr-4">{(e.difficulty || '').toString().toUpperCase()}</td>
                            <td className="py-2 pr-4">{e.score}/{e.total} ({e.percentage}%)</td>
                            <td className="py-2 pr-4">{new Date(e.created_at).toLocaleString()}</td>
                          </tr>
                        ))}
                        {leaderboard.length === 0 && (
                          <tr>
                            <td className="py-8 text-center text-white/60" colSpan={7}>No results yet.</td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>
              </motion.div>
            )}

            {/* Other tabs would go here with similar styling */}
            {activeTab === 'materials' && (
              <motion.div variants={itemVariants} className="bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-sm">
                <h3 className="text-xl font-semibold text-white mb-6">Study Materials</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {studyMaterials.map(m => (
                    <div key={m.id} className="p-4 bg-white/5 rounded-xl border border-white/10 hover:bg-white/10 transition-all">
                      <div className="flex items-center justify-between mb-2">
                        <div className="text-white font-medium">{m.title}</div>
                        <span className="px-2 py-1 rounded-full text-xs font-medium bg-purple-500/20 text-purple-400 border border-purple-500/30">{m.type.toUpperCase()}</span>
                      </div>
                      <div className="text-sm text-white/60 mb-2">{m.subject} • {m.uploadDate}</div>
                      <p className="text-white/70 text-sm mb-3">{m.description}</p>
                      <div className="flex items-center gap-2 text-xs text-white/60">
                        {m.tags?.map(tag => (
                          <span key={tag} className="px-2 py-0.5 rounded bg-white/10 border border-white/10">#{tag}</span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}

            {activeTab === 'labs' && (
              <motion.div variants={itemVariants} className="bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-sm">
                <h3 className="text-xl font-semibold text-white mb-6">Virtual Labs</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {virtualLabs.map(lab => (
                    <div key={lab.id} className="p-4 bg-white/5 rounded-xl border border-white/10 hover:bg-white/10 transition-all">
                      <div className="flex items-center justify-between mb-2">
                        <div className="text-white font-medium">{lab.title}</div>
                        <span className="px-2 py-1 rounded-full text-xs font-medium bg-purple-500/20 text-purple-400 border border-purple-500/30">{lab.type}</span>
                      </div>
                      <div className="text-sm text-white/60 mb-2">{lab.subject} • {lab.difficulty}</div>
                      <p className="text-white/70 text-sm mb-3">{lab.description}</p>
                      <div className="text-xs text-white/60">Estimated: {lab.estimatedTime} mins</div>
                      <div className="mt-2">
                        <div className="text-xs text-white/60 mb-1">Learning outcomes:</div>
                        <div className="flex flex-wrap gap-2">
                          {lab.learningOutcomes.map(out => (
                            <span key={out} className="px-2 py-0.5 rounded bg-white/10 border border-white/10 text-xs text-white/70">{out}</span>
                          ))}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}

            {activeTab === 'discussions' && (
              <motion.div variants={itemVariants} className="bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-sm">
                <h3 className="text-xl font-semibold text-white mb-6">Discussions</h3>
                <div className="space-y-3">
                  {discussions.map(d => (
                    <div key={d.id} className="p-4 bg-white/5 rounded-xl border border-white/10 hover:bg-white/10 transition-all">
                      <div className="flex items-center justify-between mb-1">
                        <div className="text-white font-medium">{d.title}</div>
                        <div className="text-xs text-white/50">{d.lastActivity}</div>
                      </div>
                      <div className="text-sm text-white/60 mb-2">{d.subject} • by {d.author} • {d.participants} participants</div>
                      <div className="flex flex-wrap gap-2">
                        {d.tags.map(tag => (
                          <span key={tag} className="px-2 py-0.5 rounded bg-white/10 border border-white/10 text-xs text-white/70">#{tag}</span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}

            {activeTab === 'groups' && (
              <motion.div variants={itemVariants} className="bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-sm">
                <h3 className="text-xl font-semibold text-white mb-6">Study Groups</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {studyGroups.map(g => (
                    <div key={g.id} className="p-4 bg-white/5 rounded-xl border border-white/10 hover:bg-white/10 transition-all">
                      <div className="flex items-center justify-between mb-1">
                        <div className="text-white font-medium">{g.name}</div>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${g.status === 'active' ? 'bg-green-500/20 text-green-400 border border-green-500/30' : 'bg-gray-500/20 text-gray-300 border border-gray-500/30'}`}>{g.status}</span>
                      </div>
                      <div className="text-sm text-white/60 mb-2">{g.subject} • {g.members}/{g.maxMembers} members</div>
                      <p className="text-white/70 text-sm">{g.description}</p>
                      <div className="text-xs text-white/60 mt-2">{g.meetingTime}</div>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}

            {activeTab === 'projects' && (
              <motion.div variants={itemVariants} className="bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-sm">
                <h3 className="text-xl font-semibold text-white mb-6">Projects</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {projects.map(p => (
                    <div key={p.id} className="p-4 bg-white/5 rounded-xl border border-white/10 hover:bg-white/10 transition-all">
                      <div className="flex items-center justify-between mb-1">
                        <div className="text-white font-medium">{p.title}</div>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${p.status === 'completed' ? 'bg-green-500/20 text-green-400 border border-green-500/30' : 'bg-orange-500/20 text-orange-400 border border-orange-500/30'}`}>{p.status}</span>
                      </div>
                      <p className="text-white/70 text-sm mb-3">{p.description}</p>
                      <div className="w-full bg-white/10 rounded-full h-2">
                        <div className="h-2 rounded-full bg-gradient-to-r from-orange-500 to-purple-600 transition-all duration-500" style={{ width: `${p.progress}%` }} />
                      </div>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}

            {activeTab === 'internships' && (
              <motion.div variants={itemVariants} className="bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-sm">
                <h3 className="text-xl font-semibold text-white mb-6">Internships</h3>
                <div className="space-y-3">
                  {internships.map(i => (
                    <div key={i.id} className="p-4 bg-white/5 rounded-xl border border-white/10 hover:bg-white/10 transition-all">
                      <div className="flex items-center justify-between mb-1">
                        <div className="text-white font-medium">{i.company} • {i.position}</div>
                        <span className="px-2 py-1 rounded-full text-xs font-medium bg-purple-500/20 text-purple-400 border border-purple-500/30">{i.status}</span>
                      </div>
                      <div className="text-sm text-white/60">Deadline: {i.deadline}</div>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}

            {activeTab === 'notes' && (
              <motion.div variants={itemVariants} className="bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-sm">
                <h3 className="text-xl font-semibold text-white mb-6">My Notes</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {notes.map(n => (
                    <div key={n.id} className="p-4 bg-white/5 rounded-xl border border-white/10 hover:bg-white/10 transition-all">
                      <div className="text-white font-medium mb-1">{n.title}</div>
                      <div className="text-sm text-white/60 mb-2">{n.subject} • Last modified: {n.lastModified}</div>
                      <div className="flex flex-wrap gap-2">
                        {n.tags.map(tag => (
                          <span key={tag} className="px-2 py-0.5 rounded bg-white/10 border border-white/10 text-xs text-white/70">#{tag}</span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}

            {activeTab === 'library' && (
              <motion.div variants={itemVariants} className="bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-sm">
                <h3 className="text-xl font-semibold text-white mb-6">Library</h3>
                <div className="overflow-x-auto">
                  <table className="min-w-full text-sm text-white/80">
                    <thead>
                      <tr className="text-left text-white/60 border-b border-white/10">
                        <th className="py-2 pr-4">Title</th>
                        <th className="py-2 pr-4">Author</th>
                        <th className="py-2 pr-4">Subject</th>
                        <th className="py-2 pr-4">Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {libraryBooks.map(b => (
                        <tr key={b.id} className="border-b border-white/5">
                          <td className="py-2 pr-4">{b.title}</td>
                          <td className="py-2 pr-4">{b.author}</td>
                          <td className="py-2 pr-4">{b.subject}</td>
                          <td className="py-2 pr-4">
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${b.status === 'available' ? 'bg-green-500/20 text-green-400 border border-green-500/30' : 'bg-orange-500/20 text-orange-400 border border-orange-500/30'}`}>{b.status}</span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </motion.div>
            )}

            {activeTab === 'certificates' && (
              <motion.div variants={itemVariants} className="bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-sm">
                <h3 className="text-xl font-semibold text-white mb-6">Certificates</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {certificates.map(c => (
                    <div key={c.id} className="p-4 bg-white/5 rounded-xl border border-white/10 hover:bg-white/10 transition-all">
                      <div className="text-white font-medium mb-1">{c.name}</div>
                      <div className="text-sm text-white/60 mb-1">Issuer: {c.issuer}</div>
                      <div className="text-sm text-white/60">Date: {c.date}</div>
                      <div className="mt-3">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${c.status === 'completed' ? 'bg-green-500/20 text-green-400 border border-green-500/30' : 'bg-gray-500/20 text-gray-300 border border-gray-500/30'}`}>{c.status}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}
                </div>

          {/* Sidebar */}
          <div className="space-y-8">
            {/* AI Study Planner */}
            <motion.div variants={itemVariants} className="bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-sm">
              <div className="flex items-center space-x-2 mb-4">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-r from-orange-500 to-purple-600 flex items-center justify-center">
                  <Brain className="h-4 w-4 text-white" />
                        </div>
                <h3 className="text-lg font-semibold text-white">AI Study Planner</h3>
                          </div>
              <div className="space-y-3">
                {aiStudyPlanner.map((item, index) => (
                  <div key={index} className="flex items-start space-x-3 p-3 bg-white/5 rounded-lg">
                    <div className="w-2 h-2 rounded-full bg-orange-400 mt-2 flex-shrink-0" />
                    <div>
                      <div className="text-xs text-orange-400 font-medium mb-1">{item.type}</div>
                      <div className="text-sm text-white/90">{item.text}</div>
                        </div>
                        </div>
                          ))}
                        </div>
            </motion.div>

            {/* Upcoming Deadlines */}
            <motion.div variants={itemVariants} className="bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-sm">
              <h3 className="text-lg font-semibold text-white mb-4">Upcoming Deadlines</h3>
              <div className="space-y-3">
                {upcomingTasks.map((task) => (
                  <div key={task.id} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
              <div>
                      <div className="text-sm font-medium text-white">{task.title}</div>
                      <div className="text-xs text-white/60">Due: {task.due.toLocaleDateString()}</div>
                          </div>
                    <button className="p-2 rounded-lg bg-gradient-to-r from-orange-500 to-purple-600 hover:from-orange-600 hover:to-purple-700 transition-all text-white">
                      <Play className="h-4 w-4" />
                    </button>
                        </div>
                          ))}
                        </div>
                    </motion.div>

            {/* Recent Grades */}
            <motion.div variants={itemVariants} className="bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-sm">
              <h3 className="text-lg font-semibold text-white mb-4">Recent Grades</h3>
              <div className="space-y-3">
                {recentGrades.map((grade) => (
                  <div key={grade.id} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                    <div>
                      <div className="text-sm font-medium text-white">{grade.assignment}</div>
                      <div className="text-xs text-white/60">{grade.subject}</div>
                        </div>
                    <div className="text-right">
                      <div className="text-sm font-bold text-green-400">{grade.grade}/{grade.maxGrade}</div>
                      <div className="text-xs text-white/60">{grade.date}</div>
                        </div>
                  </div>
                  ))}
                </div>
            </motion.div>
              </div>
          </motion.div>
      </main>

      {/* Coding Environment Modal */}
      <AnimatePresence>
        {showCodingEnvironment && selectedProblem && (
          <CodingEnvironment
            problem={{
              id: selectedProblem.id,
              title: selectedProblem.title,
              difficulty: selectedProblem.difficulty,
              category: selectedProblem.category,
              description: selectedProblem.description,
              examples: [
                {
                  input: 'nums = [2,7,11,15], target = 9',
                  output: '[0,1]',
                  explanation: 'Because nums[0] + nums[1] == 9, we return [0, 1].'
                },
                {
                  input: 'nums = [3,2,4], target = 6',
                  output: '[1,2]',
                  explanation: 'Because nums[1] + nums[2] == 6, we return [1, 2].'
                }
              ],
              constraints: [
                '2 <= nums.length <= 10^4',
                '-10^9 <= nums[i] <= 10^9',
                '-10^9 <= target <= 10^9',
                'Only one valid answer exists.'
              ],
              starterCode: {
                javascript: `/**
 * @param {number[]} nums
 * @param {number} target
 * @return {number[]}
 */
function twoSum(nums, target) {
    // Your code here
}`,
                python: `class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        # Your code here
        pass`,
                java: `class Solution {
    public int[] twoSum(int[] nums, int target) {
        // Your code here
    }
}`,
                cpp: `class Solution {
public:
    vector<int> twoSum(vector<int>& nums, int target) {
        // Your code here
    }
};`,
                csharp: `public class Solution {
    public int[] TwoSum(int[] nums, int target) {
        // Your code here
    }
}`,
                go: `func twoSum(nums []int, target int) []int {
    // Your code here
}`,
                rust: `impl Solution {
    pub fn two_sum(nums: Vec<i32>, target: i32) -> Vec<i32> {
        // Your code here
    }
}`,
                php: `class Solution {
    function twoSum($nums, $target) {
        // Your code here
    }
}`
              },
              testCases: [
                { input: '[2,7,11,15], 9', output: '[0,1]', isHidden: false },
                { input: '[3,2,4], 6', output: '[1,2]', isHidden: false },
                { input: '[3,3], 6', output: '[0,1]', isHidden: false }
              ]
            }}
            onClose={handleCloseCodingEnvironment}
            onGenerateNew={generateNewProblems}
          />
        )}
        {showSettings && (
          <motion.div onClick={() => setShowSettings(false)} initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
            <div onClick={(e)=>e.stopPropagation()} className="w-full max-w-3xl bg-[#0f0b14] border border-white/10 rounded-2xl shadow-2xl overflow-hidden">
              <div className="p-4 border-b border-white/10 flex items-center justify-between">
                <h3 className="text-lg font-semibold text-white">Profile & Settings</h3>
                <button onClick={() => setShowSettings(false)} className="text-white/60 hover:text-white">✕</button>
              </div>
              <div className="p-6 space-y-8">
              <div>
                    <h4 className="text-white font-semibold mb-4">Profile</h4>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-xs text-white/60 mb-1">Name</label>
                        <input value={profileForm.name} onChange={e=>setProfileForm({...profileForm,name:e.target.value})} className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white" />
                </div>
                      <div>
                        <label className="block text-xs text-white/60 mb-1">Email</label>
                        <input value={profileForm.email} onChange={e=>setProfileForm({...profileForm,email:e.target.value})} className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white" />
                          </div>
                      <div>
                        <label className="block text-xs text-white/60 mb-1">Role</label>
                        <input disabled value={profileForm.role} className="w-full px-3 py-2 bg-white/10 border border-white/10 rounded-lg text-white" />
                          </div>
                      <div>
                        <label className="block text-xs text-white/60 mb-1">Section</label>
                        <select value={profileForm.section} onChange={e=>setProfileForm({...profileForm,section:e.target.value})} className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white">
                          <option className="bg-[#0f0b14]" value="A">A</option>
                          <option className="bg-[#0f0b14]" value="B">B</option>
                          <option className="bg-[#0f0b14]" value="C">C</option>
                        </select>
                        </div>
                        </div>
                </div>
                  <div>
                    <h4 className="text-white font-semibold mb-4">Preferences</h4>
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                      <div>
                        <label className="block text-xs text-white/60 mb-1">Theme</label>
                        <select value={prefsForm.theme} onChange={e=>setPrefsForm({...prefsForm,theme:e.target.value})} className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white">
                          <option className="bg-[#0f0b14]" value="dark">Dark</option>
                          <option className="bg-[#0f0b14]" value="light">Light</option>
                        </select>
              </div>
              <div>
                        <label className="block text-xs text-white/60 mb-1">Language</label>
                        <select value={prefsForm.language} onChange={e=>setPrefsForm({...prefsForm,language:e.target.value})} className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white">
                          <option className="bg-[#0f0b14]" value="en">English</option>
                          <option className="bg-[#0f0b14]" value="hi">Hindi</option>
                        </select>
                </div>
                      <div className="flex items-end">
                        <label className="inline-flex items-center space-x-2">
                          <input type="checkbox" checked={prefsForm.notifications} onChange={e=>setPrefsForm({...prefsForm,notifications:e.target.checked})} />
                          <span className="text-white/80">Enable notifications</span>
                        </label>
                          </div>
                        </div>
                        </div>
                  <div>
                    <h4 className="text-white font-semibold mb-4">Security</h4>
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                      <input type="password" placeholder="Current password" value={securityForm.current} onChange={e=>setSecurityForm({...securityForm,current:e.target.value})} className="px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white" />
                      <input type="password" placeholder="New password" value={securityForm.next} onChange={e=>setSecurityForm({...securityForm,next:e.target.value})} className="px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white" />
                      <input type="password" placeholder="Confirm password" value={securityForm.confirm} onChange={e=>setSecurityForm({...securityForm,confirm:e.target.value})} className="px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white" />
                        </div>
                        </div>
                  <div className="flex justify-between pt-2">
                    <button onClick={() => { localStorage.setItem('user', JSON.stringify({ ...user, ...profileForm })); setShowSettings(false); }} className="px-4 py-2 rounded-lg bg-gradient-to-r from-orange-500 to-purple-600 text-white">Save</button>
                    <button onClick={handleLogout} className="px-4 py-2 rounded-lg bg-white/10 text-white/80 hover:bg-white/15">Logout</button>
                </div>
              </div>
            </div>
          </motion.div>
        )}
        </AnimatePresence>
    </div>
  );
};
