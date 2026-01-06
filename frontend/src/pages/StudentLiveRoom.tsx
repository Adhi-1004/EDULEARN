"use client"

import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { useAuth } from '../hooks/useAuth'
import { useToast } from '../contexts/ToastContext'
import AnimatedBackground from '../components/AnimatedBackground'

const StudentLiveRoom: React.FC = () => {
    const { batchId } = useParams<{ batchId: string }>()
    const { user } = useAuth()
    const { success } = useToast()

    const [ws, setWs] = useState<WebSocket | null>(null)
    const [status, setStatus] = useState<'CONNECTING' | 'WAITING' | 'QUIZ' | 'POLL' | 'MATERIAL'>('CONNECTING')
    const [payload, setPayload] = useState<any>(null)
    const [selectedOption, setSelectedOption] = useState<number | null>(null)
    const [answerSubmitted, setAnswerSubmitted] = useState(false)

    useEffect(() => {
        if (!user || !batchId) return

        let socket: WebSocket | null = null;
        let retryCount = 0;
        const MAX_RETRIES = 3;

        const connect = () => {
            const token = localStorage.getItem('access_token');
            if (!token) {
                console.error("No access token found");
                return;
            }

            // Close existing socket if any
            if (socket) {
                socket.close();
            }

            const wsUrl = `ws://localhost:5001/ws/live/${batchId}/${user.id}?token=${token}`;
            console.log(`Connecting to WebSocket: ${wsUrl}`);
            socket = new WebSocket(wsUrl);

            socket.onopen = () => {
                console.log("Connected to Live Class");
                setStatus('WAITING');
                retryCount = 0;
            };

            socket.onmessage = (event) => {
                try {
                    const msg = JSON.parse(event.data);
                    console.log("Received WS message:", msg);
                    handleMessage(msg);
                } catch (e) {
                    console.error("Error parsing WS message:", e);
                }
            };

            socket.onerror = (e) => {
                console.error("WS Error:", e);
            };

            socket.onclose = (e) => {
                console.log("WS Closed:", e.code, e.reason);
                if (!e.wasClean && retryCount < MAX_RETRIES) {
                    retryCount++;
                    console.log(`Reconnecting attempt ${retryCount}...`);
                    setTimeout(connect, 2000);
                }
            };

            setWs(socket);
        };

        connect();

        return () => {
            console.log("Cleaning up WebSocket connection");
            if (socket) {
                // Remove listeners to prevent logic from running during close
                socket.onopen = null;
                socket.onmessage = null;
                socket.onerror = null;
                socket.onclose = null;
                socket.close();
            }
        };
    }, [user, batchId]);

    const handleMessage = (msg: any) => {
        switch (msg.type) {
            case 'PUSH_QUIZ':
                setStatus('QUIZ')
                setPayload(msg.payload)
                setAnswerSubmitted(false)
                setSelectedOption(null)
                success("Quiz Started!", "Teacher has started a quiz")
                break
            case 'PUSH_POLL':
                setStatus('POLL')
                setPayload(msg.payload)
                setAnswerSubmitted(false)
                setSelectedOption(null)
                break
            case 'PUSH_MATERIAL':
                setStatus('MATERIAL')
                setPayload(msg.payload)
                break
            default:
                break
        }
    }

    const submitAnswer = (optionIndex: number, optionLabel: string) => {
        if (!ws || answerSubmitted) return

        ws.send(JSON.stringify({
            type: status === 'QUIZ' ? 'SUBMIT_ANSWER' : 'SUBMIT_POLL',
            payload: {
                questionId: 'current', // In real app, payload would have ID
                answer: optionLabel
            }
        }))

        setSelectedOption(optionIndex)
        setAnswerSubmitted(true)
        success("Submitted", "Your answer has been recorded")
    }

    if (!user) return <div className="p-8 text-white">Loading...</div>

    return (
        <div className="min-h-screen bg-black text-white flex flex-col items-center justify-center p-4 relative overflow-hidden">
            <div className="absolute inset-0 z-0 opacity-30">
                <AnimatedBackground />
            </div>

            <div className="z-10 w-full max-w-md">
                <div className="text-center mb-8">
                    <span className="inline-block px-3 py-1 rounded-full bg-red-500/20 text-red-400 text-xs font-bold tracking-widest border border-red-500/30 animate-pulse">
                        🔴 LIVE
                    </span>
                    <h1 className="text-2xl font-bold mt-2">{status === 'WAITING' ? "Waiting for Teacher..." : "Live Session"}</h1>
                </div>

                <AnimatePresence mode="wait">
                    {status === 'WAITING' && (
                        <motion.div
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.9 }}
                            className="bg-white/10 backdrop-blur-md rounded-2xl p-8 text-center border border-white/10"
                        >
                            <div className="w-20 h-20 mx-auto bg-blue-500/20 rounded-full flex items-center justify-center mb-6">
                                <svg className="w-10 h-10 text-blue-400 animate-bounce" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                                </svg>
                            </div>
                            <h3 className="text-xl font-bold mb-2">You're In!</h3>
                            <p className="text-gray-400">Sit tight. The class activity will appear here automatically.</p>
                        </motion.div>
                    )}

                    {(status === 'QUIZ' || status === 'POLL') && payload && (
                        <motion.div
                            key="interaction"
                            initial={{ y: 50, opacity: 0 }}
                            animate={{ y: 0, opacity: 1 }}
                            className="bg-gray-900 border border-gray-800 rounded-3xl p-6 shadow-2xl"
                        >
                            <span className="text-xs font-bold text-gray-500 uppercase tracking-widest block mb-4">{status}</span>
                            <h2 className="text-xl font-bold text-white mb-6 leading-relaxed">{payload.text}</h2>

                            <div className="space-y-3">
                                {payload.options && payload.options.map((opt: string, idx: number) => (
                                    <button
                                        key={idx}
                                        disabled={answerSubmitted}
                                        onClick={() => submitAnswer(idx, opt)}
                                        className={`w-full p-4 rounded-xl text-left transition-all duration-200 flex items-center justify-between border-2
                                                ${selectedOption === idx
                                                ? 'bg-blue-600 border-blue-500 text-white shadow-lg shadow-blue-500/30 scale-[1.02]'
                                                : 'bg-gray-800 border-transparent text-gray-300 hover:bg-gray-700'
                                            }
                                                ${answerSubmitted && selectedOption !== idx ? 'opacity-50' : ''}
                                            `}
                                    >
                                        <span className="font-medium text-lg">{opt}</span>
                                        {selectedOption === idx && (
                                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                                        )}
                                    </button>
                                ))}
                            </div>

                            {answerSubmitted && (
                                <div className="mt-6 text-center text-green-400 text-sm font-medium animate-pulse">
                                    Answer Submitted! Waiting for results...
                                </div>
                            )}
                        </motion.div>
                    )}
                </AnimatePresence>

                <div className="mt-8 flex justify-center">
                    <button
                        onClick={() => ws?.send(JSON.stringify({ type: 'RAISE_HAND' }))}
                        className="flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 rounded-full text-sm font-medium transition-colors"
                    >
                        <span>✋</span> Raise Hand
                    </button>
                </div>
            </div>
        </div>
    )
}

export default StudentLiveRoom
