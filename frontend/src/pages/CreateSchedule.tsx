import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Upload, BookOpen, FileText, CheckCircle, ArrowLeft } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import Button from '../components/ui/Button'
import Card from '../components/ui/Card'
import api from '../utils/api'
import { useToast } from '../contexts/ToastContext'
import AnimatedBackground from '../components/AnimatedBackground'

const CreateSchedule: React.FC = () => {
    const navigate = useNavigate()
    const { success, error: showError } = useToast()
    const [loading, setLoading] = useState(false)
    const [step, setStep] = useState(1) // 1: Subject/Files, 2: Pattern
    const [batches, setBatches] = useState<{ id: string; name: string }[]>([])

    const SUBJECTS = ["C", "C++", "Java", "Python", "ML", "OODP", "DSA", "DAA", "DBMS", "Networks"]
    const DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    const [formData, setFormData] = useState({
        batch_id: '',
        subject: '',
        customSubject: '',
        start_date: new Date().toISOString().split('T')[0],
        start_time: '10:00',
        days_of_week: ['Monday', 'Wednesday', 'Friday'],
    })

    const [files, setFiles] = useState<{
        handout: File | null,
        syllabus: File | null
    }>({
        handout: null,
        syllabus: null
    })

    useEffect(() => {
        fetchBatches()
    }, [])

    const fetchBatches = async () => {
        try {
            const res = await api.get('/api/teacher/batches')
            // Backend returns { id: string, name: string, ... }
            const batchData = res.data.map((b: any) => ({ id: b.id, name: b.name }))
            setBatches(batchData)
            if (batchData.length > 0) {
                setFormData(prev => ({ ...prev, batch_id: batchData[0].id }))
            }
        } catch (err) {
            console.error(err)
            showError("Error", "Failed to fetch batches")
        }
    }

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        const { name, value } = e.target
        setFormData(prev => ({ ...prev, [name]: value }))
    }

    const handleDayToggle = (day: string) => {
        setFormData(prev => {
            const days = prev.days_of_week.includes(day)
                ? prev.days_of_week.filter(d => d !== day)
                : [...prev.days_of_week, day]
            return { ...prev, days_of_week: days }
        })
    }

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>, type: 'handout' | 'syllabus') => {
        if (e.target.files && e.target.files[0]) {
            setFiles(prev => ({ ...prev, [type]: e.target.files![0] }))
        }
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()

        if (!files.handout) {
            showError("Missing File", "Course Handout is required to generate the schedule.")
            return
        }

        const finalSubject = formData.subject === 'Other' ? formData.customSubject : formData.subject
        if (!finalSubject) {
            showError("Missing Subject", "Please select or enter a subject.")
            return
        }

        setLoading(true)

        try {
            const payload = new FormData()
            payload.append('handout_file', files.handout)
            if (files.syllabus) {
                payload.append('syllabus_file', files.syllabus)
            }
            payload.append('subject', finalSubject)
            payload.append('batch_id', formData.batch_id)
            payload.append('start_date', formData.start_date)
            payload.append('start_time', formData.start_time)
            payload.append('days_of_week', formData.days_of_week.join(','))

            const response = await api.post('/api/schedule/generate-from-handout', payload, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            })

            success("Schedule Created", response.data.message)
            navigate('/teacher-dashboard')

        } catch (err: any) {
            console.error("Generate schedule error", err)
            showError("Error", err.response?.data?.detail || "Failed to generate schedule")
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="min-h-screen pt-20 px-4 relative z-10">
            <AnimatedBackground />
            <div className="max-w-3xl mx-auto">
                <Button variant="ghost" onClick={() => navigate('/teacher-dashboard')} className="mb-6 flex items-center">
                    <ArrowLeft className="mr-2" /> Back to Dashboard
                </Button>

                <Card className="p-8">
                    <div className="mb-8 border-b border-border pb-6">
                        <h1 className="text-3xl font-bold text-foreground">Create Course Schedule</h1>
                        <p className="text-muted-foreground mt-2">AI-powered schedule generation from course handout</p>
                    </div>

                    <form onSubmit={handleSubmit}>
                        {/* Step Indicator */}
                        <div className="flex items-center mb-8">
                            <div className={`flex items-center justify-center w-10 h-10 rounded-full ${step >= 1 ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground'} font-bold text-lg transition-colors`}>1</div>
                            <div className={`flex-1 h-1 mx-4 ${step >= 2 ? 'bg-primary' : 'bg-muted'} transition-colors`} />
                            <div className={`flex items-center justify-center w-10 h-10 rounded-full ${step >= 2 ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground'} font-bold text-lg transition-colors`}>2</div>
                        </div>

                        {step === 1 ? (
                            <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} className="space-y-6">
                                {/* Batch Selection */}
                                <div>
                                    <label className="block text-sm font-medium text-foreground mb-2">Select Batch</label>
                                    <select
                                        name="batch_id"
                                        value={formData.batch_id}
                                        onChange={handleChange}
                                        className="w-full px-4 py-3 bg-muted/50 border border-border rounded-lg focus:ring-2 focus:ring-primary/50 outline-none transition-all"
                                        required
                                    >
                                        <option value="" disabled>Select a batch</option>
                                        {batches.filter(b => b.id !== 'all').map(batch => (
                                            <option key={batch.id} value={batch.id}>{batch.name}</option>
                                        ))}
                                    </select>
                                </div>

                                {/* Subject Selection */}
                                <div>
                                    <label className="block text-sm font-medium text-foreground mb-2">Subject</label>
                                    <select
                                        name="subject"
                                        value={formData.subject}
                                        onChange={handleChange}
                                        className="w-full px-4 py-3 bg-muted/50 border border-border rounded-lg mb-3 focus:ring-2 focus:ring-primary/50 outline-none transition-all"
                                        required
                                    >
                                        <option value="" disabled>Select Subject</option>
                                        {SUBJECTS.map(sub => (
                                            <option key={sub} value={sub}>{sub}</option>
                                        ))}
                                        <option value="Other">Other</option>
                                    </select>
                                    {formData.subject === 'Other' && (
                                        <input
                                            type="text"
                                            name="customSubject"
                                            value={formData.customSubject}
                                            onChange={handleChange}
                                            placeholder="Enter subject name"
                                            className="w-full px-4 py-3 bg-muted/50 border border-border rounded-lg focus:ring-2 focus:ring-primary/50 outline-none transition-all"
                                        />
                                    )}
                                </div>

                                {/* Files */}
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    <div className="border-2 border-dashed border-border rounded-xl p-6 text-center hover:bg-muted/30 transition-colors cursor-pointer relative group">
                                        <input
                                            type="file"
                                            id="syllabus-upload"
                                            className="hidden"
                                            onChange={(e) => handleFileChange(e, 'syllabus')}
                                            accept=".pdf,.doc,.docx,.txt"
                                        />
                                        <label htmlFor="syllabus-upload" className="cursor-pointer block w-full h-full">
                                            <div className="w-12 h-12 rounded-full bg-blue-500/10 flex items-center justify-center mx-auto mb-3 group-hover:scale-110 transition-transform">
                                                <BookOpen className="w-6 h-6 text-blue-500" />
                                            </div>
                                            <span className="text-base font-medium block mb-1">Upload Syllabus</span>
                                            <span className="text-xs text-muted-foreground block">
                                                {files.syllabus ? files.syllabus.name : "Optional (PDF, Doc)"}
                                            </span>
                                        </label>
                                    </div>
                                    <div className={`border-2 border-dashed rounded-xl p-6 text-center transition-colors cursor-pointer relative group ${files.handout ? 'border-primary/50 bg-primary/5' : 'border-border hover:bg-muted/30'}`}>
                                        <input
                                            type="file"
                                            id="handout-upload"
                                            className="hidden"
                                            onChange={(e) => handleFileChange(e, 'handout')}
                                            accept=".pdf,.doc,.docx,.txt"
                                        />
                                        <label htmlFor="handout-upload" className="cursor-pointer block w-full h-full">
                                            <div className="w-12 h-12 rounded-full bg-green-500/10 flex items-center justify-center mx-auto mb-3 group-hover:scale-110 transition-transform">
                                                <FileText className="w-6 h-6 text-green-500" />
                                            </div>
                                            <span className="text-base font-medium block mb-1">Upload Handout *</span>
                                            <span className="text-xs text-muted-foreground block">
                                                {files.handout ? files.handout.name : "Required (PDF, Doc)"}
                                            </span>
                                        </label>
                                    </div>
                                </div>

                                <div className="flex justify-end pt-6">
                                    <Button
                                        type="button"
                                        variant="primary"
                                        onClick={() => setStep(2)}
                                        disabled={!files.handout || !formData.subject || (!formData.subject && !formData.customSubject)}
                                        className="w-full md:w-auto"
                                    >
                                        Next Step
                                    </Button>
                                </div>
                            </motion.div>
                        ) : (
                            <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="space-y-6">
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    <div>
                                        <label className="block text-sm font-medium text-foreground mb-2">Start Date</label>
                                        <input
                                            type="date"
                                            name="start_date"
                                            value={formData.start_date}
                                            onChange={handleChange}
                                            className="w-full px-4 py-3 bg-muted/50 border border-border rounded-lg focus:ring-2 focus:ring-primary/50 outline-none transition-all"
                                            required
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-foreground mb-2">Class Time</label>
                                        <input
                                            type="time"
                                            name="start_time"
                                            value={formData.start_time}
                                            onChange={handleChange}
                                            className="w-full px-4 py-3 bg-muted/50 border border-border rounded-lg focus:ring-2 focus:ring-primary/50 outline-none transition-all"
                                            required
                                        />
                                    </div>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-foreground mb-3">Class Days</label>
                                    <div className="flex flex-wrap gap-3">
                                        {DAYS.map(day => (
                                            <button
                                                key={day}
                                                type="button"
                                                onClick={() => handleDayToggle(day)}
                                                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${formData.days_of_week.includes(day)
                                                    ? 'bg-primary text-primary-foreground shadow-md scale-105'
                                                    : 'bg-muted text-muted-foreground hover:bg-muted/80'
                                                    }`}
                                            >
                                                {day.slice(0, 3)}
                                            </button>
                                        ))}
                                    </div>
                                </div>

                                <div className="flex justify-between pt-8 border-t border-border mt-8">
                                    <Button type="button" variant="ghost" onClick={() => setStep(1)} disabled={loading}>
                                        Back
                                    </Button>
                                    <Button type="submit" variant="primary" disabled={loading || formData.days_of_week.length === 0} className="px-8">
                                        {loading ? (
                                            <span className="flex items-center">
                                                <Upload className="w-4 h-4 mr-2 animate-spin" />
                                                Generating Schedule...
                                            </span>
                                        ) : (
                                            <span className="flex items-center">
                                                <CheckCircle className="w-4 h-4 mr-2" />
                                                Generate Schedule
                                            </span>
                                        )}
                                    </Button>
                                </div>
                            </motion.div>
                        )}
                    </form>
                </Card>
            </div>
        </div>
    )
}

export default CreateSchedule
