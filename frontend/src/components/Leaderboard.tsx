import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Trophy, Medal, Award, TrendingUp, Users, Target, Clock } from 'lucide-react';
import api from '../utils/api';

interface LeaderboardEntry {
  student_id: string;
  student_name: string;
  score: number;
  percentage: number;
  time_taken?: number;
  rank: number;
}

interface LeaderboardProps {
  assessmentId: string;
  onClose: () => void;
}

const Leaderboard: React.FC<LeaderboardProps> = ({ assessmentId, onClose }) => {
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchLeaderboard();
  }, [assessmentId]);

  const fetchLeaderboard = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/api/assessments/${assessmentId}/leaderboard`);
      setLeaderboard(response.data || []);
    } catch (error) {
      console.error('Failed to fetch leaderboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRankIcon = (rank: number) => {
    switch (rank) {
      case 1:
        return <Trophy className="w-6 h-6 text-yellow-400" />;
      case 2:
        return <Medal className="w-6 h-6 text-gray-400" />;
      case 3:
        return <Award className="w-6 h-6 text-orange-400" />;
      default:
        return <span className="w-6 h-6 flex items-center justify-center text-purple-400 font-bold">
          {rank}
        </span>;
    }
  };

  const getRankColor = (rank: number) => {
    switch (rank) {
      case 1:
        return 'bg-gradient-to-r from-yellow-500/20 to-yellow-600/20 border-yellow-500/30';
      case 2:
        return 'bg-gradient-to-r from-gray-500/20 to-gray-600/20 border-gray-500/30';
      case 3:
        return 'bg-gradient-to-r from-orange-500/20 to-orange-600/20 border-orange-500/30';
      default:
        return 'bg-purple-800/30 border-purple-500/30';
    }
  };

  const formatTime = (seconds?: number) => {
    if (!seconds) return 'N/A';
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const getPercentageColor = (percentage: number) => {
    if (percentage >= 90) return 'text-green-400';
    if (percentage >= 80) return 'text-blue-400';
    if (percentage >= 70) return 'text-yellow-400';
    if (percentage >= 60) return 'text-orange-400';
    return 'text-red-400';
  };

  if (loading) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          className="bg-purple-900 rounded-lg p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto"
          onClick={(e) => e.stopPropagation()}
        >
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto mb-4"></div>
            <p className="text-purple-300">Loading leaderboard...</p>
          </div>
        </motion.div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        className="bg-purple-900 rounded-lg p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-purple-200">Assessment Leaderboard</h2>
          <button
            onClick={onClose}
            className="text-purple-400 hover:text-purple-200 transition-colors"
          >
            ✕
          </button>
        </div>

        {leaderboard.length === 0 ? (
          <div className="text-center py-8">
            <Trophy className="w-16 h-16 text-purple-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-purple-300 mb-2">No Submissions Yet</h3>
            <p className="text-purple-400">Students haven't completed this assessment yet.</p>
          </div>
        ) : (
          <>
            {/* Statistics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div className="bg-purple-800/30 rounded-lg p-4 border border-purple-500/30">
                <div className="flex items-center space-x-2 mb-2">
                  <Users className="w-5 h-5 text-blue-400" />
                  <span className="text-purple-300 font-medium">Total Participants</span>
                </div>
                <div className="text-2xl font-bold text-blue-400">
                  {leaderboard.length}
                </div>
              </div>

              <div className="bg-purple-800/30 rounded-lg p-4 border border-purple-500/30">
                <div className="flex items-center space-x-2 mb-2">
                  <Target className="w-5 h-5 text-green-400" />
                  <span className="text-purple-300 font-medium">Average Score</span>
                </div>
                <div className="text-2xl font-bold text-green-400">
                  {(leaderboard.reduce((sum, entry) => sum + entry.percentage, 0) / leaderboard.length).toFixed(1)}%
                </div>
              </div>

              <div className="bg-purple-800/30 rounded-lg p-4 border border-purple-500/30">
                <div className="flex items-center space-x-2 mb-2">
                  <TrendingUp className="w-5 h-5 text-purple-400" />
                  <span className="text-purple-300 font-medium">Top Performer</span>
                </div>
                <div className="text-lg font-bold text-purple-400">
                  {leaderboard[0]?.student_name || 'N/A'}
                </div>
              </div>
            </div>

            {/* Leaderboard */}
            <div className="space-y-3">
              <h3 className="text-lg font-semibold text-purple-200 mb-4">Rankings</h3>
              
              {leaderboard.map((entry, index) => (
                <motion.div
                  key={entry.student_id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className={`p-4 rounded-lg border ${getRankColor(entry.rank)}`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className="flex items-center space-x-2">
                        {getRankIcon(entry.rank)}
                        <span className="text-lg font-bold text-purple-200">
                          #{entry.rank}
                        </span>
                      </div>
                      
                      <div>
                        <h4 className="text-purple-200 font-semibold">
                          {entry.student_name}
                        </h4>
                        <div className="flex items-center space-x-4 text-sm text-purple-400">
                          <span>Score: {entry.score}</span>
                          <span className={`font-medium ${getPercentageColor(entry.percentage)}`}>
                            {entry.percentage.toFixed(1)}%
                          </span>
                          {entry.time_taken && (
                            <span className="flex items-center space-x-1">
                              <Clock className="w-3 h-3" />
                              <span>{formatTime(entry.time_taken)}</span>
                            </span>
                          )}
                        </div>
                      </div>
                    </div>

                    <div className="text-right">
                      <div className={`text-2xl font-bold ${getPercentageColor(entry.percentage)}`}>
                        {entry.percentage.toFixed(1)}%
                      </div>
                      <div className="text-sm text-purple-400">
                        {entry.percentage >= 90 ? 'Excellent' : 
                         entry.percentage >= 80 ? 'Good' : 
                         entry.percentage >= 70 ? 'Average' : 'Needs Improvement'}
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </>
        )}
      </motion.div>
    </motion.div>
  );
};

export default Leaderboard;
