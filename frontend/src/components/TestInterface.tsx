import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Clock, CheckCircle, AlertCircle, ArrowLeft, ArrowRight } from 'lucide-react';
import api from '../utils/api';
import { useToast } from '../contexts/ToastContext';

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
  onComplete: (result: any) => void;
}

const TestInterface: React.FC<TestInterfaceProps> = ({ assessmentId, onComplete }) => {
  const { error: showError, success } = useToast();
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
      const response = await api.get(`/api/assessments/${assessmentId}`);
      const data = response.data;
      
      setAssessment(data);
      setTimeLeft(data.time_limit * 60); // Convert minutes to seconds
      setAnswers(new Array(data.questions.length).fill(-1));
    } catch (error) {
      console.error('Failed to fetch assessment:', error);
      showError('Error', 'Failed to load assessment. Please try again.');
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
      
      const response = await api.post(`/api/assessments/${assessmentId}/submit`, {
        answers: answers,
        time_taken: assessment!.time_limit * 60 - timeLeft
      });
      
      success('Success', 'Assessment submitted successfully!');
      onComplete(response.data);
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
    <div className="min-h-screen pt-20 px-4 bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-purple-900/50 backdrop-blur-sm rounded-lg p-6 mb-6 border border-purple-500/30"
        >
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-2xl font-bold text-purple-200">{assessment.title}</h1>
              <p className="text-purple-300">Topic: {assessment.topic} • Difficulty: {assessment.difficulty}</p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 text-orange-400">
                <Clock className="w-5 h-5" />
                <span className="font-mono text-lg">{formatTime(timeLeft)}</span>
              </div>
              <div className="text-purple-300">
                Question {currentQuestionIndex + 1} of {assessment.questions.length}
              </div>
            </div>
          </div>
          
          {/* Progress Bar */}
          <div className="w-full bg-purple-800/30 rounded-full h-2">
            <motion.div
              className="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.3 }}
            />
          </div>
        </motion.div>

        {/* Question */}
        <motion.div
          key={currentQuestionIndex}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          className="bg-purple-900/50 backdrop-blur-sm rounded-lg p-6 mb-6 border border-purple-500/30"
        >
          <div className="mb-6">
            <h2 className="text-xl font-semibold text-purple-200 mb-4">
              {currentQuestion.question}
            </h2>
            
            <div className="space-y-3">
              {currentQuestion.options.map((option, index) => (
                <label
                  key={index}
                  className={`flex items-center p-4 rounded-lg border cursor-pointer transition-all hover:bg-purple-800/30 ${
                    answers[currentQuestionIndex] === index
                      ? 'border-purple-400 bg-purple-800/50'
                      : 'border-purple-500/30'
                  }`}
                >
                  <input
                    type="radio"
                    name={`question-${currentQuestionIndex}`}
                    checked={answers[currentQuestionIndex] === index}
                    onChange={() => handleAnswerChange(currentQuestionIndex, index)}
                    className="mr-4 w-4 h-4 text-purple-500"
                  />
                  <span className="text-purple-200">{option}</span>
                </label>
              ))}
            </div>
          </div>
        </motion.div>

        {/* Navigation */}
        <div className="flex items-center justify-between">
          <button
            onClick={handlePrevious}
            disabled={currentQuestionIndex === 0}
            className="flex items-center space-x-2 px-4 py-2 bg-purple-800 hover:bg-purple-700 disabled:bg-purple-800/50 disabled:cursor-not-allowed text-purple-200 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Previous</span>
          </button>

          <div className="flex space-x-2">
            {assessment.questions.map((_, index) => (
              <button
                key={index}
                onClick={() => setCurrentQuestionIndex(index)}
                className={`w-8 h-8 rounded-full text-sm font-medium transition-colors ${
                  index === currentQuestionIndex
                    ? 'bg-purple-500 text-white'
                    : answers[index] !== -1
                    ? 'bg-green-500 text-white'
                    : 'bg-purple-800 text-purple-300 hover:bg-purple-700'
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
              className="flex items-center space-x-2 px-6 py-2 bg-green-600 hover:bg-green-700 disabled:bg-green-600/50 text-white rounded-lg transition-colors"
            >
              <CheckCircle className="w-4 h-4" />
              <span>{submitting ? 'Submitting...' : 'Submit Test'}</span>
            </button>
          ) : (
            <button
              onClick={handleNext}
              className="flex items-center space-x-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-purple-200 rounded-lg transition-colors"
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
