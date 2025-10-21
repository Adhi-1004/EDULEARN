import React from "react"
import { motion, AnimatePresence } from "framer-motion"
import Button from "./Button"
import { AlertTriangle, X } from "lucide-react"

interface ConfirmDialogProps {
  isOpen: boolean
  onClose: () => void
  onConfirm: () => void
  title: string
  message: string
  confirmText?: string
  cancelText?: string
  variant?: "danger" | "warning" | "info"
  loading?: boolean
}

const ConfirmDialog: React.FC<ConfirmDialogProps> = ({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  confirmText = "Confirm",
  cancelText = "Cancel",
  variant = "danger",
  loading = false
}) => {
  const variantStyles = {
    danger: {
      icon: "text-red-500",
      bg: "bg-red-500/10",
      border: "border-red-500/30",
      button: "bg-red-600 hover:bg-red-700"
    },
    warning: {
      icon: "text-yellow-500",
      bg: "bg-yellow-500/10",
      border: "border-yellow-500/30",
      button: "bg-yellow-600 hover:bg-yellow-700"
    },
    info: {
      icon: "text-blue-500",
      bg: "bg-blue-500/10",
      border: "border-blue-500/30",
      button: "bg-blue-600 hover:bg-blue-700"
    }
  }

  const style = variantStyles[variant]

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-[9999] p-4"
          onClick={onClose}
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            className="bg-card border border-border rounded-lg p-6 max-w-md w-full shadow-xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-start gap-4">
              <div className={`p-3 rounded-full ${style.bg} ${style.border} border`}>
                <AlertTriangle className={`h-6 w-6 ${style.icon}`} />
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-foreground mb-2">{title}</h3>
                <p className="text-muted-foreground text-sm mb-6">{message}</p>
                <div className="flex gap-3 justify-end">
                  <Button
                    variant="ghost"
                    onClick={onClose}
                    disabled={loading}
                  >
                    {cancelText}
                  </Button>
                  <Button
                    onClick={onConfirm}
                    disabled={loading}
                    className={style.button}
                  >
                    {loading ? "Processing..." : confirmText}
                  </Button>
                </div>
              </div>
              <button
                onClick={onClose}
                disabled={loading}
                className="text-muted-foreground hover:text-foreground transition-colors"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}

export default ConfirmDialog

