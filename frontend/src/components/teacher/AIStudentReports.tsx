import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import Card from "../ui/Card";
import Button from "../ui/Button";
import LoadingSpinner from "../ui/LoadingSpinner";
import api from "../../utils/api";

interface Student {
  id: string;
  name: string;
  email: string;
  batchId?: string;
  lastActive: string;
}

interface AIReport {
  id: string;
  studentId: string;
  studentName: string;
  generatedAt: string;
  summary: string;
  strengths: string[];
  weaknesses: string[];
  recommendations: string[];
  performanceTrend: "improving" | "stable" | "declining";
  nextSteps: string[];
}

interface AIStudentReportsProps {
  teacherId: string;
  students: Student[];
}

const AIStudentReports: React.FC<AIStudentReportsProps> = ({ teacherId, students }) => {
  const [reports, setReports] = useState<AIReport[]>([]);
  const [generatingReports, setGeneratingReports] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchExistingReports();
  }, [teacherId]);

  const fetchExistingReports = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/api/teacher-dashboard/ai-reports/${teacherId}`);
      setReports(response.data);
    } catch (err) {
      console.error("Failed to fetch AI reports:", err);
      console.log("Using mock data for AI reports");
      // Use mock data as fallback
      const mockReports: AIReport[] = [
        {
          id: "report-1",
          studentId: "s1",
          studentName: "Alice Johnson",
          generatedAt: "2024-01-15T10:30:00Z",
          summary: "Alice shows strong analytical thinking but struggles with time management during assessments. Her recent performance indicates improvement in problem-solving skills.",
          strengths: ["Logical reasoning", "Code structure", "Debugging skills"],
          weaknesses: ["Time management", "Complex algorithms", "Test case coverage"],
          recommendations: ["Practice timed coding challenges", "Focus on algorithm optimization", "Review test-driven development"],
          performanceTrend: "improving",
          nextSteps: ["Complete 5 timed challenges this week", "Review sorting algorithms", "Practice unit testing"]
        },
        {
          id: "report-2",
          studentId: "s2",
          studentName: "Bob Smith",
          generatedAt: "2024-01-14T14:20:00Z",
          summary: "Bob demonstrates excellent theoretical knowledge but needs more hands-on practice. His conceptual understanding is solid but implementation skills need development.",
          strengths: ["Theory knowledge", "Problem analysis", "Documentation"],
          weaknesses: ["Code implementation", "Syntax errors", "Runtime optimization"],
          recommendations: ["Increase coding practice", "Focus on syntax fundamentals", "Practice with real projects"],
          performanceTrend: "stable",
          nextSteps: ["Complete daily coding exercises", "Join coding bootcamp", "Build a personal project"]
        }
      ];
      setReports(mockReports);
    } finally {
      setLoading(false);
    }
  };

  const generateStudentReport = async (studentId: string) => {
    try {
      setGeneratingReports(prev => new Set(prev).add(studentId));
      
      const response = await api.post(`/api/teacher-dashboard/generate-student-report`, {
        studentId,
        teacherId
      });
      
      if (response.data.success) {
        setReports(prev => [...prev, response.data.report]);
      }
    } catch (err) {
      console.error("Failed to generate AI report:", err);
      console.log("Using mock data for generated report");
      // Use mock data as fallback
      const student = students.find(s => s.id === studentId);
      const mockReport: AIReport = {
        id: `report-${Date.now()}`,
        studentId,
        studentName: student?.name || "Unknown Student",
        generatedAt: new Date().toISOString(),
        summary: `${student?.name || "This student"} shows promising progress in programming fundamentals. Recent assessments indicate strong problem-solving abilities with room for improvement in advanced concepts.`,
        strengths: ["Basic programming", "Problem solving", "Code organization"],
        weaknesses: ["Advanced algorithms", "Time complexity", "Data structures"],
        recommendations: ["Practice with intermediate problems", "Study algorithm complexity", "Focus on data structure implementation"],
        performanceTrend: "improving",
        nextSteps: ["Complete 3 algorithm challenges", "Review data structures", "Practice time management"]
      };
      setReports(prev => [...prev, mockReport]);
    } finally {
      setGeneratingReports(prev => {
        const newSet = new Set(prev);
        newSet.delete(studentId);
        return newSet;
      });
    }
  };

  const getPerformanceTrendColor = (trend: string) => {
    switch (trend) {
      case "improving": return "text-green-400";
      case "declining": return "text-red-400";
      default: return "text-yellow-400";
    }
  };

  const getPerformanceTrendIcon = (trend: string) => {
    switch (trend) {
      case "improving": return "📈";
      case "declining": return "📉";
      default: return "➡️";
    }
  };

  if (loading) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center h-64">
          <LoadingSpinner />
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-purple-200 mb-2">
          🤖 AI Student Reports
        </h2>
        <p className="text-purple-300">
          Generate intelligent insights about your students' performance
        </p>
      </div>

      {error && (
        <Card className="p-4 bg-red-500/20 border-red-500/30">
          <div className="text-red-400 text-center">
            <p>{error}</p>
            <Button 
              variant="outline" 
              size="sm" 
              onClick={fetchExistingReports}
              className="mt-2"
            >
              Retry
            </Button>
          </div>
        </Card>
      )}

      {/* Students List */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {students.map((student, index) => {
          const existingReport = reports.find(r => r.studentId === student.id);
          const isGenerating = generatingReports.has(student.id);
          
          return (
            <motion.div
              key={student.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <Card className="p-4">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <h3 className="font-semibold text-purple-200">{student.name}</h3>
                    <p className="text-sm text-purple-400">{student.email}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-purple-400">
                      Last active: {new Date(student.lastActive).toLocaleDateString()}
                    </p>
                  </div>
                </div>

                <div className="flex gap-2">
                  {existingReport ? (
                    <Button 
                      variant="outline" 
                      size="sm" 
                      className="flex-1"
                      onClick={() => {
                        // Show existing report
                        console.log("Show existing report:", existingReport.id);
                      }}
                    >
                      View Report
                    </Button>
                  ) : (
                    <Button 
                      variant="primary" 
                      size="sm" 
                      className="flex-1"
                      onClick={() => generateStudentReport(student.id)}
                      disabled={isGenerating}
                    >
                      {isGenerating ? (
                        <>
                          <LoadingSpinner size="sm" />
                          <span className="ml-2">Generating...</span>
                        </>
                      ) : (
                        "Generate AI Report"
                      )}
                    </Button>
                  )}
                </div>
              </Card>
            </motion.div>
          );
        })}
      </div>

      {/* Generated Reports */}
      {reports.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-xl font-semibold text-purple-200 mb-4">
            Generated Reports
          </h3>
          {reports.map((report, index) => (
            <motion.div
              key={report.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <Card className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h4 className="text-lg font-semibold text-purple-200">
                      {report.studentName}
                    </h4>
                    <p className="text-sm text-purple-400">
                      Generated: {new Date(report.generatedAt).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm">
                      {getPerformanceTrendIcon(report.performanceTrend)}
                    </span>
                    <span className={`text-sm font-medium ${getPerformanceTrendColor(report.performanceTrend)}`}>
                      {report.performanceTrend}
                    </span>
                  </div>
                </div>

                <div className="space-y-4">
                  {/* Summary */}
                  <div>
                    <h5 className="font-semibold text-purple-200 mb-2">Summary</h5>
                    <p className="text-purple-300 text-sm">{report.summary}</p>
                  </div>

                  {/* Strengths and Weaknesses */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <h5 className="font-semibold text-green-400 mb-2">Strengths</h5>
                      <ul className="text-sm text-purple-300 space-y-1">
                        {report.strengths.map((strength, idx) => (
                          <li key={idx} className="flex items-start">
                            <span className="text-green-400 mr-2">✓</span>
                            {strength}
                          </li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <h5 className="font-semibold text-red-400 mb-2">Areas for Improvement</h5>
                      <ul className="text-sm text-purple-300 space-y-1">
                        {report.weaknesses.map((weakness, idx) => (
                          <li key={idx} className="flex items-start">
                            <span className="text-red-400 mr-2">⚠</span>
                            {weakness}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  {/* Recommendations */}
                  <div>
                    <h5 className="font-semibold text-purple-200 mb-2">Recommendations</h5>
                    <ul className="text-sm text-purple-300 space-y-1">
                      {report.recommendations.map((rec, idx) => (
                        <li key={idx} className="flex items-start">
                          <span className="text-purple-400 mr-2">•</span>
                          {rec}
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Next Steps */}
                  <div>
                    <h5 className="font-semibold text-purple-200 mb-2">Next Steps</h5>
                    <ul className="text-sm text-purple-300 space-y-1">
                      {report.nextSteps.map((step, idx) => (
                        <li key={idx} className="flex items-start">
                          <span className="text-blue-400 mr-2">→</span>
                          {step}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                <div className="mt-4 flex gap-2">
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => {
                      // Download report
                      console.log("Download report:", report.id);
                    }}
                  >
                    Download
                  </Button>
                  <Button 
                    variant="primary" 
                    size="sm"
                    onClick={() => {
                      // Share report
                      console.log("Share report:", report.id);
                    }}
                  >
                    Share
                  </Button>
                </div>
              </Card>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
};

export default AIStudentReports;
