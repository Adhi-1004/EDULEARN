import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Upload, BookOpen, FileText, CheckCircle } from 'lucide-react'
import Button from '../ui/Button'
import api from '../../utils/api'
import { useToast } from '../../contexts/ToastContext'

interface CreateScheduleModalProps {
    isOpen: boolean
    onClose: () => void
    onSuccess: () => void
    batches: { id: string; name: string }[]
}

const CreateScheduleModal: React.FC<CreateScheduleModalProps> = ({ isOpen, onClose, onSuccess, batches }) => {
    // const { user } = useAuth() // user unused
    const { success, error: showError } = useToast()
    const [loading, setLoading] = useState(false)
    const [step, setStep] = useState(1) // 1: Subject/Files, 2: Pattern

    const SUBJECTS = ["C", "C++", "Java", "Python", "ML", "OODP", "DSA", "DAA", "DBMS", "Networks"]

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

    // Reset when opening
    useEffect(() => {
        if (isOpen) {
            setStep(1)
            if (batches.length > 0 && !formData.batch_id) {
                setFormData(prev => ({ ...prev, batch_id: batches[0].id }))
            }
        }
    }, [isOpen, batches])

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
            onSuccess()
            onClose()

            // Reset
            setFiles({ handout: null, syllabus: null })
            setStep(1)

        } catch (err: any) {
            console.error("Generate schedule error", err)
            showError("Error", err.response?.data?.detail || "Failed to generate schedule")
        } finally {
            setLoading(false)
        }
    }

    const validBatches = batches.filter(b => b.id !== 'all')
    const DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50"
                    />
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: 20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: 20 }}
                        className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-lg bg-card border border-border rounded-xl shadow-2xl z-50 p-0 overflow-hidden"
                    >
                        <div className="bg-primary/5 p-6 border-b border-border">
                            <div className="flex justify-between items-center">
                                <div>
                                    <h2 className="text-xl font-bold text-foreground">Create Course Schedule</h2>
                                    <p className="text-sm text-muted-foreground mt-1">AI-powered schedule generation from handout</p>
                                </div>
                                <button onClick={onClose} className="text-muted-foreground hover:text-foreground">
                                    <X size={24} />
                                </button>
                            </div>
                        </div>

                        <form onSubmit={handleSubmit} className="p-6">
                            {/* Step Indicator */}
                            <div className="flex items-center mb-6">
                                <div className={`flex items-center justify-center w-8 h-8 rounded-full ${step >= 1 ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground'} font-bold text-sm`}>1</div>
                                <div className={`flex-1 h-1 mx-2 ${step >= 2 ? 'bg-primary' : 'bg-muted'}`} />
                                <div className={`flex items-center justify-center w-8 h-8 rounded-full ${step >= 2 ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground'} font-bold text-sm`}>2</div>
                            </div>

                            {step === 1 ? (
                                <div className="space-y-4">
                                    {/* Batch Selection */}
                                    <div>
                                        <label className="block text-sm font-medium text-foreground mb-1">Select Batch</label>
                                        <select
                                            name="batch_id"
                                            value={formData.batch_id}
                                            onChange={handleChange}
                                            className="w-full px-3 py-2 bg-muted/50 border border-border rounded-lg"
                                            required
                                        >
                                            <option value="" disabled>Select a batch</option>
                                            {validBatches.map(batch => (
                                                <option key={batch.id} value={batch.id}>{batch.name}</option>
                                            ))}
                                        </select>
                                    </div>

                                    {/* Subject Selection */}
                                    <div>
                                        <label className="block text-sm font-medium text-foreground mb-1">Subject</label>
                                        <select
                                            name="subject"
                                            value={formData.subject}
                                            onChange={handleChange}
                                            className="w-full px-3 py-2 bg-muted/50 border border-border rounded-lg mb-2"
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
                                                className="w-full px-3 py-2 bg-muted/50 border border-border rounded-lg"
                                            />
                                        )}
                                    </div>

                                    {/* Files */}
                                    <div className="grid grid-cols-2 gap-4">
                                        <div className="border-2 border-dashed border-border rounded-lg p-4 text-center hover:bg-muted/30 transition-colors">
                                            <input
                                                type="file"
                                                id="syllabus-upload"
                                                className="hidden"
                                                onChange={(e) => handleFileChange(e, 'syllabus')}
                                                accept=".pdf,.doc,.docx,.txt"
                                            />
                                            <label htmlFor="syllabus-upload" className="cursor-pointer block">
                                                <BookOpen className="w-8 h-8 mx-auto text-blue-500 mb-2" />
                                                <span className="text-sm font-medium block">Syllabus</span>
                                                <span className="text-xs text-muted-foreground">
                                                    {files.syllabus ? files.syllabus.name : "Optional"}
                                                </span>
                                            </label>
                                        </div>
                                        <div className={`border-2 border-dashed rounded-lg p-4 text-center transition-colors ${files.handout ? 'border-primary/50 bg-primary/5' : 'border-border hover:bg-muted/30'}`}>
                                            <input
                                                type="file"
                                                id="handout-upload"
                                                className="hidden"
                                                onChange={(e) => handleFileChange(e, 'handout')}
                                                accept=".pdf,.doc,.docx,.txt"
                                            />
                                            <label htmlFor="handout-upload" className="cursor-pointer block">
                                                <FileText className="w-8 h-8 mx-auto text-green-500 mb-2" />
                                                <span className="text-sm font-medium block">Course Handout *</span>
                                                <span className="text-xs text-muted-foreground">
                                                    {files.handout ? files.handout.name : "Required"}
                                                </span>
                                            </label>
                                        </div>
                                    </div>

                                    <div className="flex justify-end pt-4">
                                        <Button
                                            type="button"
                                            variant="primary"
                                            onClick={() => setStep(2)}
                                            disabled={!files.handout || !formData.subject || (!formData.subject && !formData.customSubject)}
                                        >
                                            Next: Schedule Pattern
                                        </Button>
                                    </div>
                                </div>
                            ) : (
                                <div className="space-y-4">
                                    <div className="grid grid-cols-2 gap-4">
                                        <div>
                                            <label className="block text-sm font-medium text-foreground mb-1">Start Date</label>
                                            <input
                                                type="date"
                                                name="start_date"
                                                value={formData.start_date}
                                                onChange={handleChange}
                                                className="w-full px-3 py-2 bg-muted/50 border border-border rounded-lg"
                                                required
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-foreground mb-1">Class Time</label>
                                            <input
                                                type="time"
                                                name="start_time"
                                                value={formData.start_time}
                                                onChange={handleChange}
                                                className="w-full px-3 py-2 bg-muted/50 border border-border rounded-lg"
                                                required
                                            />
                                        </div>
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium text-foreground mb-2">Class Days</label>
                                        <div className="flex flex-wrap gap-2">
                                            {DAYS.map(day => (
                                                <button
                                                    key={day}
                                                    type="button"
                                                    onClick={() => handleDayToggle(day)}
                                                    className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${formData.days_of_week.includes(day)
                                                        ? 'bg-primary text-primary-foreground'
                                                        : 'bg-muted text-muted-foreground hover:bg-muted/80'
                                                        }`}
                                                >
                                                    {day.slice(0, 3)}
                                                </button>
                                            ))}
                                        </div>
                                    </div>

                                    <div className="flex justify-between pt-6">
                                        <Button type="button" variant="ghost" onClick={() => setStep(1)} disabled={loading}>
                                            Back
                                        </Button>
                                        <Button type="submit" variant="primary" disabled={loading || formData.days_of_week.length === 0}>
                                            {loading ? (
                                                <span className="flex items-center">
                                                    <Upload className="w-4 h-4 mr-2 animate-spin" />
                                                    Generating...
                                                </span>
                                            ) : (
                                                <span className="flex items-center">
                                                    <CheckCircle className="w-4 h-4 mr-2" />
                                                    Generate Schedule
                                                </span>
                                            )}
                                        </Button>
                                    </div>
                                </div>
                            )}
                        </form>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    )
}

export default CreateScheduleModal
