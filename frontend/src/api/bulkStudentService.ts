/**
 * Bulk Student Upload Service
 * Handles Excel file upload and bulk student creation
 */

import api from '../utils/api';

export interface StudentData {
  name: string;
  roll_number: string;
  email: string;
}

export interface BulkUploadResponse {
  success: boolean;
  total_rows: number;
  successful_imports: number;
  failed_imports: number;
  errors: Array<{
    row: number;
    data?: any;
    errors?: string[];
    error?: string;
    email?: string;
    roll_number?: string;
  }>;
  created_students: Array<{
    id: string;
    name: string;
    roll_number: string;
    email: string;
    row: number;
  }>;
  batch_id?: string;
}

export interface ValidationResponse {
  success: boolean;
  total_rows: number;
  valid_rows: number;
  invalid_rows: number;
  preview_data: StudentData[];
  errors: Array<{
    row: number;
    data: any;
    errors: string[];
  }>;
  message: string;
}

export interface UploadHistory {
  _id: string;
  batch_id: string;
  uploaded_by: string;
  uploaded_at: string;
  total_rows: number;
  successful_imports: number;
  failed_imports: number;
  file_name: string;
  created_students: Array<{
    id: string;
    name: string;
    roll_number: string;
    email: string;
    row: number;
  }>;
  errors: Array<{
    row: number;
    data?: any;
    errors?: string[];
    error?: string;
  }>;
}

class BulkStudentService {
  /**
   * Upload Excel file and create student accounts in bulk
   */
  async uploadStudents(
    file: File,
    batchId: string,
    sendWelcomeEmails: boolean = true
  ): Promise<BulkUploadResponse> {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('batch_id', batchId);
      formData.append('send_welcome_emails', sendWelcomeEmails.toString());

      const response = await api.post('/bulk-students/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 60000, // 60 seconds timeout for large files
      });

      return response.data;
    } catch (error: any) {
      console.error('Bulk upload error:', error);
      throw new Error(
        error.response?.data?.detail || 
        'Failed to upload students. Please check your file format and try again.'
      );
    }
  }

  /**
   * Validate Excel file without creating accounts
   */
  async validateFile(file: File): Promise<ValidationResponse> {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await api.post('/bulk-students/validate', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 30000, // 30 seconds timeout for validation
      });

      return response.data;
    } catch (error: any) {
      console.error('File validation error:', error);
      throw new Error(
        error.response?.data?.detail || 
        'Failed to validate file. Please check your file format.'
      );
    }
  }

  /**
   * Download Excel template
   */
  async downloadTemplate(): Promise<void> {
    try {
      const response = await api.get('/bulk-students/template');
      
      // Create template data
      const templateData = response.data.template_data;
      
      // Create CSV content
      const csvContent = [
        'name,roll_number,email',
        ...templateData.map((row: any) => 
          `${row.name},${row.roll_number},${row.email}`
        )
      ].join('\n');

      // Create and download file
      const blob = new Blob([csvContent], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'student_template.csv';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
    } catch (error: any) {
      console.error('Template download error:', error);
      throw new Error('Failed to download template');
    }
  }

  /**
   * Get upload history for a batch
   */
  async getUploadHistory(batchId: string): Promise<UploadHistory[]> {
    try {
      const response = await api.get(`/bulk-students/history/${batchId}`);
      return response.data.uploads || [];
    } catch (error: any) {
      console.error('Upload history error:', error);
      throw new Error('Failed to fetch upload history');
    }
  }

  /**
   * Create Excel template file for download
   */
  createTemplateFile(): void {
    const templateData = [
      ['name', 'roll_number', 'email'],
      ['John Doe', '2024001', 'john.doe@example.com'],
      ['Jane Smith', '2024002', 'jane.smith@example.com'],
      ['Mike Johnson', '2024003', 'mike.johnson@example.com']
    ];

    // Convert to CSV
    const csvContent = templateData.map(row => row.join(',')).join('\n');
    
    // Create and download file
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'student_template.csv';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  }

  /**
   * Validate file format
   */
  validateFileFormat(file: File): { valid: boolean; error?: string } {
    const allowedTypes = [
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', // .xlsx
      'application/vnd.ms-excel', // .xls
      'text/csv' // .csv
    ];

    const allowedExtensions = ['.xlsx', '.xls', '.csv'];
    const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));

    if (!allowedTypes.includes(file.type) && !allowedExtensions.includes(fileExtension)) {
      return {
        valid: false,
        error: 'Please upload an Excel file (.xlsx, .xls) or CSV file (.csv)'
      };
    }

    if (file.size > 10 * 1024 * 1024) { // 10MB limit
      return {
        valid: false,
        error: 'File size must be less than 10MB'
      };
    }

    return { valid: true };
  }

  /**
   * Format error messages for display
   */
  formatErrors(errors: BulkUploadResponse['errors']): string[] {
    return errors.map(error => {
      if (error.errors && error.errors.length > 0) {
        return `Row ${error.row}: ${error.errors.join(', ')}`;
      } else if (error.error) {
        return `Row ${error.row}: ${error.error}`;
      } else {
        return `Row ${error.row}: Unknown error`;
      }
    });
  }

  /**
   * Get success message
   */
  getSuccessMessage(response: BulkUploadResponse): string {
    const { successful_imports, total_rows, failed_imports } = response;
    
    if (successful_imports === total_rows) {
      return `✅ All ${successful_imports} students imported successfully!`;
    } else if (successful_imports > 0) {
      return `✅ ${successful_imports} students imported successfully. ${failed_imports} failed.`;
    } else {
      return `❌ No students were imported. Please check the errors and try again.`;
    }
  }
}

export const bulkStudentService = new BulkStudentService();
export default bulkStudentService;
