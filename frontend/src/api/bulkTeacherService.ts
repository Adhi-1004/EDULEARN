/**
 * Bulk Teacher Upload Service
 */
import api from '../utils/api'

export interface TeacherData {
  name: string
  email: string
  teacher_id: string
}

export interface BulkTeacherUploadResponse {
  success: boolean
  total_rows: number
  successful_imports: number
  failed_imports: number
  errors: Array<{ row: number; data?: any; errors?: string[]; error?: string; email?: string; teacher_id?: string }>
  created_teachers: Array<{ id: string; name: string; email: string; teacher_id: string; row: number }>
}

class BulkTeacherService {
  async upload(file: File): Promise<BulkTeacherUploadResponse> {
    const formData = new FormData()
    formData.append('file', file)
    const res = await api.post('/bulk-teachers/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' }, timeout: 60000 })
    return res.data
  }

  async validate(file: File) {
    const formData = new FormData()
    formData.append('file', file)
    const res = await api.post('/bulk-teachers/validate', formData, { headers: { 'Content-Type': 'multipart/form-data' }, timeout: 30000 })
    return res.data
  }

  async template() {
    const res = await api.get('/bulk-teachers/template')
    return res.data.template_data
  }

  async history() {
    const res = await api.get('/bulk-teachers/history')
    return res.data.uploads || []
  }

  createTemplateCsv(): void {
    const rows = [
      ['name', 'email', 'teacher_id'],
      ['Alice Johnson', 'alice@example.com', 'TCH1001'],
      ['Bob Smith', 'bob@example.com', 'TCH1002'],
    ]
    const csv = rows.map(r => r.join(',')).join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'teacher_template.csv'
    a.click()
    window.URL.revokeObjectURL(url)
  }
}

export const bulkTeacherService = new BulkTeacherService()
export default bulkTeacherService


