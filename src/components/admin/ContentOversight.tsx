import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import Card from '../ui/Card';
import Button from '../ui/Button';
import Input from '../ui/Input';
import LoadingSpinner from '../ui/LoadingSpinner';
import api from '../../utils/api';

interface Assessment {
  id: string;
  title: string;
  topic: string;
  difficulty: string;
  type: string;
  created_by: string;
  created_at: string;
  completion_count: number;
  is_published: boolean;
}

interface CodingProblem {
  id: string;
  title: string;
  topic: string;
  difficulty: string;
  created_by: string;
  created_at: string;
  submission_count: number;
  success_rate: number;
  average_time: number | null;
}

const ContentOversight: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'assessments' | 'coding'>('assessments');
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [codingProblems, setCodingProblems] = useState<CodingProblem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    if (activeTab === 'assessments') {
      fetchAssessments();
    } else {
      fetchCodingProblems();
    }
  }, [activeTab, page, searchTerm]);

  const fetchAssessments = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        page: page.toString(),
        limit: '20'
      });

      if (searchTerm) params.append('search', searchTerm);

      const response = await api.get(`/api/admin/content/assessments?${params}`);
      
      if (response.data.success) {
        setAssessments(response.data.assessments);
        setTotalPages(response.data.pagination.pages);
      }
    } catch (error: any) {
      console.error('Error fetching assessments:', error);
      setError(error.response?.data?.detail || 'Failed to fetch assessments');
    } finally {
      setLoading(false);
    }
  };

  const fetchCodingProblems = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        page: page.toString(),
        limit: '20'
      });

      if (searchTerm) params.append('search', searchTerm);

      const response = await api.get(`/api/admin/content/coding-problems?${params}`);
      
      if (response.data.success) {
        setCodingProblems(response.data.problems);
        setTotalPages(response.data.pagination.pages);
      }
    } catch (error: any) {
      console.error('Error fetching coding problems:', error);
      setError(error.response?.data?.detail || 'Failed to fetch coding problems');
    } finally {
      setLoading(false);
    }
  };

  const deleteAssessment = async (assessmentId: string) => {
    if (!confirm('Are you sure you want to delete this assessment?')) {
      return;
    }

    try {
      const response = await api.delete(`/api/assessments/${assessmentId}`);
      if (response.data.success) {
        fetchAssessments();
      }
    } catch (error: any) {
      console.error('Error deleting assessment:', error);
      setError('Failed to delete assessment');
    }
  };

  const deleteCodingProblem = async (problemId: string) => {
    if (!confirm('Are you sure you want to delete this coding problem?')) {
      return;
    }

    try {
      const response = await api.delete(`/api/coding/problems/${problemId}`);
      if (response.data.success) {
        fetchCodingProblems();
      }
    } catch (error: any) {
      console.error('Error deleting coding problem:', error);
      setError('Failed to delete coding problem');
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty.toLowerCase()) {
      case 'easy':
        return 'text-green-400 bg-green-900/20';
      case 'medium':
        return 'text-yellow-400 bg-yellow-900/20';
      case 'hard':
        return 'text-red-400 bg-red-900/20';
      default:
        return 'text-gray-400 bg-gray-900/20';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'mcq':
        return '📝';
      case 'coding':
        return '💻';
      default:
        return '📊';
    }
  };

  if (loading && assessments.length === 0 && codingProblems.length === 0) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header and Tabs */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <h2 className="text-2xl font-bold text-purple-200">Content & Course Oversight</h2>
        <div className="flex space-x-2">
          <button
            onClick={() => setActiveTab('assessments')}
            className={`px-4 py-2 rounded-lg ${
              activeTab === 'assessments'
                ? 'bg-purple-600 text-white'
                : 'bg-purple-900/50 text-purple-300 hover:bg-purple-800/50'
            }`}
          >
            📝 Assessments
          </button>
          <button
            onClick={() => setActiveTab('coding')}
            className={`px-4 py-2 rounded-lg ${
              activeTab === 'coding'
                ? 'bg-purple-600 text-white'
                : 'bg-purple-900/50 text-purple-300 hover:bg-purple-800/50'
            }`}
          >
            💻 Coding Problems
          </button>
        </div>
      </div>

      {/* Search */}
      <div className="flex flex-col sm:flex-row gap-4">
        <Input
          type="text"
          placeholder={`Search ${activeTab}...`}
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full sm:w-64"
        />
      </div>

      {/* Content Tables */}
      {activeTab === 'assessments' && (
        <Card className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-purple-500/30">
                <th className="text-left p-4 text-purple-300">Assessment</th>
                <th className="text-left p-4 text-purple-300">Topic</th>
                <th className="text-left p-4 text-purple-300">Difficulty</th>
                <th className="text-left p-4 text-purple-300">Type</th>
                <th className="text-left p-4 text-purple-300">Created By</th>
                <th className="text-left p-4 text-purple-300">Completions</th>
                <th className="text-left p-4 text-purple-300">Status</th>
                <th className="text-left p-4 text-purple-300">Actions</th>
              </tr>
            </thead>
            <tbody>
              {assessments.map((assessment, index) => (
                <motion.tr
                  key={assessment.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="border-b border-purple-500/20 hover:bg-purple-900/20"
                >
                  <td className="p-4">
                    <div>
                      <p className="text-purple-200 font-medium">{assessment.title}</p>
                      <p className="text-purple-400 text-sm">{formatDate(assessment.created_at)}</p>
                    </div>
                  </td>
                  <td className="p-4 text-purple-300">{assessment.topic}</td>
                  <td className="p-4">
                    <span className={`px-2 py-1 rounded text-sm ${getDifficultyColor(assessment.difficulty)}`}>
                      {assessment.difficulty}
                    </span>
                  </td>
                  <td className="p-4">
                    <span className="flex items-center space-x-2">
                      <span>{getTypeIcon(assessment.type)}</span>
                      <span className="text-purple-300">{assessment.type.toUpperCase()}</span>
                    </span>
                  </td>
                  <td className="p-4 text-purple-300">{assessment.created_by}</td>
                  <td className="p-4 text-purple-300">{assessment.completion_count}</td>
                  <td className="p-4">
                    <span className={`px-2 py-1 rounded text-sm ${
                      assessment.is_published 
                        ? 'text-green-400 bg-green-900/20' 
                        : 'text-yellow-400 bg-yellow-900/20'
                    }`}>
                      {assessment.is_published ? 'Published' : 'Draft'}
                    </span>
                  </td>
                  <td className="p-4">
                    <div className="flex space-x-2">
                      <Button
                        onClick={() => deleteAssessment(assessment.id)}
                        className="bg-red-600 hover:bg-red-700 text-sm px-3 py-1"
                      >
                        Delete
                      </Button>
                    </div>
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>

          {assessments.length === 0 && !loading && (
            <div className="text-center py-8">
              <p className="text-purple-400">No assessments found</p>
            </div>
          )}
        </Card>
      )}

      {activeTab === 'coding' && (
        <Card className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-purple-500/30">
                <th className="text-left p-4 text-purple-300">Problem</th>
                <th className="text-left p-4 text-purple-300">Topic</th>
                <th className="text-left p-4 text-purple-300">Difficulty</th>
                <th className="text-left p-4 text-purple-300">Created By</th>
                <th className="text-left p-4 text-purple-300">Submissions</th>
                <th className="text-left p-4 text-purple-300">Success Rate</th>
                <th className="text-left p-4 text-purple-300">Avg Time</th>
                <th className="text-left p-4 text-purple-300">Actions</th>
              </tr>
            </thead>
            <tbody>
              {codingProblems.map((problem, index) => (
                <motion.tr
                  key={problem.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="border-b border-purple-500/20 hover:bg-purple-900/20"
                >
                  <td className="p-4">
                    <div>
                      <p className="text-purple-200 font-medium">{problem.title}</p>
                      <p className="text-purple-400 text-sm">{formatDate(problem.created_at)}</p>
                    </div>
                  </td>
                  <td className="p-4 text-purple-300">{problem.topic}</td>
                  <td className="p-4">
                    <span className={`px-2 py-1 rounded text-sm ${getDifficultyColor(problem.difficulty)}`}>
                      {problem.difficulty}
                    </span>
                  </td>
                  <td className="p-4 text-purple-300">{problem.created_by}</td>
                  <td className="p-4 text-purple-300">{problem.submission_count}</td>
                  <td className="p-4">
                    <div className="flex items-center space-x-2">
                      <div className="w-16 bg-purple-900/50 rounded-full h-2">
                        <div 
                          className="bg-purple-500 h-2 rounded-full" 
                          style={{ width: `${problem.success_rate * 100}%` }}
                        ></div>
                      </div>
                      <span className="text-purple-300 text-sm">
                        {(problem.success_rate * 100).toFixed(1)}%
                      </span>
                    </div>
                  </td>
                  <td className="p-4 text-purple-300">
                    {problem.average_time ? `${problem.average_time}s` : 'N/A'}
                  </td>
                  <td className="p-4">
                    <div className="flex space-x-2">
                      <Button
                        onClick={() => deleteCodingProblem(problem.id)}
                        className="bg-red-600 hover:bg-red-700 text-sm px-3 py-1"
                      >
                        Delete
                      </Button>
                    </div>
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>

          {codingProblems.length === 0 && !loading && (
            <div className="text-center py-8">
              <p className="text-purple-400">No coding problems found</p>
            </div>
          )}
        </Card>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex justify-center space-x-2">
          <Button
            onClick={() => setPage(page - 1)}
            disabled={page === 1}
            className="bg-purple-600 hover:bg-purple-700 disabled:opacity-50"
          >
            Previous
          </Button>
          <span className="flex items-center px-4 py-2 text-purple-200">
            Page {page} of {totalPages}
          </span>
          <Button
            onClick={() => setPage(page + 1)}
            disabled={page === totalPages}
            className="bg-purple-600 hover:bg-purple-700 disabled:opacity-50"
          >
            Next
          </Button>
        </div>
      )}

      {error && (
        <div className="text-center py-4">
          <p className="text-red-400">Error: {error}</p>
          <Button 
            onClick={() => activeTab === 'assessments' ? fetchAssessments() : fetchCodingProblems()} 
            className="mt-2"
          >
            Retry
          </Button>
        </div>
      )}
    </div>
  );
};

export default ContentOversight;
