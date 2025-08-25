export interface User {
  id: string;
  name: string;
  email: string;
  role: 'student' | 'teacher';
  avatar?: string;
  department?: string;
  section?: string;
  year?: number;
  semester?: number;
  rollNumber?: string;
  phone?: string;
  address?: string;
}

export interface Assignment {
  id: string;
  title: string;
  subject: string;
  description: string;
  dueDate: string;
  status: 'pending' | 'completed' | 'overdue' | 'submitted';
  grade?: number;
  maxGrade: number;
  attachments?: string[];
  submissionDate?: string;
  feedback?: string;
  aiGraded?: boolean;
}

export interface CodingProblem {
  id: string;
  title: string;
  difficulty: 'Easy' | 'Medium' | 'Hard';
  description: string;
  examples: {
    input: string;
    output: string;
    explanation?: string;
  }[];
  constraints: string[];
  testCases: {
    input: string;
    expectedOutput: string;
  }[];
  starterCode: {
    [language: string]: string;
  };
}

export interface MCQTest {
  id: string;
  title: string;
  subject: string;
  questions: MCQQuestion[];
  duration: number;
  totalMarks: number;
  dueDate: string;
  status: 'pending' | 'completed' | 'in-progress';
  attempts?: number;
  maxAttempts: number;
}

export interface MCQQuestion {
  id: string;
  question: string;
  options: string[];
  correctAnswer: number;
  explanation?: string;
  marks: number;
}

export interface StudyMaterial {
  id: string;
  title: string;
  subject: string;
  type: 'pdf' | 'video' | 'article' | 'presentation';
  url: string;
  description: string;
  uploadDate: string;
  size?: string;
  duration?: string;
  tags: string[];
}

export interface VirtualLab {
  id: string;
  title: string;
  subject: string;
  description: string;
  type: 'simulation' | 'coding' | 'experiment';
  difficulty: 'Beginner' | 'Intermediate' | 'Advanced';
  estimatedTime: number;
  prerequisites: string[];
  learningOutcomes: string[];
}

export interface Discussion {
  id: string;
  title: string;
  subject: string;
  author: string;
  // Optional rich fields for full threads
  content?: string;
  authorId?: string;
  createdAt?: string;
  replies?: DiscussionReply[];
  likes?: number;
  views?: number;
  // Dashboard list helpers
  participants?: number;
  lastActivity?: string;
  tags: string[];
}

export interface DiscussionReply {
  id: string;
  content: string;
  author: string;
  authorId: string;
  createdAt: string;
  likes: number;
}

export interface Attendance {
  id: string;
  subject: string;
  date: string;
  status: 'present' | 'absent' | 'late';
  duration?: number;
  topic?: string;
}

export interface Grade {
  id: string;
  subject: string;
  assignment: string;
  grade: number;
  maxGrade: number;
  date: string;
  feedback?: string;
}

export interface StudyGroup {
  id: string;
  name: string;
  subject: string;
  description: string;
  // Dashboard summary
  members: number;
  maxMembers?: number;
  status?: 'active' | 'inactive';
  meetingTime?: string;
  // Detailed fields (optional)
  createdBy?: string;
  createdAt?: string;
  meetingLink?: string;
  nextMeeting?: string;
}

export interface Certificate {
  id: string;
  name: string;
  issuer: string;
  date: string;
  status: 'completed' | 'in-progress';
}

export interface Project {
  id: string;
  title: string;
  description: string;
  subject: string;
  teamMembers: string[];
  status: 'planning' | 'in-progress' | 'completed' | 'submitted';
  dueDate: string;
  progress: number;
  repository?: string;
  documentation?: string[];
}

export interface Internship {
  id: string;
  company: string;
  position: string;
  description?: string;
  requirements?: string[];
  duration?: string;
  stipend?: string;
  location?: string;
  applicationDeadline?: string;
  deadline?: string;
  status: 'open' | 'applied' | 'interview' | 'closed';
}

export interface StudentProgress {
  studentId: string;
  studentName: string;
  averageGrade: number;
  completedAssignments: number;
  totalAssignments: number;
  attendancePercentage: number;
  weakAreas: string[];
  strengths: string[];
  lastActivity: string;
  totalStudyHours: number;
  projectsCompleted: number;
  certificatesEarned: number;
}

export interface CalendarEvent {
  id: string;
  title: string;
  description?: string;
  date: string;
  time: string;
  type: 'assignment' | 'exam' | 'class' | 'meeting' | 'event';
  subject?: string;
  location?: string;
}

export interface Note {
  id: string;
  title: string;
  subject: string;
  content?: string;
  tags: string[];
  createdAt?: string;
  updatedAt?: string;
  lastModified?: string;
  isShared?: boolean;
}

export interface LibraryBook {
  id: string;
  title: string;
  author: string;
  subject: string;
  isbn?: string;
  description?: string;
  availableCopies?: number;
  totalCopies?: number;
  dueDate?: string;
  status: 'available' | 'borrowed' | 'reserved';
}

// Additional shared models
export interface Announcement {
  id: string;
  title: string;
  content: string;
  audience: 'global' | 'course' | 'section';
  createdAt: string;
  read?: boolean;
  author?: string;
}

export interface CourseSummary {
  id: string;
  name: string;
  completion: number; // 0-100
  lastLesson: string;
  learningStyle?: 'visual' | 'analytical' | 'auditory' | 'kinesthetic';
}

// Updated LeaderboardEntry interface (merged the two versions)
export interface LeaderboardEntry {
  rank: number;
  studentId: string;
  studentName: string;
  score: number;
  timeSpent?: number;
  kindnessPoints?: number;
  avatar?: string;
}
