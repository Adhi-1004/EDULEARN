import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import Card from "../ui/Card";
import Button from "../ui/Button";
import LoadingSpinner from "../ui/LoadingSpinner";
import api from "../../utils/api";

interface Question {
  id: string;
  question: string;
  topic: string;
  difficulty: string;
  successRate: number;
  attempts: number;
  flagged: boolean;
  flagReason?: string;
  lastAudited?: string;
  aiAuditScore?: number;
}

interface ContentQualityMetrics {
  totalQuestions: number;
  flaggedQuestions: number;
  highFailureRate: number;
  highSuccessRate: number;
  needsAudit: number;
  averageQualityScore: number;
}

interface AIAuditResult {
  questionId: string;
  clarityScore: number;
  correctnessScore: number;
  difficultyScore: number;
  ambiguityIssues: string[];
  suggestions: string[];
  overallScore: number;
  auditDate: string;
}

interface ContentQualityOversightProps {
  adminId: string;
}

const ContentQualityOversight: React.FC<ContentQualityOversightProps> = ({ adminId }) => {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [metrics, setMetrics] = useState<ContentQualityMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [auditing, setAuditing] = useState<Set<string>>(new Set());
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'flagged' | 'high-failure' | 'high-success' | 'needs-audit'>('all');

  useEffect(() => {
    fetchContentQuality();
  }, [adminId]);

  const fetchContentQuality = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/api/admin-dashboard/content-quality/${adminId}`);
      setQuestions(response.data.questions);
      setMetrics(response.data.metrics);
    } catch (err) {
      console.error("Failed to fetch content quality data:", err);
      setError("Failed to load content quality data");
    } finally {
      setLoading(false);
    }
  };

  const performAIAudit = async (questionId: string) => {
    try {
      setAuditing(prev => new Set(prev).add(questionId));
      
      const response = await api.post(`/api/admin-dashboard/audit-content`, {
        questionId,
        adminId
      });
      
      if (response.data.success) {
        // Update the question with audit results
        setQuestions(prev => prev.map(q => 
          q.id === questionId 
            ? { 
                ...q, 
                aiAuditScore: response.data.auditResult.overallScore,
                lastAudited: response.data.auditResult.auditDate,
                flagged: response.data.auditResult.overallScore < 70
              }
            : q
        ));
      }
    } catch (err) {
      console.error("Failed to perform AI audit:", err);
      setError("Failed to perform AI audit");
    } finally {
      setAuditing(prev => {
        const newSet = new Set(prev);
        newSet.delete(questionId);
        return newSet;
      });
    }
  };

  const getQualityColor = (score: number) => {
    if (score >= 80) return "text-green-400";
    if (score >= 60) return "text-yellow-400";
    return "text-red-400";
  };

  const getQualityBgColor = (score: number) => {
    if (score >= 80) return "bg-green-500/20 border-green-500/30";
    if (score >= 60) return "bg-yellow-500/20 border-yellow-500/30";
    return "bg-red-500/20 border-red-500/30";
  };

  const getSuccessRateColor = (rate: number) => {
    if (rate >= 80) return "text-green-400";
    if (rate >= 60) return "text-yellow-400";
    if (rate <= 20) return "text-red-400";
    return "text-purple-400";
  };

  const filteredQuestions = questions.filter(question => {
    switch (filter) {
      case 'flagged':
        return question.flagged;
      case 'high-failure':
        return question.successRate <= 20;
      case 'high-success':
        return question.successRate >= 90;
      case 'needs-audit':
        return !question.lastAudited;
      default:
        return true;
    }
  });

  if (loading && !metrics) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center h-64">
          <LoadingSpinner />
        </div>
      </Card>
    );
  }

  if (error && !metrics) {
    return (
      <Card className="p-6">
        <div className="text-center text-red-400">
          <p>{error}</p>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={fetchContentQuality}
            className="mt-4"
          >
            Retry
          </Button>
        </div>
      </Card>
    );
  }

  if (!metrics) return null;

  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-purple-200 mb-2">
          🔍 Content Quality Oversight
        </h2>
        <p className="text-purple-300">
          Monitor and audit content quality with AI-powered insights
        </p>
      </div>

      {/* Quality Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-purple-200">Total Questions</h3>
            <span className="text-2xl">📝</span>
          </div>
          <div className="text-3xl font-bold text-purple-200 mb-2">
            {metrics.totalQuestions.toLocaleString()}
          </div>
          <p className="text-sm text-purple-400">Questions in database</p>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-purple-200">Flagged Content</h3>
            <span className="text-2xl">🚩</span>
          </div>
          <div className="text-3xl font-bold text-red-400 mb-2">
            {metrics.flaggedQuestions}
          </div>
          <p className="text-sm text-purple-400">Need attention</p>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-purple-200">High Failure Rate</h3>
            <span className="text-2xl">⚠️</span>
          </div>
          <div className="text-3xl font-bold text-red-400 mb-2">
            {metrics.highFailureRate}
          </div>
          <p className="text-sm text-purple-400">Success rate ≤ 20%</p>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-purple-200">Quality Score</h3>
            <span className="text-2xl">⭐</span>
          </div>
          <div className={`text-3xl font-bold ${getQualityColor(metrics.averageQualityScore)} mb-2`}>
            {metrics.averageQualityScore.toFixed(1)}
          </div>
          <p className="text-sm text-purple-400">Average AI audit score</p>
        </Card>
      </div>

      {/* Filter Controls */}
      <Card className="p-6">
        <div className="flex flex-wrap gap-2 mb-4">
          <Button
            variant={filter === 'all' ? 'primary' : 'outline'}
            size="sm"
            onClick={() => setFilter('all')}
          >
            All Questions
          </Button>
          <Button
            variant={filter === 'flagged' ? 'primary' : 'outline'}
            size="sm"
            onClick={() => setFilter('flagged')}
          >
            Flagged ({metrics.flaggedQuestions})
          </Button>
          <Button
            variant={filter === 'high-failure' ? 'primary' : 'outline'}
            size="sm"
            onClick={() => setFilter('high-failure')}
          >
            High Failure ({metrics.highFailureRate})
          </Button>
          <Button
            variant={filter === 'high-success' ? 'primary' : 'outline'}
            size="sm"
            onClick={() => setFilter('high-success')}
          >
            High Success ({metrics.highSuccessRate})
          </Button>
          <Button
            variant={filter === 'needs-audit' ? 'primary' : 'outline'}
            size="sm"
            onClick={() => setFilter('needs-audit')}
          >
            Needs Audit ({metrics.needsAudit})
          </Button>
        </div>
      </Card>

      {/* Questions List */}
      <div className="space-y-4">
        {filteredQuestions.map((question, index) => (
          <motion.div
            key={question.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <Card className={`p-6 ${question.flagged ? 'border-red-500/30 bg-red-500/5' : ''}`}>
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="font-semibold text-purple-200 line-clamp-2">
                      {question.question}
                    </h3>
                    {question.flagged && (
                      <span className="px-2 py-1 bg-red-500/20 text-red-400 text-xs rounded-full">
                        Flagged
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-4 text-sm text-purple-400">
                    <span>Topic: {question.topic}</span>
                    <span>Difficulty: {question.difficulty}</span>
                    <span>Attempts: {question.attempts}</span>
                    {question.lastAudited && (
                      <span>Last audited: {new Date(question.lastAudited).toLocaleDateString()}</span>
                    )}
                  </div>
                </div>
                <div className="text-right">
                  <div className={`text-lg font-bold ${getSuccessRateColor(question.successRate)}`}>
                    {question.successRate.toFixed(1)}%
                  </div>
                  <div className="text-sm text-purple-400">Success Rate</div>
                  {question.aiAuditScore && (
                    <div className={`text-sm font-semibold ${getQualityColor(question.aiAuditScore)}`}>
                      AI Score: {question.aiAuditScore.toFixed(1)}
                    </div>
                  )}
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-sm text-purple-300">Quality Status:</span>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    question.successRate >= 80 ? 'bg-green-500/20 text-green-400' :
                    question.successRate >= 60 ? 'bg-yellow-500/20 text-yellow-400' :
                    question.successRate <= 20 ? 'bg-red-500/20 text-red-400' :
                    'bg-purple-500/20 text-purple-400'
                  }`}>
                    {question.successRate >= 80 ? 'Excellent' :
                     question.successRate >= 60 ? 'Good' :
                     question.successRate <= 20 ? 'Poor' : 'Average'}
                  </span>
                </div>
                
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => performAIAudit(question.id)}
                    disabled={auditing.has(question.id)}
                  >
                    {auditing.has(question.id) ? (
                      <>
                        <LoadingSpinner size="sm" />
                        <span className="ml-2">Auditing...</span>
                      </>
                    ) : (
                      "AI Audit"
                    )}
                  </Button>
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={() => {
                      // View question details
                      console.log("View question details:", question.id);
                    }}
                  >
                    View Details
                  </Button>
                </div>
              </div>
            </Card>
          </motion.div>
        ))}
      </div>

      {filteredQuestions.length === 0 && (
        <Card className="p-8 text-center">
          <div className="text-purple-300">
            <p className="text-lg mb-4">No questions found</p>
            <p>Try adjusting your filter criteria</p>
          </div>
        </Card>
      )}
    </div>
  );
};

export default ContentQualityOversight;
