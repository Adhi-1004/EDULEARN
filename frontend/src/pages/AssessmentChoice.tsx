import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { User } from '../types';
import { useTheme } from '../contexts/ThemeContext';
import AnimatedBackground from '../components/AnimatedBackground';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import { ANIMATION_VARIANTS } from '../utils/constants';

interface AssessmentChoiceProps {
  user: User;
}

const AssessmentChoice: React.FC<AssessmentChoiceProps> = ({ user }) => {
  const { mode } = useTheme();

  return (
    <>
      <AnimatedBackground />
      <div className="min-h-screen pt-20 px-4 relative z-10">
        <motion.div
          variants={ANIMATION_VARIANTS.fadeIn}
          initial="initial"
          animate="animate"
          className="max-w-4xl mx-auto"
        >
          {/* Header */}
          <motion.div
            variants={ANIMATION_VARIANTS.slideDown}
            className="text-center mb-12"
          >
            <h1 className="text-4xl font-bold text-purple-200 mb-4">
              Choose Your Assessment Type
            </h1>
            <p className="text-purple-300 text-lg">
              Select the type of assessment you'd like to take today
            </p>
          </motion.div>

          {/* Assessment Options */}
          <motion.div
            variants={ANIMATION_VARIANTS.stagger}
            className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8"
          >
            {/* MCQ Assessment */}
            <motion.div variants={ANIMATION_VARIANTS.slideLeft}>
              <Card className="p-8 h-full hover:border-purple-400/50 transition-all duration-300 group">
                <div className="text-center">
                  {/* Icon */}
                  <div className="w-20 h-20 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform duration-300">
                    <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>

                  {/* Title */}
                  <h3 className="text-2xl font-bold text-purple-200 mb-4">
                    📝 MCQ Assessment
                  </h3>

                  {/* Description */}
                  <p className="text-purple-300 mb-6 leading-relaxed">
                    Test your theoretical knowledge with our AI-powered adaptive multiple-choice questions. 
                    Get personalized questions that adapt to your skill level across various topics.
                  </p>

                  {/* Features */}
                  <div className="space-y-3 mb-8 text-left">
                    <div className="flex items-center text-purple-200">
                      <svg className="w-5 h-5 text-green-400 mr-3" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                      <span className="text-sm">AI-powered adaptive questions</span>
                    </div>
                    <div className="flex items-center text-purple-200">
                      <svg className="w-5 h-5 text-green-400 mr-3" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                      <span className="text-sm">Multiple topics & difficulty levels</span>
                    </div>
                    <div className="flex items-center text-purple-200">
                      <svg className="w-5 h-5 text-green-400 mr-3" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                      <span className="text-sm">Instant results & explanations</span>
                    </div>
                    <div className="flex items-center text-purple-200">
                      <svg className="w-5 h-5 text-green-400 mr-3" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                      <span className="text-sm">Face recognition proctoring</span>
                    </div>
                  </div>

                  {/* Stats */}
                  <div className="bg-purple-900/20 rounded-lg p-4 mb-6">
                    <div className="grid grid-cols-2 gap-4 text-center">
                      <div>
                        <div className="text-lg font-bold text-purple-200">15-30</div>
                        <div className="text-xs text-purple-400">Minutes</div>
                      </div>
                      <div>
                        <div className="text-lg font-bold text-purple-200">5-25</div>
                        <div className="text-xs text-purple-400">Questions</div>
                      </div>
                    </div>
                  </div>

                  {/* Button */}
                  <Link to="/assessconfig">
                    <Button 
                      variant="primary" 
                      className="w-full bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600"
                    >
                      Start MCQ Assessment
                    </Button>
                  </Link>
                </div>
              </Card>
            </motion.div>

            {/* Coding Assessment */}
            <motion.div variants={ANIMATION_VARIANTS.slideRight}>
              <Card className="p-8 h-full hover:border-green-400/50 transition-all duration-300 group">
                <div className="text-center">
                  {/* Icon */}
                  <div className="w-20 h-20 rounded-full bg-gradient-to-r from-green-500 to-blue-500 flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform duration-300">
                    <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                    </svg>
                  </div>

                  {/* Title */}
                  <h3 className="text-2xl font-bold text-purple-200 mb-4">
                    💻 Coding Challenge
                  </h3>

                  {/* Description */}
                  <p className="text-purple-300 mb-6 leading-relaxed">
                    Practice your programming skills with AI-generated coding problems. 
                    Write code, test solutions, and get detailed AI feedback on your implementation.
                  </p>

                  {/* Features */}
                  <div className="space-y-3 mb-8 text-left">
                    <div className="flex items-center text-purple-200">
                      <svg className="w-5 h-5 text-green-400 mr-3" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                      <span className="text-sm">AI-generated original problems</span>
                    </div>
                    <div className="flex items-center text-purple-200">
                      <svg className="w-5 h-5 text-green-400 mr-3" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                      <span className="text-sm">Multi-language support</span>
                    </div>
                    <div className="flex items-center text-purple-200">
                      <svg className="w-5 h-5 text-green-400 mr-3" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                      <span className="text-sm">Real-time code execution</span>
                    </div>
                    <div className="flex items-center text-purple-200">
                      <svg className="w-5 h-5 text-green-400 mr-3" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                      <span className="text-sm">Detailed AI code review</span>
                    </div>
                  </div>

                  {/* Stats */}
                  <div className="bg-green-900/20 rounded-lg p-4 mb-6">
                    <div className="grid grid-cols-2 gap-4 text-center">
                      <div>
                        <div className="text-lg font-bold text-purple-200">30-90</div>
                        <div className="text-xs text-purple-400">Minutes</div>
                      </div>
                      <div>
                        <div className="text-lg font-bold text-purple-200">1-3</div>
                        <div className="text-xs text-purple-400">Problems</div>
                      </div>
                    </div>
                  </div>

                  {/* Button */}
                  <Link to="/coding">
                    <Button 
                      variant="primary" 
                      className="w-full bg-gradient-to-r from-green-500 to-blue-500 hover:from-green-600 hover:to-blue-600"
                    >
                      Start Coding Challenge
                    </Button>
                  </Link>
                </div>
              </Card>
            </motion.div>
          </motion.div>

          {/* Back Button */}
          <motion.div
            variants={ANIMATION_VARIANTS.slideUp}
            className="text-center"
          >
            <Link to="/dashboard">
              <Button variant="outline" size="sm">
                ← Back to Dashboard
              </Button>
            </Link>
          </motion.div>
        </motion.div>
      </div>
    </>
  );
};

export default AssessmentChoice;
