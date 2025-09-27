import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { User, CodingProblem, CodingTestResult } from '../types';
import { useTheme } from '../contexts/ThemeContext';
import { useToast } from '../contexts/ToastContext';
import AnimatedBackground from '../components/AnimatedBackground';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import { Editor } from '@monaco-editor/react';
import api from '../utils/api';
import { ANIMATION_VARIANTS } from '../utils/constants';

interface CodingProblemPageProps {
  user: User;
}

const CodingProblemPage: React.FC<CodingProblemPageProps> = ({ user }) => {
  const { problemId } = useParams<{ problemId: string }>();
  const { colorScheme } = useTheme();
  const { success, error: showError, info } = useToast();
  
  const [problem, setProblem] = useState<CodingProblem | null>(null);
  const [code, setCode] = useState<string>('');
  const [language, setLanguage] = useState<string>('python');
  const [loading, setLoading] = useState(true);
  const [executing, setExecuting] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [testResults, setTestResults] = useState<CodingTestResult[]>([]);
  const [showHints, setShowHints] = useState(false);
  const [hintsUsed, setHintsUsed] = useState(0);
  const [sessionId, setSessionId] = useState<string>('');
  const [keystrokes, setKeystrokes] = useState(0);
  const [startTime] = useState(Date.now());
  const [autocompleteEnabled, setAutocompleteEnabled] = useState(true);
  const [useJudge0, setUseJudge0] = useState(false);

  const languages = [
    { value: 'python', label: 'Python', template: '# Write your solution here\ndef solution():\n    pass' },
    { value: 'javascript', label: 'JavaScript', template: '// Write your solution here\nfunction solution() {\n    // Your code\n}' },
    { value: 'java', label: 'Java', template: '// Write your solution here\npublic class Solution {\n    public void solution() {\n        // Your code\n    }\n}' },
    { value: 'cpp', label: 'C++', template: '// Write your solution here\n#include <iostream>\nusing namespace std;\n\nint main() {\n    // Your code\n    return 0;\n}' }
  ];

  // Get the correct Monaco language ID
  const getMonacoLanguage = (lang: string) => {
    const languageMap: { [key: string]: string } = {
      'python': 'python',
      'javascript': 'javascript',
      'java': 'java',
      'cpp': 'cpp'
    };
    return languageMap[lang] || 'python';
  };

  useEffect(() => {
    if (problemId) {
      fetchProblem();
      startSession();
    }
  }, [problemId]);

  useEffect(() => {
    // Set default template when language changes
    const selectedLang = languages.find(lang => lang.value === language);
    if (selectedLang) {
      // Only set template if code is empty or just whitespace
      if (!code.trim() || code.trim() === '') {
        setCode(selectedLang.template);
      }
    }
  }, [language]);

  const fetchProblem = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/api/coding/problems/${problemId}`);
      
      if (response.data.success) {
        setProblem(response.data.problem);
      } else {
        showError('Problem not found');
      }
    } catch (error) {
      showError('Failed to load problem');
    } finally {
      setLoading(false);
    }
  };

  const startSession = async () => {
    try {
      const response = await api.post('/api/coding/sessions/start', {
        problem_id: problemId
      });
      
      if (response.data.success) {
        setSessionId(response.data.session_id);
      }
    } catch (error) {
      console.error('Failed to start session:', error);
    }
  };

  const updateSession = async (updates: any) => {
    if (!sessionId) return;
    
    try {
      await api.put(`/api/coding/sessions/${sessionId}`, updates);
    } catch (error) {
      console.error('Failed to update session:', error);
    }
  };

  const handleCodeChange = (newCode: string) => {
    setCode(newCode);
    setKeystrokes(prev => prev + 1);
    
    // Update session every 50 keystrokes
    if (keystrokes % 50 === 0) {
      updateSession({
        keystrokes: keystrokes + 1,
        lines_of_code: newCode.split('\n').length
      });
    }
  };

  const runCode = async (codeToRun?: string) => {
    const codeToExecute = codeToRun || code;
    
    if (!problem || !codeToExecute.trim()) {
      showError('Please write some code first');
      return;
    }

    // Validate code before execution
    const validation = validateCode(codeToExecute);
    if (!validation.isValid) {
      showError(`Code validation failed: ${validation.errors.join(', ')}`);
      return;
    }

    setExecuting(true);
    setTestResults([]);

    try {
      // Use visible test cases for running
      const visibleTestCases = problem.examples.map((example, index) => ({
        input: parseInput(example.input),
        output: parseOutput(example.output),
        description: `Example ${index + 1}`
      }));

      const response = await api.post('/api/execute/execute', {
        code: codeToExecute,
        language,
        test_cases: visibleTestCases,
        timeout: 10,
        use_judge0: useJudge0
      });

      if (response.data.success) {
        const results = response.data.results || [];
        setTestResults(results);
        
        const passed = response.data.passed_tests || 0;
        const total = response.data.total_tests || 0;
        
        if (passed === total && total > 0) {
          success(`All ${total} test cases passed! 🎉`);
        } else if (total > 0) {
          const failedTests = results.filter((r: any) => !r.passed);
          if (failedTests.length > 0) {
            info(`${passed}/${total} test cases passed. Check the results below for details.`);
          } else {
            info(`${passed}/${total} test cases passed`);
          }
        } else {
          success('Code executed successfully!');
        }

        // Update session with detailed results
        updateSession({ 
          test_runs: 1,
          last_test_results: {
            passed,
            total,
            execution_time: results.reduce((sum: number, r: any) => sum + (r.execution_time || 0), 0)
          }
        });
      } else {
        showError(response.data.error || 'Execution failed');
      }
    } catch (error: any) {
      console.error('Execution error:', error);
      const errorMessage = error.response?.data?.detail || 
                          error.response?.data?.error || 
                          'Code execution failed. Please check your code.';
      showError(errorMessage);
      
      // Update session with error
      updateSession({ 
        test_runs: 1,
        last_error: errorMessage
      });
    } finally {
      setExecuting(false);
    }
  };

  const submitSolution = async (codeToSubmit?: string) => {
    const codeToExecute = codeToSubmit || code;
    
    if (!problem || !codeToExecute.trim()) {
      showError('Please write some code first');
      return;
    }

    // Validate code before submission
    const validation = validateCode(codeToExecute);
    if (!validation.isValid) {
      showError(`Code validation failed: ${validation.errors.join(', ')}`);
      return;
    }

    setSubmitting(true);

    try {
      // First run tests to validate with visible examples
      const visibleTestCases = problem.examples.map((example, index) => ({
        input: parseInput(example.input),
        output: parseOutput(example.output),
        description: `Example ${index + 1}`
      }));

      const testResponse = await api.post('/api/execute/execute', {
        code: codeToExecute,
        language,
        test_cases: visibleTestCases,
        timeout: 10,
        use_judge0: useJudge0
      });

      if (!testResponse.data.success) {
        showError('Code failed test cases. Please fix your solution.');
        setTestResults(testResponse.data.results || []);
        return;
      }

      const passedTests = testResponse.data.passed_tests || 0;
      const totalTests = testResponse.data.total_tests || 0;

      if (passedTests < totalTests) {
        showError(`Only ${passedTests}/${totalTests} test cases passed. Please fix your solution before submitting.`);
        setTestResults(testResponse.data.results || []);
        return;
      }

      // Submit to coding platform
      const response = await api.post('/api/coding/submit', {
        problem_id: problemId,
        code: codeToExecute,
        language,
        session_id: sessionId
      });

      if (response.data.success) {
        const submission = response.data.submission;
        
        if (submission.status === 'accepted') {
          success('🎉 Solution Accepted! Great job!');
          
          // End session with success
          if (sessionId) {
            await api.post(`/api/coding/sessions/${sessionId}/end`, {
              final_status: 'accepted',
              solution_code: codeToExecute,
              completion_time: Date.now() - startTime
            });
          }
          
          // Navigate to submission details
          setTimeout(() => {
            window.location.href = `/coding/submission/${submission.id}`;
          }, 2000);
        } else {
          const statusMessages = {
            wrong_answer: 'Wrong Answer - Some test cases failed',
            time_limit_exceeded: 'Time Limit Exceeded - Your solution is too slow',
            runtime_error: 'Runtime Error - Check your code for errors',
            compilation_error: 'Compilation Error - Fix syntax errors',
            memory_limit_exceeded: 'Memory Limit Exceeded - Your solution uses too much memory',
            presentation_error: 'Presentation Error - Check your output format'
          };
          
          const errorMessage = statusMessages[submission.status as keyof typeof statusMessages] || 'Submission failed';
          showError(errorMessage);
          setTestResults(submission.test_results || []);
          
          // Update session with failure
          updateSession({ 
            submissions: 1,
            last_submission_status: submission.status,
            last_error: errorMessage
          });
        }
      } else {
        showError(response.data.error || 'Submission failed');
      }
    } catch (error: any) {
      console.error('Submission error:', error);
      const errorMessage = error.response?.data?.detail || 
                          error.response?.data?.error || 
                          'Failed to submit solution. Please try again.';
      showError(errorMessage);
      
      // Update session with error
      updateSession({ 
        submissions: 1,
        last_error: errorMessage
      });
    } finally {
      setSubmitting(false);
    }
  };

  const showHint = () => {
    if (!problem || hintsUsed >= problem.hints.length) return;
    
    setShowHints(true);
    setHintsUsed(prev => prev + 1);
    
    // Update session
    updateSession({ hints_used: 1 });
  };

  const parseInput = (inputStr: string): any => {
    try {
      // Enhanced input parsing for different formats
      if (inputStr.includes('=')) {
        const match = inputStr.match(/=\s*(.+)$/);
        if (match) {
          return JSON.parse(match[1].replace(/'/g, '"'));
        }
      }
      
      // Try to parse as JSON directly
      if (inputStr.startsWith('[') || inputStr.startsWith('{')) {
        return JSON.parse(inputStr.replace(/'/g, '"'));
      }
      
      // Handle space-separated values
      if (inputStr.includes(' ')) {
        const parts = inputStr.split(' ').map(part => {
          const num = parseFloat(part);
          return isNaN(num) ? part : num;
        });
        return parts.length === 1 ? parts[0] : parts;
      }
      
      // Try to parse as number
      const num = parseFloat(inputStr);
      return isNaN(num) ? inputStr : num;
    } catch {
      return inputStr;
    }
  };

  const parseOutput = (outputStr: string): any => {
    try {
      // Enhanced output parsing
      if (outputStr.startsWith('[') || outputStr.startsWith('{')) {
        return JSON.parse(outputStr.replace(/'/g, '"'));
      }
      
      // Try to parse as number
      const num = parseFloat(outputStr);
      if (!isNaN(num)) {
        return num;
      }
      
      return outputStr;
    } catch {
      return outputStr;
    }
  };

  // Helper function to validate code before execution
  const validateCode = (code: string): { isValid: boolean; errors: string[] } => {
    const errors: string[] = [];
    
    if (!code.trim()) {
      errors.push('Code cannot be empty');
    }
    
    if (language === 'python') {
      // Basic Python syntax checks
      const lines = code.split('\n');
      let indentLevel = 0;
      
      for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        if (line.trim()) {
          const currentIndent = line.length - line.trimStart().length;
          if (currentIndent > indentLevel + 4) {
            errors.push(`Line ${i + 1}: Unexpected indentation`);
          }
          if (line.trim().endsWith(':')) {
            indentLevel = currentIndent;
          }
        }
      }
    }
    
    return { isValid: errors.length === 0, errors };
  };

  const getDifficultyColor = (difficulty: string) => {
    const colors = {
      easy: 'text-green-400 bg-green-400/10 border-green-400/30',
      medium: 'text-yellow-400 bg-yellow-400/10 border-yellow-400/30',
      hard: 'text-red-400 bg-red-400/10 border-red-400/30'
    };
    return colors[difficulty as keyof typeof colors] || colors.medium;
  };

  if (loading) {
    return (
      <div className="min-h-screen pt-20 px-4 flex items-center justify-center">
        <LoadingSpinner size="lg" text="Loading problem..." />
      </div>
    );
  }

  if (!problem) {
    return (
      <div className="min-h-screen pt-20 px-4 flex items-center justify-center">
        <Card className="p-8 text-center">
          <div className="text-6xl mb-4">❌</div>
          <h2 className="text-2xl font-bold text-purple-200 mb-2">Problem Not Found</h2>
          <p className="text-purple-300 mb-6">The requested problem could not be loaded.</p>
          <Button onClick={() => window.location.href = '/coding'} variant="primary">
            Back to Coding Platform
          </Button>
        </Card>
      </div>
    );
  }

  return (
    <>
      <AnimatedBackground />
      <div className="min-h-screen pt-20 px-4 relative z-10">
        <div className="w-[95%] mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-[45%_55%] xl:grid-cols-[40%_60%] gap-6" style={{ minHeight: 'calc(100vh - 120px)' }}>
            {/* Problem Description */}
            <motion.div
              variants={ANIMATION_VARIANTS.slideLeft}
              initial="initial"
              animate="animate"
              className="overflow-y-auto"
              style={{ height: 'calc(100vh - 140px)', minHeight: '600px' }}
            >
              <Card className="p-6 h-full">
                {/* Header */}
                <div className="flex items-start justify-between mb-6">
                  <div>
                    <h1 className="text-2xl font-bold text-purple-200 mb-2">
                      {problem.title}
                    </h1>
                    <div className="flex items-center space-x-3">
                      <span className={`px-3 py-1 rounded-full text-sm border ${getDifficultyColor(problem.difficulty)}`}>
                        {problem.difficulty}
                      </span>
                      <span className="text-sm text-purple-400 bg-purple-500/20 px-2 py-1 rounded">
                        {problem.topic}
                      </span>
                    </div>
                  </div>
                  
                  <Button
                    onClick={() => window.location.href = '/coding'}
                    variant="outline"
                    size="sm"
                  >
                    ← Back
                  </Button>
                </div>

                {/* Description */}
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-purple-200 mb-3">Description</h3>
                  <p className="text-purple-300 leading-relaxed whitespace-pre-line">
                    {problem.description}
                  </p>
                </div>

                {/* Examples */}
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-purple-200 mb-3">Examples</h3>
                  <div className="space-y-4">
                    {problem.examples.map((example, index) => (
                      <div key={index} className="bg-purple-900/20 rounded-lg p-4">
                        <div className="font-semibold text-purple-200 mb-2">
                          Example {index + 1}:
                        </div>
                        <div className="space-y-2 text-sm">
                          <div>
                            <span className="text-purple-300">Input: </span>
                            <code className="text-purple-100 bg-purple-800/30 px-2 py-1 rounded">
                              {typeof example.input === 'string' ? example.input : JSON.stringify(example.input)}
                            </code>
                          </div>
                          <div>
                            <span className="text-purple-300">Output: </span>
                            <code className="text-purple-100 bg-purple-800/30 px-2 py-1 rounded">
                              {typeof example.output === 'string' ? example.output : JSON.stringify(example.output)}
                            </code>
                          </div>
                          {example.explanation && (
                            <div>
                              <span className="text-purple-300">Explanation: </span>
                              <span className="text-purple-200">{example.explanation}</span>
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Constraints */}
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-purple-200 mb-3">Constraints</h3>
                  <ul className="space-y-1">
                    {problem.constraints.map((constraint, index) => (
                      <li key={index} className="text-purple-300 text-sm">
                        • {constraint}
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Hints */}
                <div className="mb-6">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="text-lg font-semibold text-purple-200">
                      Hints ({hintsUsed}/{problem.hints.length})
                    </h3>
                    {hintsUsed < problem.hints.length && (
                      <Button
                        onClick={showHint}
                        variant="outline"
                        size="sm"
                      >
                        💡 Show Hint
                      </Button>
                    )}
                  </div>
                  
                  {showHints && (
                    <div className="space-y-2">
                      {problem.hints.slice(0, hintsUsed).map((hint, index) => (
                        <motion.div
                          key={index}
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-3"
                        >
                          <div className="text-sm text-blue-200">
                            <span className="font-semibold">Hint {index + 1}: </span>
                            {hint}
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Expected Complexity */}
                <div>
                  <h3 className="text-lg font-semibold text-purple-200 mb-3">Expected Complexity</h3>
                  <div className="flex space-x-4 text-sm">
                    <div>
                      <span className="text-purple-300">Time: </span>
                      <code className="text-purple-100 bg-purple-800/30 px-2 py-1 rounded">
                        {problem.expected_complexity.time}
                      </code>
                    </div>
                    <div>
                      <span className="text-purple-300">Space: </span>
                      <code className="text-purple-100 bg-purple-800/30 px-2 py-1 rounded">
                        {problem.expected_complexity.space}
                      </code>
                    </div>
                  </div>
                </div>
              </Card>
            </motion.div>

            {/* Code Editor */}
            <motion.div
              variants={ANIMATION_VARIANTS.slideRight}
              initial="initial"
              animate="animate"
              className="flex flex-col"
            >
              <div style={{ height: 'calc(100vh - 140px)', minHeight: '600px' }}>
                <Card className="p-6 flex flex-col h-full">
                {/* Editor Header */}
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-4">
                    <select
                      value={language}
                      onChange={(e) => setLanguage(e.target.value)}
                      className="px-3 py-1 bg-purple-800/30 border border-purple-500/30 rounded text-purple-100 text-sm focus:outline-none focus:border-purple-400"
                    >
                      {languages.map(lang => (
                        <option key={lang.value} value={lang.value}>
                          {lang.label}
                        </option>
                      ))}
                    </select>
                    
                    <div className="flex items-center space-x-4">
                      <label className="flex items-center space-x-2 text-sm text-purple-300">
                        <input
                          type="checkbox"
                          checked={autocompleteEnabled}
                          onChange={(e) => setAutocompleteEnabled(e.target.checked)}
                          className="w-4 h-4 text-purple-600 bg-purple-800/30 border-purple-500/30 rounded focus:ring-purple-400 focus:ring-2"
                        />
                        <span>Autocomplete</span>
                      </label>
                      
                      <label className="flex items-center space-x-2 text-sm text-purple-300">
                        <input
                          type="checkbox"
                          checked={useJudge0}
                          onChange={(e) => setUseJudge0(e.target.checked)}
                          className="w-4 h-4 text-purple-600 bg-purple-800/30 border-purple-500/30 rounded focus:ring-purple-400 focus:ring-2"
                        />
                        <span>Judge0 API</span>
                      </label>
                    </div>
                    
                    <div className="text-sm text-purple-400">
                      Time: {Math.floor((Date.now() - startTime) / 1000)}s
                    </div>
                  </div>

                  <div className="flex space-x-2">
                    <Button
                      onClick={() => runCode()}
                      disabled={executing || !code.trim()}
                      variant="outline"
                      size="sm"
                    >
                      {executing ? (
                        <>
                          <LoadingSpinner size="sm" />
                          <span className="ml-1">Running...</span>
                        </>
                      ) : (
                        '▶️ Run'
                      )}
                    </Button>
                    
                    <Button
                      onClick={() => submitSolution()}
                      disabled={submitting || !code.trim()}
                      variant="primary"
                      size="sm"
                    >
                      {submitting ? (
                        <>
                          <LoadingSpinner size="sm" />
                          <span className="ml-1">Submitting...</span>
                        </>
                      ) : (
                        '🚀 Submit'
                      )}
                    </Button>
                  </div>
                </div>

                {/* Monaco Code Editor */}
                <div 
                  className="border border-purple-500/20 rounded-lg overflow-hidden"
                  style={{ 
                    height: 'calc(100vh - 280px)', 
                    minHeight: '500px',
                    flex: '1 1 auto'
                  }}
                >
                  <Editor
                    height="100%"
                    width="100%"
                    defaultLanguage={getMonacoLanguage(language)}
                    language={getMonacoLanguage(language)}
                    theme={colorScheme === 'dark' ? 'vs-dark' : 'light'}
                    value={code}
                    onChange={(value) => handleCodeChange(value || '')}
                    onMount={(editor, monaco) => {
                      // Configure language-specific features
                      if (language === 'javascript') {
                        // Enable JavaScript-specific features
                        monaco.languages.typescript.javascriptDefaults.setDiagnosticsOptions({
                          noSemanticValidation: false,
                          noSyntaxValidation: false
                        });
                      }
                      
                      // Configure editor for better autocomplete
                      editor.updateOptions({
                        suggest: {
                          showKeywords: autocompleteEnabled,
                          showSnippets: autocompleteEnabled,
                          showFunctions: autocompleteEnabled,
                          showConstructors: autocompleteEnabled,
                          showFields: autocompleteEnabled,
                          showVariables: autocompleteEnabled,
                          showClasses: autocompleteEnabled,
                          showStructs: autocompleteEnabled,
                          showInterfaces: autocompleteEnabled,
                          showModules: autocompleteEnabled,
                          showProperties: autocompleteEnabled,
                          showEvents: autocompleteEnabled,
                          showOperators: autocompleteEnabled,
                          showUnits: autocompleteEnabled,
                          showValues: autocompleteEnabled,
                          showConstants: autocompleteEnabled,
                          showEnums: autocompleteEnabled,
                          showEnumMembers: autocompleteEnabled,
                          showColors: autocompleteEnabled,
                          showFiles: autocompleteEnabled,
                          showReferences: autocompleteEnabled,
                          showFolders: autocompleteEnabled,
                          showTypeParameters: autocompleteEnabled,
                          showIssues: autocompleteEnabled,
                          showUsers: autocompleteEnabled,
                          showWords: autocompleteEnabled,
                        }
                      });
                    }}
                    options={{
                      // Basic editor settings
                      minimap: { enabled: false },
                      fontSize: 18,
                      wordWrap: 'on',
                      automaticLayout: true,
                      scrollBeyondLastLine: false,
                      smoothScrolling: true,
                      lineNumbers: 'on',
                      renderLineHighlight: 'all',
                      cursorBlinking: 'blink',
                      cursorSmoothCaretAnimation: 'on',
                      padding: { top: 20, bottom: 20 },
                      folding: true,
                      foldingStrategy: 'indentation',
                      showFoldingControls: 'always',
                      lineHeight: 1.6,
                      
                      // Syntax and error detection
                      glyphMargin: true,
                      lightbulb: {},
                      codeLens: true,
                      occurrencesHighlight: 'singleFile',
                      selectionHighlight: true,
                      bracketPairColorization: { enabled: true },
                      guides: {
                        bracketPairs: true,
                        indentation: true,
                        highlightActiveIndentation: true
                      },
                      
                      // Error detection and validation
                      // Validation is handled by language services
                      
                      // Autocomplete and suggestions
                      quickSuggestions: autocompleteEnabled ? {
                        other: true,
                        comments: true,
                        strings: true
                      } : false,
                      suggestOnTriggerCharacters: autocompleteEnabled,
                      acceptSuggestionOnEnter: autocompleteEnabled ? 'on' : 'off',
                      tabCompletion: autocompleteEnabled ? 'on' : 'off',
                      wordBasedSuggestions: autocompleteEnabled ? 'currentDocument' : 'off',
                      
                      // Language-specific autocomplete
                      suggest: {
                        showKeywords: autocompleteEnabled,
                        showSnippets: autocompleteEnabled,
                        showFunctions: autocompleteEnabled,
                        showConstructors: autocompleteEnabled,
                        showFields: autocompleteEnabled,
                        showVariables: autocompleteEnabled,
                        showClasses: autocompleteEnabled,
                        showStructs: autocompleteEnabled,
                        showInterfaces: autocompleteEnabled,
                        showModules: autocompleteEnabled,
                        showProperties: autocompleteEnabled,
                        showEvents: autocompleteEnabled,
                        showOperators: autocompleteEnabled,
                        showUnits: autocompleteEnabled,
                        showValues: autocompleteEnabled,
                        showConstants: autocompleteEnabled,
                        showEnums: autocompleteEnabled,
                        showEnumMembers: autocompleteEnabled,
                        showColors: autocompleteEnabled,
                        showFiles: autocompleteEnabled,
                        showReferences: autocompleteEnabled,
                        showFolders: autocompleteEnabled,
                        showTypeParameters: autocompleteEnabled,
                        showIssues: autocompleteEnabled,
                        showUsers: autocompleteEnabled,
                        showWords: autocompleteEnabled,
                      },
                      
                      // Parameter hints
                      parameterHints: {
                        enabled: autocompleteEnabled,
                        cycle: true
                      },
                      
                      // Hover information
                      hover: {
                        enabled: true,
                        delay: 300
                      },
                      
                      // Formatting
                      formatOnPaste: true,
                      formatOnType: true,
                      
                      // Accessibility
                      accessibilitySupport: 'auto',
                      
                      // Multi-cursor
                      multiCursorModifier: 'ctrlCmd',
                      
                      // Find and replace
                      find: {
                        seedSearchStringFromSelection: 'always',
                        autoFindInSelection: 'multiline'
                      }
                    }}
                  />
                </div>

                {/* Test Results */}
                {testResults.length > 0 && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-4 max-h-48 overflow-y-auto border-t border-purple-500/20 pt-4"
                  >
                    <h4 className="text-sm font-semibold text-purple-200 mb-2">Test Results</h4>
                    <div className="space-y-2">
                      {testResults.map((result, index) => (
                        <div
                          key={index}
                          className={`p-3 rounded-lg border text-sm ${
                            result.passed
                              ? 'bg-green-900/20 border-green-500/30 text-green-200'
                              : 'bg-red-900/20 border-red-500/30 text-red-200'
                          }`}
                        >
                          <div className="flex items-center justify-between mb-1">
                            <span className="font-medium">
                              Test {index + 1}: {result.passed ? '✅ Passed' : '❌ Failed'}
                            </span>
                            <span className="text-xs opacity-75">
                              {result.execution_time}ms
                            </span>
                          </div>
                          
                          {!result.passed && (
                            <div className="space-y-1 text-xs opacity-90">
                              {result.error ? (
                                <div>Error: {typeof result.error === 'string' ? result.error : JSON.stringify(result.error)}</div>
                              ) : (
                                <>
                                  <div>Expected: {typeof result.expected === 'string' ? result.expected : JSON.stringify(result.expected)}</div>
                                  <div>Got: {typeof result.output === 'string' ? result.output : JSON.stringify(result.output)}</div>
                                </>
                              )}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </motion.div>
                )}
                </Card>
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </>
  );
};

export default CodingProblemPage;
