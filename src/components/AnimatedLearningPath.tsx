import React from 'react';
import { motion } from 'framer-motion';

interface AnimatedLearningPathProps {
  className?: string;
}

// A lightweight, unique SVG-based animation representing a learning journey
// with animated gradient lines, pulsing topic nodes, and moving progress orbs.
export const AnimatedLearningPath: React.FC<AnimatedLearningPathProps> = ({ className }) => {
  const topics = [
    { x: 20, y: 70, color: '#3B82F6', label: 'Basics' },
    { x: 35, y: 45, color: '#10B981', label: 'Practice' },
    { x: 55, y: 65, color: '#F59E0B', label: 'Projects' },
    { x: 72, y: 40, color: '#8B5CF6', label: 'AI/ML' },
    { x: 88, y: 60, color: '#EF4444', label: 'Mastery' }
  ];

  return (
    <div className={className}>
      <svg viewBox="0 0 100 70" className="w-full h-full" preserveAspectRatio="xMidYMid meet">
        <defs>
          <linearGradient id="pathGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#60A5FA" />
            <stop offset="50%" stopColor="#A78BFA" />
            <stop offset="100%" stopColor="#F472B6" />
          </linearGradient>
          <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="0.8" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* Decorative soft blobs */}
        <g opacity={0.15}>
          <motion.circle cx="10" cy="15" r="8" fill="#60A5FA" animate={{ cy: [14, 16, 14] }} transition={{ duration: 6, repeat: Infinity, ease: 'easeInOut' }} />
          <motion.circle cx="90" cy="10" r="7" fill="#A78BFA" animate={{ cx: [89, 91, 89] }} transition={{ duration: 7, repeat: Infinity, ease: 'easeInOut' }} />
          <motion.circle cx="20" cy="65" r="9" fill="#F472B6" animate={{ r: [8, 10, 8] }} transition={{ duration: 8, repeat: Infinity, ease: 'easeInOut' }} />
        </g>

        {/* Learning path curve */}
        <motion.path
          d="M 8 58 C 22 25, 42 80, 60 38 S 94 48, 95 58"
          fill="none"
          stroke="url(#pathGradient)"
          strokeWidth={1.2}
          filter="url(#glow)"
          strokeLinecap="round"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 2.2, ease: 'easeInOut' }}
        />

        {/* Moving progress orb along the path (approximate animation) */}
        <motion.circle
          r="1.6"
          fill="#FFFFFF"
          stroke="#60A5FA"
          strokeWidth="0.6"
          filter="url(#glow)"
          animate={{ cx: [8, 22, 42, 60, 80, 95], cy: [58, 35, 65, 38, 50, 58] }}
          transition={{ duration: 8, repeat: Infinity, ease: 'easeInOut' }}
        />

        {/* Topic nodes */}
        {topics.map((t, i) => (
          <g key={t.label}>
            <motion.circle
              cx={t.x}
              cy={t.y}
              r={2.2}
              fill={t.color}
              filter="url(#glow)"
              animate={{ r: [2, 2.6, 2] }}
              transition={{ duration: 2 + i * 0.2, repeat: Infinity, ease: 'easeInOut' }}
            />
            <text x={t.x} y={t.y - 3.8} textAnchor="middle" fontSize="3" fill={t.color} style={{ fontWeight: 600 }}>{t.label}</text>
          </g>
        ))}
      </svg>
    </div>
  );
};

export default AnimatedLearningPath;


