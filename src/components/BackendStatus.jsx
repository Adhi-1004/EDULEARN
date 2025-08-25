"use client"

import { useBackend } from "../contexts/BackendContext"

const BackendStatus = () => {
  const { isOnline, isChecking, lastChecked, checkBackendStatus } = useBackend()

  const getStatusColor = () => {
    if (isChecking) return 'bg-yellow-500'
    return isOnline ? 'bg-green-500' : 'bg-red-500'
  }

  const getStatusText = () => {
    if (isChecking) return 'Checking...'
    return isOnline ? 'Online' : 'Offline'
  }

  const getStatusIcon = () => {
    if (isChecking) {
      return (
        <svg className="w-4 h-4 text-white animate-spin" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      )
    }
    
    if (isOnline) {
      return (
        <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
        </svg>
      )
    }
    
    return (
      <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
      </svg>
    )
  }

  return (
    <div className="flex items-center space-x-2">
      <div className="flex items-center space-x-1">
        <div className={`w-2 h-2 rounded-full ${getStatusColor()} animate-pulse`}></div>
        <span className="text-xs text-gray-600 hidden sm:inline">
          Backend: {getStatusText()}
        </span>
      </div>
      
      {/* Tooltip with more details */}
      <div className="relative group">
        <button 
          onClick={checkBackendStatus}
          className="p-1 rounded-full hover:bg-gray-100 transition-colors"
          title="Click to check connection status"
        >
          {getStatusIcon()}
        </button>
        
        {/* Tooltip */}
        <div className="absolute bottom-full right-0 mb-2 px-3 py-2 bg-gray-900 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap z-50">
          <div className="flex flex-col space-y-1">
            <div className="flex items-center space-x-2">
              <span>Status:</span>
              <span className={isOnline ? 'text-green-400' : 'text-red-400'}>
                {getStatusText()}
              </span>
            </div>
            {lastChecked && (
              <div className="text-gray-300">
                Last checked: {lastChecked.toLocaleTimeString()}
              </div>
            )}
            <div className="text-gray-300">
              Backend URL: localhost:5003
            </div>
          </div>
          {/* Arrow */}
          <div className="absolute top-full right-2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900"></div>
        </div>
      </div>
    </div>
  )
}

export default BackendStatus
