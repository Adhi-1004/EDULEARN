import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Clock, CheckCircle, AlertCircle, ArrowLeft, ArrowRight } from 'lucide-react';
import api from '../utils/api';
import { useToast } from '../contexts/ToastContext';
import { useAuth } from '../hooks/useAuth';

interface Question {
  id: string;
  question: string;
  options: string[];
  correct_answer: number;
  explanation?: string;
  points: number;
}

interface Assessment {
  id: string;
  title: string;
  topic: string;
  difficulty: string;
  time_limit: number;
  questions: Question[];
}

interface TestInterfaceProps {
  assessmentId: string;
  onComplete?: (result: any) => void;
}

const TestInterface: React.FC<TestInterfaceProps> = ({ assessmentId, onComplete }) => {
  const { error: showError, success } = useToast();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [assessment, setAssessment] = useState<Assessment | null>(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState<number[]>([]);
  const [timeLeft, setTimeLeft] = useState(0);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchAssessment();
  }, [assessmentId]);

  useEffect(() => {
    if (timeLeft > 0) {
      const timer = setTimeout(() => setTimeLeft(timeLeft - 1), 1000);
      return () => clearTimeout(timer);
    } else if (timeLeft === 0 && assessment) {
      handleSubmit();
    }
  }, [timeLeft, assessment]);

  const fetchAssessment = async () => {
    try {
      setLoading(true);
      console.log("📊 [TEST] Fetching assessment:", assessmentId);
      
      // Try teacher endpoint first, then student endpoint
      let response;
      try {
        response = await api.get(`/api/assessments/teacher/${assessmentId}`);
        console.log("✅ [TEST] Fetched from teacher endpoint");
      } catch (teacherError) {
        console.log("⚠️ [TEST] Teacher endpoint failed, trying student endpoint");
        response = await api.get(`/api/assessments/${assessmentId}/details`);
        console.log("✅ [TEST] Fetched from student endpoint");
      }
      
      const data = response.data;
      console.log("📊 [TEST] Assessment data:", data);
      console.log("📊 [TEST] Questions count:", data.questions?.length);
      
      setAssessment(data);
      setTimeLeft(data.time_limit * 60); // Convert minutes to seconds
      setAnswers(new Array(data.questions.length).fill(-1));
    } catch (error: any) {
      console.error('❌ [TEST] Failed to fetch assessment:', error);
      console.error('❌ [TEST] Error details:', error.response?.data);
      showError('Error', error.response?.data?.detail || 'Failed to load assessment. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerChange = (questionIndex: number, answerIndex: number) => {
    const newAnswers = [...answers];
    newAnswers[questionIndex] = answerIndex;
    setAnswers(newAnswers);
  };

  const handleNext = () => {
    if (currentQuestionIndex < assessment!.questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    }
  };

  const handlePrevious = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1);
    }
  };

  const handleSubmit = async () => {
    try {
      setSubmitting(true);
      
      // Calculate score locally first
      let score = 0;
      assessment!.questions.forEach((question, index) => {
        if (answers[index] === question.correct_answer) {
          score++;
        }
      });
      
      const percentage = Math.round((score / assessment!.questions.length) * 100);
      const timeTaken = assessment!.time_limit * 60 - timeLeft;
      
      // Submit to backend
      const response = await api.post(`/api/assessments/${assessmentId}/submit`, {
        assessment_id: assessmentId,
        student_id: user?.id || '',
        answers: answers,
        time_taken: timeTaken,
        score: score,
        percentage: percentage,
        submitted_at: new Date().toISOString(),
        is_completed: true
      });
      
      success('Success', 'Assessment submitted successfully!');
      
      // Prepare result state for Results page
      const resultState = {
        score: score,
        totalQuestions: assessment!.questions.length,
        topic: assessment!.topic,
        difficulty: assessment!.difficulty,
        questions: assessment!.questions.map((q, idx) => ({
          id: q.id,
          question: q.question,
          options: q.options,
          answer: q.options[q.correct_answer], // Convert index to actual answer text
          explanation: q.explanation,
          difficulty: assessment!.difficulty,
          topic: assessment!.topic
        })),
        userAnswers: answers.map((answerIndex, questionIndex) => {
          const question = assessment!.questions[questionIndex];
          return answerIndex >= 0 && question?.options[answerIndex] 
            ? question.options[answerIndex] 
            : '';
        }),
        timeTaken: timeTaken,
        explanations: assessment!.questions.map((q, idx) => ({
          questionIndex: idx,
          explanation: q.explanation || "",
        }))
      };
      
      // Navigate to Results page with state
      navigate('/results', { state: resultState });
      
      // Call onComplete if provided (for backward compatibility)
      if (onComplete) {
        onComplete(response.data);
      }
    } catch (error) {
      console.error('Failed to submit assessment:', error);
      showError('Error', 'Failed to submit assessment. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  if (loading) {
    return (
      <div className="min-h-screen pt-20 px-4 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto mb-4"></div>
          <p className="text-purple-300">Loading assessment...</p>
        </div>
      </div>
    );
  }

  if (!assessment) {
    return (
      <div className="min-h-screen pt-20 px-4 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-16 h-16 text-red-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-red-400 mb-2">Assessment Not Found</h2>
          <p className="text-red-300">The assessment you're looking for doesn't exist or has been removed.</p>
        </div>
      </div>
    );
  }

  const currentQuestion = assessment.questions[currentQuestionIndex];
  const progress = ((currentQuestionIndex + 1) / assessment.questions.length) * 100;

  return (
    <div className="min-h-screen pt-20 px-4" style={{ backgroundColor: 'rgb(26, 32, 44)' }}>
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6"
        >
          <div className="flex items-center justify-between mb-3">
            <h1 className="text-2xl font-bold text-white">{assessment.title}</h1>
            <div className="text-right">
              <div className="text-orange-500 font-bold text-xl">{formatTime(timeLeft)}</div>
              <div className="text-gray-400 text-sm">Time Remaining</div>
            </div>
          </div>
          
          {/* Progress Bar */}
          <div className="w-full bg-gray-800 rounded-full h-2 mb-3">
            <motion.div
              className="bg-blue-600 h-2 rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.3 }}
            />
          </div>
          
          <div className="flex items-center justify-between text-gray-400">
            <div>Question {currentQuestionIndex + 1} of {assessment.questions.length}</div>
            <div>{Math.round(progress)}% Complete</div>
          </div>
        </motion.div>

        {/* Question */}
        <motion.div
          key={currentQuestionIndex}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          style={{ backgroundColor: 'rgb(31, 41, 55)' }}
          className="rounded-lg p-8 mb-6 border border-gray-700"
        >
          <div className="mb-8">
            <h2 className="text-xl font-bold text-white mb-6">
              {currentQuestion.question}
            </h2>
            
            <div className="space-y-3">
              {(currentQuestion.options || []).map((option, index) => (
                <label
                  key={index}
                  className={`flex items-center p-4 rounded-lg bg-gray-800 border cursor-pointer transition-all hover:bg-gray-700 ${
                    answers[currentQuestionIndex] === index
                      ? 'border-blue-500 bg-gray-700'
                      : 'border-gray-700'
                  }`}
                >
                  <input
                    type="radio"
                    name={`question-${currentQuestionIndex}`}
                    checked={answers[currentQuestionIndex] === index}
                    onChange={() => handleAnswerChange(currentQuestionIndex, index)}
                    className="mr-4 w-5 h-5 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-gray-200">{String.fromCharCode(65 + index)}. {option}</span>
                </label>
              ))}
            </div>
          </div>
        </motion.div>

        {/* Navigation */}
        <div className="flex items-center justify-between mt-6">
          <button
            onClick={handlePrevious}
            disabled={currentQuestionIndex === 0}
            className="flex items-center space-x-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 disabled:bg-gray-800/50 disabled:cursor-not-allowed disabled:text-gray-500 text-gray-300 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Previous</span>
          </button>

          <div className="flex space-x-2">
            {assessment.questions.map((_, index) => (
              <button
                key={index}
                onClick={() => setCurrentQuestionIndex(index)}
                className={`w-10 h-10 rounded-full text-sm font-medium transition-colors ${
                  index === currentQuestionIndex
                    ? 'bg-blue-600 text-white'
                    : answers[index] !== -1
                    ? 'bg-green-600 text-white'
                    : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                }`}
              >
                {index + 1}
              </button>
            ))}
          </div>

          {currentQuestionIndex === assessment.questions.length - 1 ? (
            <button
              onClick={handleSubmit}
              disabled={submitting}
              className="flex items-center space-x-2 px-6 py-3 bg-green-600 hover:bg-green-700 disabled:bg-green-600/50 text-white rounded-lg transition-colors font-medium"
            >
              <CheckCircle className="w-4 h-4" />
              <span>{submitting ? 'Submitting...' : 'Submit Test'}</span>
            </button>
          ) : (
            <button
              onClick={handleNext}
              className="flex items-center space-x-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium"
            >
              <span>Next</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Time Warning */}
        {timeLeft < 300 && timeLeft > 0 && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="mt-4 p-4 bg-orange-900/50 border border-orange-500/30 rounded-lg"
          >
            <div className="flex items-center space-x-2 text-orange-400">
              <AlertCircle className="w-5 h-5" />
              <span className="font-medium">
                Warning: Only {formatTime(timeLeft)} remaining!
              </span>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default TestInterface;
