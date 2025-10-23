/**
 * Utility functions for handling API errors consistently
 */

export interface ApiError {
  response?: {
    data?: {
      detail?: string | Array<{ msg?: string; message?: string; [key: string]: any }>;
      message?: string;
    };
  };
  message?: string;
}

/**
 * Extracts a user-friendly error message from an API error response
 * @param error - The error object from an API call
 * @param fallback - Fallback message if no error details found
 * @returns A string error message suitable for display to users
 */
export function getErrorMessage(error: ApiError, fallback: string = "An error occurred"): string {
  if (!error?.response?.data) {
    return error?.message || fallback;
  }

  const errorData = error.response.data;
  
  // Handle Pydantic validation errors (array of error objects)
  if (Array.isArray(errorData.detail)) {
    return errorData.detail
      .map((e: any) => {
        if (typeof e === 'string') return e;
        if (e.msg) return e.msg;
        if (e.message) return e.message;
        return JSON.stringify(e);
      })
      .join(", ");
  }
  
  // Handle single detail string
  if (typeof errorData.detail === 'string') {
    return errorData.detail;
  }
  
  // Handle message field
  if (errorData.message) {
    return errorData.message;
  }
  
  return fallback;
}

/**
 * Safely extracts error details for logging
 * @param error - The error object
 * @returns A string representation of the error for logging
 */
export function getErrorDetails(error: ApiError): string {
  try {
    return JSON.stringify({
      message: error?.message,
      response: error?.response?.data,
      status: error?.response?.status,
      statusText: error?.response?.statusText
    });
  } catch {
    return String(error);
  }
}
