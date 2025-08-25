import React from 'react';
import { motion } from 'framer-motion';
import { Trophy, Medal, Award, Clock, Target } from 'lucide-react';
import { LeaderboardEntry } from '../types';
import { Card } from './ui/Card';

interface LeaderboardProps {
  entries: LeaderboardEntry[];
  currentUserId?: string;
  title?: string;
}

export const Leaderboard: React.FC<LeaderboardProps> = ({
  entries,
  currentUserId,
  title = "Leaderboard"
}) => {
  const getRankIcon = (rank: number) => {
    switch (rank) {
      case 1:
        return <Trophy className="h-6 w-6 text-yellow-500" />;
      case 2:
        return <Medal className="h-6 w-6 text-gray-400" />;
      case 3:
        return <Award className="h-6 w-6 text-amber-600" />;
      default:
        return <span className="text-lg font-bold text-gray-600">#{rank}</span>;
    }
  };

  const getRankColor = (rank: number) => {
    switch (rank) {
      case 1:
        return 'from-yellow-400 to-yellow-600';
      case 2:
        return 'from-gray-300 to-gray-500';
      case 3:
        return 'from-amber-400 to-amber-600';
      default:
        return 'from-blue-400 to-blue-600';
    }
  };

  return (
    <Card className="p-6">
      <div className="flex items-center justify-center mb-6">
        <Trophy className="h-8 w-8 text-yellow-500 mr-3" />
        <h2 className="text-2xl font-bold text-gray-900">{title}</h2>
      </div>

      <div className="space-y-3">
        {entries.map((entry, index) => (
          <motion.div
            key={entry.studentId}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className={`relative overflow-hidden rounded-lg ${
              entry.studentId === currentUserId
                ? 'ring-2 ring-blue-500 bg-blue-50'
                : 'bg-white border border-gray-200'
            }`}
          >
            <div className="flex items-center p-4">
              {/* Rank */}
              <div className={`flex items-center justify-center w-12 h-12 rounded-full bg-gradient-to-r ${getRankColor(entry.rank)} text-white mr-4`}>
                {getRankIcon(entry.rank)}
              </div>

              {/* Avatar */}
              <div className="w-10 h-10 rounded-full overflow-hidden mr-4">
                <img
                  src={entry.avatar || `/placeholder.svg?height=40&width=40&text=${entry.studentName.charAt(0)}`}
                  alt={entry.studentName}
                  className="w-full h-full object-cover"
                />
              </div>

              {/* Student Info */}
              <div className="flex-1">
                <h3 className="font-semibold text-gray-900">{entry.studentName}</h3>
                <div className="flex items-center space-x-4 text-sm text-gray-600">
                  <div className="flex items-center">
                    <Target className="h-4 w-4 mr-1" />
                    <span>{entry.score} points</span>
                  </div>
                  <div className="flex items-center">
                    <Clock className="h-4 w-4 mr-1" />
                    <span>{Math.floor(entry.timeSpent / 60)}m {entry.timeSpent % 60}s</span>
                  </div>
                </div>
              </div>

              {/* Score Badge */}
              <div className="text-right">
                <div className="text-2xl font-bold text-gray-900">{entry.score}</div>
                <div className="text-sm text-gray-500">points</div>
              </div>
            </div>

            {/* Animated background for top 3 */}
            {entry.rank <= 3 && (
              <motion.div
                className={`absolute inset-0 bg-gradient-to-r ${getRankColor(entry.rank)} opacity-5`}
                animate={{
                  opacity: [0.05, 0.1, 0.05],
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
              />
            )}
          </motion.div>
        ))}
      </div>

      {entries.length === 0 && (
        <div className="text-center py-8">
          <Trophy className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500">No results yet. Be the first to complete the test!</p>
        </div>
      )}
    </Card>
  );
};
