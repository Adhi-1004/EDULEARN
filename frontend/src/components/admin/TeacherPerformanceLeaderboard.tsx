import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import Card from "../ui/Card";
import Button from "../ui/Button";
import LoadingSpinner from "../ui/LoadingSpinner";
import api from "../../utils/api";

interface TeacherPerformance {
  id: string;
  name: string;
  email: string;
  totalStudents: number;
  averageStudentScore: number;
  contentContributions: number;
  assessmentsCreated: number;
  questionsCreated: number;
  codingProblemsCreated: number;
  studentSatisfaction: number;
  lastActive: string;
  batches: Array<{
    id: string;
    name: string;
    studentCount: number;
    averageScore: number;
  }>;
  achievements: string[];
  performanceScore: number;
}

interface TeacherPerformanceLeaderboardProps {
  adminId: string;
}

const TeacherPerformanceLeaderboard: React.FC<TeacherPerformanceLeaderboardProps> = ({ adminId }) => {
  const [teachers, setTeachers] = useState<TeacherPerformance[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sortBy, setSortBy] = useState<'performance' | 'students' | 'contributions' | 'satisfaction'>('performance');
  const [filterBy, setFilterBy] = useState<'all' | 'active' | 'top-contributors'>('all');

  useEffect(() => {
    fetchTeacherPerformance();
  }, [adminId]);

  const fetchTeacherPerformance = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/api/admin-dashboard/teacher-performance/${adminId}`);
      setTeachers(response.data);
    } catch (err) {
      console.error("Failed to fetch teacher performance:", err);
      setError("Failed to load teacher performance data");
    } finally {
      setLoading(false);
    }
  };

  const getPerformanceColor = (score: number) => {
    if (score >= 90) return "text-green-400";
    if (score >= 70) return "text-yellow-400";
    if (score >= 50) return "text-orange-400";
    return "text-red-400";
  };

  const getPerformanceBgColor = (score: number) => {
    if (score >= 90) return "bg-green-500/20 border-green-500/30";
    if (score >= 70) return "bg-yellow-500/20 border-yellow-500/30";
    if (score >= 50) return "bg-orange-500/20 border-orange-500/30";
    return "bg-red-500/20 border-red-500/30";
  };

  const getRankIcon = (index: number) => {
    if (index === 0) return "🥇";
    if (index === 1) return "🥈";
    if (index === 2) return "🥉";
    return `#${index + 1}`;
  };

  const getRankColor = (index: number) => {
    if (index === 0) return "text-yellow-400";
    if (index === 1) return "text-gray-400";
    if (index === 2) return "text-orange-400";
    return "text-purple-400";
  };

  const sortedTeachers = [...teachers].sort((a, b) => {
    switch (sortBy) {
      case 'performance':
        return b.performanceScore - a.performanceScore;
      case 'students':
        return b.totalStudents - a.totalStudents;
      case 'contributions':
        return b.contentContributions - a.contentContributions;
      case 'satisfaction':
        return b.studentSatisfaction - a.studentSatisfaction;
      default:
        return 0;
    }
  });

  const filteredTeachers = sortedTeachers.filter(teacher => {
    switch (filterBy) {
      case 'active':
        const daysSinceActive = (Date.now() - new Date(teacher.lastActive).getTime()) / (1000 * 60 * 60 * 24);
        return daysSinceActive <= 7;
      case 'top-contributors':
        return teacher.contentContributions >= 10;
      default:
        return true;
    }
  });

  if (loading) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center h-64">
          <LoadingSpinner />
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="p-6">
        <div className="text-center text-red-400">
          <p>{error}</p>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={fetchTeacherPerformance}
            className="mt-4"
          >
            Retry
          </Button>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-purple-200 mb-2">
          🏆 Teacher Performance & Contribution Leaderboard
        </h2>
        <p className="text-purple-300">
          Track and recognize top-performing teachers and content contributors
        </p>
      </div>

      {/* Controls */}
      <Card className="p-6">
        <div className="flex flex-wrap gap-4 items-center justify-between">
          <div className="flex flex-wrap gap-2">
            <span className="text-purple-300 font-medium">Sort by:</span>
            <Button
              variant={sortBy === 'performance' ? 'primary' : 'outline'}
              size="sm"
              onClick={() => setSortBy('performance')}
            >
              Performance Score
            </Button>
            <Button
              variant={sortBy === 'students' ? 'primary' : 'outline'}
              size="sm"
              onClick={() => setSortBy('students')}
            >
              Student Count
            </Button>
            <Button
              variant={sortBy === 'contributions' ? 'primary' : 'outline'}
              size="sm"
              onClick={() => setSortBy('contributions')}
            >
              Contributions
            </Button>
            <Button
              variant={sortBy === 'satisfaction' ? 'primary' : 'outline'}
              size="sm"
              onClick={() => setSortBy('satisfaction')}
            >
              Satisfaction
            </Button>
          </div>
          
          <div className="flex flex-wrap gap-2">
            <span className="text-purple-300 font-medium">Filter:</span>
            <Button
              variant={filterBy === 'all' ? 'primary' : 'outline'}
              size="sm"
              onClick={() => setFilterBy('all')}
            >
              All Teachers
            </Button>
            <Button
              variant={filterBy === 'active' ? 'primary' : 'outline'}
              size="sm"
              onClick={() => setFilterBy('active')}
            >
              Active (7 days)
            </Button>
            <Button
              variant={filterBy === 'top-contributors' ? 'primary' : 'outline'}
              size="sm"
              onClick={() => setFilterBy('top-contributors')}
            >
              Top Contributors
            </Button>
          </div>
        </div>
      </Card>

      {/* Leaderboard */}
      <div className="space-y-4">
        {filteredTeachers.map((teacher, index) => (
          <motion.div
            key={teacher.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <Card className={`p-6 ${index < 3 ? 'ring-2 ring-purple-400/50' : ''}`}>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-4">
                  <div className={`text-2xl font-bold ${getRankColor(index)}`}>
                    {getRankIcon(index)}
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold text-purple-200">
                      {teacher.name}
                    </h3>
                    <p className="text-purple-400">{teacher.email}</p>
                  </div>
                </div>
                <div className="text-right">
                  <div className={`text-2xl font-bold ${getPerformanceColor(teacher.performanceScore)}`}>
                    {teacher.performanceScore.toFixed(1)}
                  </div>
                  <div className="text-sm text-purple-400">Performance Score</div>
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                <div className="text-center">
                  <div className="text-lg font-semibold text-purple-200">
                    {teacher.totalStudents}
                  </div>
                  <div className="text-sm text-purple-400">Students</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-semibold text-purple-200">
                    {teacher.averageStudentScore.toFixed(1)}%
                  </div>
                  <div className="text-sm text-purple-400">Avg Score</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-semibold text-purple-200">
                    {teacher.contentContributions}
                  </div>
                  <div className="text-sm text-purple-400">Contributions</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-semibold text-purple-200">
                    {teacher.studentSatisfaction.toFixed(1)}%
                  </div>
                  <div className="text-sm text-purple-400">Satisfaction</div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h4 className="font-semibold text-purple-200 mb-2">Content Created</h4>
                  <div className="flex gap-4 text-sm">
                    <span className="text-purple-300">
                      <span className="font-semibold">{teacher.assessmentsCreated}</span> Assessments
                    </span>
                    <span className="text-purple-300">
                      <span className="font-semibold">{teacher.questionsCreated}</span> Questions
                    </span>
                    <span className="text-purple-300">
                      <span className="font-semibold">{teacher.codingProblemsCreated}</span> Coding Problems
                    </span>
                  </div>
                </div>
                
                <div>
                  <h4 className="font-semibold text-purple-200 mb-2">Batches</h4>
                  <div className="text-sm text-purple-300">
                    {teacher.batches.length} batches • {teacher.batches.reduce((sum, batch) => sum + batch.studentCount, 0)} total students
                  </div>
                </div>
              </div>

              {teacher.achievements.length > 0 && (
                <div className="mt-4">
                  <h4 className="font-semibold text-purple-200 mb-2">Achievements</h4>
                  <div className="flex flex-wrap gap-2">
                    {teacher.achievements.map((achievement, idx) => (
                      <span 
                        key={idx}
                        className="px-2 py-1 bg-purple-500/20 text-purple-300 text-xs rounded-full"
                      >
                        {achievement}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              <div className="mt-4 flex gap-2">
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => {
                    // View teacher details
                    console.log("View teacher details:", teacher.id);
                  }}
                >
                  View Details
                </Button>
                <Button 
                  variant="primary" 
                  size="sm"
                  onClick={() => {
                    // Send recognition
                    console.log("Send recognition to:", teacher.id);
                  }}
                >
                  Send Recognition
                </Button>
              </div>
            </Card>
          </motion.div>
        ))}
      </div>

      {filteredTeachers.length === 0 && (
        <Card className="p-8 text-center">
          <div className="text-purple-300">
            <p className="text-lg mb-4">No teachers found</p>
            <p>Try adjusting your filter criteria</p>
          </div>
        </Card>
      )}
    </div>
  );
};

export default TeacherPerformanceLeaderboard;
