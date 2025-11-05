import React, { useState, useEffect } from "react";
import { useLocation, useNavigate, Link } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Code, CheckCircle, XCircle, Clock, Cpu, TrendingUp, ArrowLeft } from "lucide-react";
import AnimatedBackground from "../components/AnimatedBackground";
import Card from "../components/ui/Card";
import Button from "../components/ui/Button";
import EmptyState from "../components/EmptyState";
import { ANIMATION_VARIANTS, TRANSITION_DEFAULTS } from "../utils/constants";

const CodingResults: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { 
    assessmentId, 
    assessmentTitle, 
    question, 
    code, 
    language, 
    testResults, 
    executionTime, 
    memoryUsed, 
    passedTests, 
    totalTests, 
    score, 
    timeTaken 
  } = location.state || {};

  const [expandedTests, setExpandedTests] = useState<Set<number>>(new Set());

  useEffect(() => {
    if (!location.state) {
      console.log("❌ No state found, redirecting to dashboard");
      navigate('/dashboard');
      return;
    }
  }, [location.state, navigate]);

  const toggleTestExpansion = (index: number) => {
    setExpandedTests((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(index)) {
        newSet.delete(index);
      } else {
        newSet.add(index);
      }
      return newSet;
    });
  };

  const formatTime = (seconds: number | undefined) => {
    if (!seconds) return 'N/A';
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const formatMemory = (bytes: number | undefined) => {
    if (!bytes) return 'N/A';
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  if (!location.state) {
    return (
      <>
        <AnimatedBackground />
        <div className="min-h-screen pt-20 px-4 relative z-10 flex items-center justify-center">
          <EmptyState
            title="No Results Found"
            message="No coding assessment results were found. Please complete a coding assessment first."
            actionText="Back to Dashboard"
            onAction={() => navigate("/dashboard")}
            icon={<Code className="w-16 h-16 mx-auto mb-4" />}
          />
        </div>
      </>
    );
  }

  const percentage = totalTests > 0 ? ((passedTests / totalTests) * 100).toFixed(2) : "0";
  const allPassed = passedTests === totalTests && totalTests > 0;

  return (
    <>
      <AnimatedBackground />
      <motion.div
        initial="initial"
        animate="animate"
        exit="exit"
        variants={ANIMATION_VARIANTS.fadeIn}
        transition={TRANSITION_DEFAULTS}
        className="container mx-auto px-4 pt-24 py-8 relative z-10"
      >
        <motion.div
          variants={ANIMATION_VARIANTS.slideDown}
          className="text-center mb-12"
        >
          <h2 className="text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-cyan-400 mb-4">
            Coding Assessment Results
          </h2>
          <p className="text-purple-200 text-xl">{assessmentTitle || "Coding Challenge"}</p>
        </motion.div>

        {/* Score Card */}
        <motion.div
          variants={ANIMATION_VARIANTS.slideUp}
          className="max-w-4xl mx-auto mb-8"
        >
          <Card className="p-8 text-center bg-gradient-to-br from-purple-900/40 to-blue-900/40 border-2 border-purple-500/30">
            {/* Circular Score */}
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.3, type: "spring", stiffness: 100 }}
              className="mb-6"
            >
              <div className={`w-48 h-48 rounded-full bg-gradient-to-r flex items-center justify-center mx-auto mb-6 shadow-2xl ${
                allPassed 
                  ? "from-green-500 to-emerald-500 shadow-green-500/50" 
                  : "from-yellow-500 to-orange-500 shadow-orange-500/50"
              }`}>
                <span className="text-5xl font-bold text-white">{percentage}%</span>
              </div>
              
              {/* Result Message */}
              <div className="flex items-center justify-center space-x-2 mb-6">
                <h3 className="text-2xl font-bold text-white">
                  {allPassed ? "🎉 All Tests Passed!" : `${passedTests}/${totalTests} Tests Passed`}
                </h3>
              </div>
            </motion.div>

            {/* Progress Bar */}
            <div className="w-full bg-purple-900/50 rounded-full h-4 mb-8">
              <motion.div 
                initial={{ width: 0 }}
                animate={{ width: `${parseFloat(percentage)}%` }}
                transition={{ duration: 1, ease: "easeOut", delay: 0.5 }}
                className={`h-4 rounded-full shadow-lg ${
                  allPassed 
                    ? "bg-gradient-to-r from-green-500 to-emerald-500" 
                    : "bg-gradient-to-r from-yellow-500 to-orange-500"
                }`}
              />
            </div>

            {/* Metric Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { 
                  label: "Tests Passed", 
                  value: `${passedTests}/${totalTests}`, 
                  icon: <CheckCircle className="w-6 h-6" />
                },
                { 
                  label: "Execution Time", 
                  value: executionTime ? `${executionTime}ms` : 'N/A', 
                  icon: <Clock className="w-6 h-6" />
                },
                { 
                  label: "Memory Used", 
                  value: formatMemory(memoryUsed), 
                  icon: <Cpu className="w-6 h-6" />
                },
                { 
                  label: "Time Taken", 
                  value: formatTime(timeTaken), 
                  icon: <TrendingUp className="w-6 h-6" />
                }
              ].map((stat, index) => (
                <motion.div
                  key={stat.label}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.7 + index * 0.1 }}
                  className="p-5 rounded-lg bg-purple-900/30 border border-purple-500/30 text-center"
                >
                  <div className="flex justify-center mb-3 text-white">
                    {stat.icon}
                  </div>
                  <p className="text-white font-bold text-xl mb-1">
                    {stat.value}
                  </p>
                  <p className="text-white/80 text-sm">{stat.label}</p>
                </motion.div>
              ))}
            </div>
          </Card>
        </motion.div>

        {/* Problem Statement */}
        {question && (
          <motion.div
            variants={ANIMATION_VARIANTS.slideUp}
            className="max-w-4xl mx-auto mb-8"
          >
            <Card className="p-6">
              <h3 className="text-2xl font-bold text-purple-200 mb-4">Problem Statement</h3>
              <p className="text-purple-100 text-lg leading-relaxed whitespace-pre-line">
                {question.problem_statement || question.description || ""}
              </p>
            </Card>
          </motion.div>
        )}

        {/* Test Results */}
        {testResults && testResults.length > 0 && (
          <motion.div
            variants={ANIMATION_VARIANTS.slideUp}
            className="max-w-4xl mx-auto mb-8"
          >
            <Card className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-2xl font-bold text-purple-200">Test Results</h3>
                <div className="flex items-center space-x-4">
                  <div
                    className={`px-3 py-1 rounded-full text-sm font-medium ${
                      allPassed
                        ? "bg-green-900/30 text-green-300 border border-green-500/30"
                        : "bg-red-900/30 text-red-300 border border-red-500/30"
                    }`}
                  >
                    {passedTests}/{totalTests} passed
                  </div>
                  <button
                    onClick={() => setExpandedTests(new Set(testResults.map((_, i) => i)))}
                    className="text-xs text-purple-400 hover:text-purple-300 transition-colors"
                  >
                    {expandedTests.size === testResults.length ? "Collapse All" : "Expand All"}
                  </button>
                </div>
              </div>
              
              <div className="space-y-3">
                {testResults.map((result: any, index: number) => {
                  const isExpanded = expandedTests.has(index);
                  return (
                    <div
                      key={index}
                      className={`p-4 rounded-lg border transition-all duration-200 ${
                        result.passed
                          ? "bg-green-900/20 border-green-500/30 hover:bg-green-900/30"
                          : "bg-red-900/20 border-red-500/30 hover:bg-red-900/30"
                      }`}
                    >
                      <div className="flex items-center justify-between mb-3">
                        <button
                          onClick={() => toggleTestExpansion(index)}
                          className="font-medium flex items-center space-x-3 hover:opacity-80 transition-opacity group"
                        >
                          <div className="flex items-center space-x-2">
                            <span className="text-sm font-medium text-purple-300">Test {index + 1}:</span>
                            <span
                              className={`font-semibold ${result.passed ? "text-green-400" : "text-red-400"}`}
                            >
                              {result.passed ? "✅ Passed" : "❌ Failed"}
                            </span>
                          </div>
                          <div className="flex items-center space-x-2">
                            {result.execution_time && (
                              <span className="text-xs text-purple-400">{result.execution_time}ms</span>
                            )}
                            <span className="text-lg group-hover:scale-110 transition-transform">
                              {isExpanded ? "▼" : "▶"}
                            </span>
                          </div>
                        </button>
                      </div>

                      {/* Expandable Test Details */}
                      <AnimatePresence>
                        {isExpanded && (
                          <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: "auto" }}
                            exit={{ opacity: 0, height: 0 }}
                            className="space-y-4 mt-4 pt-4 border-t border-purple-500/20"
                          >
                            {/* Test Case Input */}
                            <div>
                              <div className="flex items-center space-x-2 mb-2">
                                <span className="text-sm font-medium text-purple-300">Input:</span>
                              </div>
                              <div className="p-3 bg-black/30 rounded-lg border border-purple-500/20 font-mono text-sm">
                                {result.input ? (
                                  typeof result.input === "string" ? (
                                    result.input
                                  ) : (
                                    JSON.stringify(result.input, null, 2)
                                  )
                                ) : (
                                  <span className="text-purple-400 opacity-75">No input data</span>
                                )}
                              </div>
                            </div>

                            {!result.passed && (
                              <div className="space-y-4">
                                {/* Error Message */}
                                {result.error && (
                                  <div>
                                    <div className="flex items-center space-x-2 mb-2">
                                      <span className="text-sm font-medium text-red-300">Error:</span>
                                    </div>
                                    <div className="p-3 bg-red-900/30 rounded-lg border border-red-500/30 text-red-200 text-sm font-mono">
                                      {typeof result.error === "string"
                                        ? result.error
                                        : JSON.stringify(result.error)}
                                    </div>
                                  </div>
                                )}

                                {/* Expected vs Actual Output */}
                                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                                  <div>
                                    <div className="flex items-center space-x-2 mb-2">
                                      <span className="text-sm font-medium text-green-300">Expected Output:</span>
                                    </div>
                                    <div className="p-3 bg-green-900/20 rounded-lg border border-green-500/30 text-green-200 text-sm font-mono">
                                      {result.expected !== undefined && result.expected !== null ? (
                                        typeof result.expected === "string"
                                          ? result.expected
                                          : JSON.stringify(result.expected, null, 2)
                                      ) : (
                                        <span className="text-green-400 opacity-75">No expected output</span>
                                      )}
                                    </div>
                                  </div>
                                  <div>
                                    <div className="flex items-center space-x-2 mb-2">
                                      <span className="text-sm font-medium text-red-300">Your Output:</span>
                                    </div>
                                    <div className="p-3 bg-red-900/20 rounded-lg border border-red-500/30 text-red-200 text-sm font-mono">
                                      {result.output ? (
                                        typeof result.output === "string"
                                          ? result.output
                                          : JSON.stringify(result.output, null, 2)
                                      ) : (
                                        <span className="text-red-400 opacity-75">No output</span>
                                      )}
                                    </div>
                                  </div>
                                </div>
                              </div>
                            )}

                            {/* Success Message */}
                            {result.passed && (
                              <div className="flex items-center space-x-2 p-3 bg-green-900/20 rounded-lg border border-green-500/30">
                                <span className="text-green-400">✅</span>
                                <span className="text-green-300 text-sm font-medium">
                                  Output matches expected result
                                </span>
                              </div>
                            )}
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </div>
                  );
                })}
              </div>
            </Card>
          </motion.div>
        )}

        {/* Submitted Code */}
        {code && (
          <motion.div
            variants={ANIMATION_VARIANTS.slideUp}
            className="max-w-4xl mx-auto mb-8"
          >
            <Card className="p-6">
              <h3 className="text-2xl font-bold text-purple-200 mb-4">Your Solution</h3>
              <div className="bg-gray-900 rounded-lg p-4 border border-gray-700">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-400">Language: {language}</span>
                </div>
                <pre className="text-sm text-gray-100 overflow-x-auto">
                  <code>{code}</code>
                </pre>
              </div>
            </Card>
          </motion.div>
        )}

        {/* Action Buttons */}
        <motion.div
          variants={ANIMATION_VARIANTS.slideUp}
          className="text-center mb-8 space-x-4"
        >
          <Link to="/dashboard">
            <Button variant="primary" size="lg">
              Back to Dashboard
            </Button>
          </Link>
          <Button 
            variant="secondary" 
            size="lg"
            onClick={() => navigate(-1)}
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Go Back
          </Button>
        </motion.div>
      </motion.div>
    </>
  );
};

export default CodingResults;

