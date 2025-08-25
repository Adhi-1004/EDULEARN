import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Webcam from 'react-webcam';
import { Camera, AlertTriangle } from 'lucide-react';
import { useCamera } from '../hooks/useCamera';

interface CameraMonitorProps {
  isActive: boolean;
  onViolation?: (type: string) => void;
}

export const CameraMonitor: React.FC<CameraMonitorProps> = ({
  isActive,
  onViolation
}) => {
  const { webcamRef, startCamera, stopCamera } = useCamera();
  const [violations, setViolations] = useState<string[]>([]);
  const [isMinimized, setIsMinimized] = useState(false);

  useEffect(() => {
    if (isActive) {
      startCamera();
      // Start monitoring for violations
      const interval = setInterval(() => {
        // Simulate violation detection
        const random = Math.random();
        if (random < 0.1) { // 10% chance of violation
          const violationType = random < 0.05 ? 'face_not_detected' : 'multiple_faces';
          setViolations(prev => [...prev, violationType]);
          onViolation?.(violationType);
        }
      }, 5000);

      return () => {
        clearInterval(interval);
        stopCamera();
      };
    }
  }, [isActive, startCamera, stopCamera, onViolation]);

  if (!isActive) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.8 }}
        className={`fixed ${isMinimized ? 'bottom-4 right-4' : 'top-4 right-4'} z-50`}
      >
        <div className={`bg-white rounded-lg shadow-2xl border-2 border-blue-500 overflow-hidden ${
          isMinimized ? 'w-32 h-24' : 'w-64 h-48'
        }`}>
          <div className="bg-blue-600 text-white px-3 py-2 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Camera className="h-4 w-4" />
              <span className="text-sm font-medium">Proctoring</span>
            </div>
            <button
              onClick={() => setIsMinimized(!isMinimized)}
              className="text-white hover:text-blue-200"
            >
              {isMinimized ? '□' : '−'}
            </button>
          </div>
          
          {!isMinimized && (
            <div className="relative">
              <Webcam
                ref={webcamRef}
                audio={false}
                screenshotFormat="image/jpeg"
                className="w-full h-40 object-cover"
              />
              
              {violations.length > 0 && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="absolute bottom-2 left-2 right-2 bg-red-500 text-white text-xs px-2 py-1 rounded flex items-center"
                >
                  <AlertTriangle className="h-3 w-3 mr-1" />
                  <span>Violation detected</span>
                </motion.div>
              )}
            </div>
          )}
        </div>
      </motion.div>
    </AnimatePresence>
  );
};
