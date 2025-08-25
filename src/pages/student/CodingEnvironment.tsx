import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  ArrowLeft, 
  Play, 
  CheckCircle, 
  X, 
  Settings, 
  Download, 
  Upload, 
  RotateCcw,
  Copy,
  Share,
  Eye,
  EyeOff,
  Terminal,
  FileCode,
  Monitor,
  Smartphone,
  Plus,
  Sparkles
} from 'lucide-react';

interface CodingProblem {
  id: string;
  title: string;
  difficulty: 'Easy' | 'Medium' | 'Hard';
  category: string;
  description: string;
  examples: {
    input: string;
    output: string;
    explanation?: string;
  }[];
  constraints: string[];
  starterCode: {
    [key: string]: string;
  };
  testCases: {
    input: string;
    output: string;
    isHidden: boolean;
  }[];
}

interface CodingEnvironmentProps {
  problem: CodingProblem;
  onClose: () => void;
  onGenerateNew?: (difficulty: string, topic: string) => void;
}

const CodingEnvironment: React.FC<CodingEnvironmentProps> = ({ problem, onClose, onGenerateNew }) => {
  const [selectedLanguage, setSelectedLanguage] = useState('javascript');
  const [code, setCode] = useState(problem.starterCode[selectedLanguage] || '');
  const [output, setOutput] = useState('');
  const [isRunning, setIsRunning] = useState(false);
  const [testResults, setTestResults] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState<'problem' | 'solution' | 'submissions'>('problem');
  const [fontSize, setFontSize] = useState(14);
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');
  const [showLineNumbers, setShowLineNumbers] = useState(true);
  const [showGenerator, setShowGenerator] = useState(false);
  const [generatorForm, setGeneratorForm] = useState({
    topic: 'algorithms',
    difficulty: 'easy'
  });

  const languages = [
    { id: 'javascript', name: 'JavaScript', icon: '⚡' },
    { id: 'python', name: 'Python', icon: '🐍' },
    { id: 'java', name: 'Java', icon: '☕' },
    { id: 'cpp', name: 'C++', icon: '⚙️' },
    { id: 'csharp', name: 'C#', icon: '🔷' },
    { id: 'go', name: 'Go', icon: '🐹' },
    { id: 'rust', name: 'Rust', icon: '🦀' },
    { id: 'php', name: 'PHP', icon: '🐘' }
  ];

  useEffect(() => {
    setCode(problem.starterCode[selectedLanguage] || '');
  }, [selectedLanguage, problem.starterCode]);

  const API_BASE = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000';

  const handleRunCode = async () => {
    setIsRunning(true);
    setOutput('Evaluating your code with AI...\n');
    try {
      const res = await fetch(`${API_BASE}/coding/evaluate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          language: selectedLanguage,
          code,
          problem: {
            title: problem.title,
            statement: problem.description,
            constraints: problem.constraints,
            examples: problem.examples,
          },
          test_cases: problem.testCases.map(t => ({ input: t.input, output: t.output })),
        }),
      });
      const data = await res.json();
      if (data?.tests) {
        setTestResults(
          data.tests.map((t: any, idx: number) => ({
            testCase: idx + 1,
            status: t.pass ? 'passed' : 'failed',
            input: t.input,
            output: t.predicted,
            expected: t.expected,
          }))
        );
      }
      const summary = `Score: ${data?.score ?? 'N/A'}\nPassed: ${data?.passed ? 'Yes' : 'No'}\n` + (data?.feedback || '');
      setOutput(summary);
    } catch (e) {
      setOutput('Error while evaluating code.');
      console.error(e);
    } finally {
      setIsRunning(false);
    }
  };

  const handleSubmit = async () => {
    await handleRunCode();
  };

  const copyCode = () => {
    navigator.clipboard.writeText(code);
  };

  const resetCode = () => {
    setCode(problem.starterCode[selectedLanguage] || '');
  };

  const handleGenerateNew = () => {
    if (onGenerateNew) {
      onGenerateNew(generatorForm.difficulty, generatorForm.topic);
      setShowGenerator(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.9 }}
        className="h-full flex flex-col"
      >
        {/* Header */}
        <div className="bg-gradient-to-r from-[#0e0a12] to-[#221628] border-b border-white/10 p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={onClose}
                className="p-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors text-white"
              >
                <ArrowLeft className="h-5 w-5" />
              </button>
              <div>
                <h2 className="text-xl font-bold text-white">{problem.title}</h2>
                <div className="flex items-center space-x-2 mt-1">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    problem.difficulty === 'Easy' ? 'bg-green-500/20 text-green-400 border border-green-500/30' :
                    problem.difficulty === 'Medium' ? 'bg-orange-500/20 text-orange-400 border border-orange-500/30' :
                    'bg-red-500/20 text-red-400 border border-red-500/30'
                  }`}>
                    {problem.difficulty}
                  </span>
                  <span className="px-2 py-1 rounded-full text-xs font-medium bg-purple-500/20 text-purple-400 border border-purple-500/30">
                    {problem.category}
                  </span>
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              {onGenerateNew && (
                <button 
                  onClick={() => setShowGenerator(true)}
                  className="p-2 rounded-lg bg-gradient-to-r from-orange-500 to-purple-600 hover:from-orange-600 hover:to-purple-700 transition-all text-white"
                  title="Generate New Problem"
                >
                  <Plus className="h-4 w-4" />
                </button>
              )}
              <button className="p-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors text-white">
                <Settings className="h-5 w-5" />
              </button>
              <button className="p-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors text-white">
                <Share className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>

        {/* Problem Generator Modal */}
        <AnimatePresence>
          {showGenerator && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 bg-black/60 flex items-center justify-center z-50"
            >
              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.9, opacity: 0 }}
                className="bg-[#1a1a2e] border border-white/20 rounded-2xl p-6 w-96"
              >
                <div className="flex items-center mb-4">
                  <Sparkles className="h-5 w-5 text-orange-400 mr-2" />
                  <h3 className="text-lg font-semibold text-white">Generate New Problem</h3>
                </div>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-white/80 mb-2">Topic</label>
                    <input
                      type="text"
                      value={generatorForm.topic}
                      onChange={(e) => setGeneratorForm({...generatorForm, topic: e.target.value})}
                      placeholder="e.g., arrays, trees, dynamic programming"
                      className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-orange-500/50"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-white/80 mb-2">Difficulty</label>
                    <select
                      value={generatorForm.difficulty}
                      onChange={(e) => setGeneratorForm({...generatorForm, difficulty: e.target.value})}
                      className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-orange-500/50"
                    >
                      <option value="easy" className="bg-[#1a1a2e]">Easy</option>
                      <option value="medium" className="bg-[#1a1a2e]">Medium</option>
                      <option value="hard" className="bg-[#1a1a2e]">Hard</option>
                    </select>
                  </div>
                </div>
                
                <div className="flex space-x-3 mt-6">
                  <button
                    onClick={() => setShowGenerator(false)}
                    className="flex-1 px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg text-white transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleGenerateNew}
                    className="flex-1 px-4 py-2 bg-gradient-to-r from-orange-500 to-purple-600 hover:from-orange-600 hover:to-purple-700 rounded-lg text-white font-medium transition-all"
                  >
                    Generate
                  </button>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Main Content */}
        <div className="flex-1 flex overflow-hidden">
          {/* Left Panel - Problem Description */}
          <div className="w-1/3 bg-white/5 border-r border-white/10 flex flex-col">
            {/* Tabs */}
            <div className="flex border-b border-white/10">
              <button
                onClick={() => setActiveTab('problem')}
                className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
                  activeTab === 'problem' 
                    ? 'text-white border-b-2 border-orange-500 bg-white/5' 
                    : 'text-white/70 hover:text-white hover:bg-white/5'
                }`}
              >
                Problem
              </button>
              <button
                onClick={() => setActiveTab('solution')}
                className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
                  activeTab === 'solution' 
                    ? 'text-white border-b-2 border-orange-500 bg-white/5' 
                    : 'text-white/70 hover:text-white hover:bg-white/5'
                }`}
              >
                Solution
              </button>
              <button
                onClick={() => setActiveTab('submissions')}
                className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
                  activeTab === 'submissions' 
                    ? 'text-white border-b-2 border-orange-500 bg-white/5' 
                    : 'text-white/70 hover:text-white hover:bg-white/5'
                }`}
              >
                Submissions
              </button>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-6">
              <AnimatePresence mode="wait">
                {activeTab === 'problem' && (
                  <motion.div
                    key="problem"
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                    className="space-y-6"
                  >
                    <div>
                      <h3 className="text-lg font-semibold text-white mb-3">Problem Description</h3>
                      <p className="text-white/80 leading-relaxed">{problem.description}</p>
                    </div>

                    <div>
                      <h4 className="text-md font-semibold text-white mb-3">Examples</h4>
                      <div className="space-y-4">
                        {problem.examples.map((example, index) => (
                          <div key={index} className="bg-white/5 rounded-lg p-4 border border-white/10">
                            <div className="text-sm text-white/60 mb-2">Example {index + 1}:</div>
                            <div className="space-y-2">
                              <div>
                                <span className="text-sm text-white/70">Input: </span>
                                <code className="text-sm bg-white/10 px-2 py-1 rounded text-orange-300">{example.input}</code>
                              </div>
                              <div>
                                <span className="text-sm text-white/70">Output: </span>
                                <code className="text-sm bg-white/10 px-2 py-1 rounded text-green-300">{example.output}</code>
                              </div>
                              {example.explanation && (
                                <div>
                                  <span className="text-sm text-white/70">Explanation: </span>
                                  <span className="text-sm text-white/80">{example.explanation}</span>
                                </div>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div>
                      <h4 className="text-md font-semibold text-white mb-3">Constraints</h4>
                      <ul className="space-y-1">
                        {problem.constraints.map((constraint, index) => (
                          <li key={index} className="text-sm text-white/70 flex items-start">
                            <span className="text-orange-400 mr-2">•</span>
                            {constraint}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </motion.div>
                )}

                {activeTab === 'solution' && (
                  <motion.div
                    key="solution"
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                    className="space-y-4"
                  >
                    <div className="text-center py-8">
                      <div className="w-16 h-16 rounded-full bg-gradient-to-r from-orange-500 to-purple-600 flex items-center justify-center mx-auto mb-4">
                        <Eye className="h-8 w-8 text-white" />
                      </div>
                      <h3 className="text-lg font-semibold text-white mb-2">Solution Available</h3>
                      <p className="text-white/70 mb-4">Complete this problem to view the solution</p>
                      <button className="px-4 py-2 bg-gradient-to-r from-orange-500 to-purple-600 hover:from-orange-600 hover:to-purple-700 rounded-lg text-white font-medium transition-all">
                        Complete Problem First
                      </button>
                    </div>
                  </motion.div>
                )}

                {activeTab === 'submissions' && (
                  <motion.div
                    key="submissions"
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                    className="space-y-4"
                  >
                    <div className="text-center py-8">
                      <div className="w-16 h-16 rounded-full bg-gradient-to-r from-orange-500 to-purple-600 flex items-center justify-center mx-auto mb-4">
                        <FileCode className="h-8 w-8 text-white" />
                      </div>
                      <h3 className="text-lg font-semibold text-white mb-2">No Submissions Yet</h3>
                      <p className="text-white/70">Submit your solution to see it here</p>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>

          {/* Right Panel - Code Editor */}
          <div className="flex-1 flex flex-col">
            {/* Language Selection and Controls */}
            <div className="bg-white/5 border-b border-white/10 p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <select
                    value={selectedLanguage}
                    onChange={(e) => setSelectedLanguage(e.target.value)}
                    className="px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-orange-500/50"
                  >
                    {languages.map((lang) => (
                      <option key={lang.id} value={lang.id} className="bg-gray-800">
                        {lang.icon} {lang.name}
                      </option>
                    ))}
                  </select>
                  
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={copyCode}
                      className="p-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors text-white"
                      title="Copy Code"
                    >
                      <Copy className="h-4 w-4" />
                    </button>
                    <button
                      onClick={resetCode}
                      className="p-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors text-white"
                      title="Reset Code"
                    >
                      <RotateCcw className="h-4 w-4" />
                    </button>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <button
                    onClick={handleRunCode}
                    disabled={isRunning}
                    className="px-4 py-2 bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 disabled:opacity-50 rounded-lg text-white font-medium transition-all flex items-center space-x-2"
                  >
                    <Play className="h-4 w-4" />
                    <span>Run</span>
                  </button>
                  <button
                    onClick={handleSubmit}
                    disabled={isRunning}
                    className="px-4 py-2 bg-gradient-to-r from-orange-500 to-purple-600 hover:from-orange-600 hover:to-purple-700 disabled:opacity-50 rounded-lg text-white font-medium transition-all flex items-center space-x-2"
                  >
                    <CheckCircle className="h-4 w-4" />
                    <span>Submit</span>
                  </button>
                </div>
              </div>
            </div>

            {/* Code Editor */}
            <div className="flex-1 flex">
              <div className="flex-1 bg-[#1e1e1e] p-4">
                <div className="h-full bg-[#1e1e1e] rounded-lg border border-white/10 overflow-hidden">
                  <textarea
                    value={code}
                    onChange={(e) => setCode(e.target.value)}
                    className="w-full h-full bg-transparent text-white p-4 font-mono text-sm resize-none focus:outline-none"
                    style={{ fontSize: `${fontSize}px` }}
                    placeholder="Write your code here..."
                  />
                </div>
              </div>

              {/* Output Panel */}
              <div className="w-1/3 bg-[#0d1117] border-l border-white/10 flex flex-col">
                <div className="p-4 border-b border-white/10">
                  <h3 className="text-lg font-semibold text-white">Output</h3>
                </div>
                <div className="flex-1 p-4 overflow-y-auto">
                  <pre className="text-sm text-white/90 font-mono whitespace-pre-wrap">
                    {output}
                  </pre>
                  
                  {testResults.length > 0 && (
                    <div className="mt-6">
                      <h4 className="text-md font-semibold text-white mb-3">Test Results</h4>
                      <div className="space-y-2">
                        {testResults.map((result, index) => (
                          <div key={index} className="p-3 bg-white/5 rounded-lg border border-white/10">
                            <div className="flex items-center justify-between mb-2">
                              <span className="text-sm font-medium text-white">Test Case {result.testCase}</span>
                              <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                result.status === 'passed' 
                                  ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                                  : 'bg-red-500/20 text-red-400 border border-red-500/30'
                              }`}>
                                {result.status === 'passed' ? '✓ Passed' : '✗ Failed'}
                              </span>
                            </div>
                            <div className="text-xs text-white/70 space-y-1">
                              <div>Input: <code className="bg-white/10 px-1 rounded">{result.input}</code></div>
                              <div>Output: <code className="bg-white/10 px-1 rounded">{result.output}</code></div>
                              <div>Expected: <code className="bg-white/10 px-1 rounded">{result.expected}</code></div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default CodingEnvironment;
