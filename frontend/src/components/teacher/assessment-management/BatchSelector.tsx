/**
 * BatchSelector Component
 * Handles batch selection for assessment assignment
 */
import React, { useState } from "react"
import { motion } from "framer-motion"
import Card from "../../ui/Card"
import Button from "../../ui/Button"
import Input from "../../ui/Input"
import { ANIMATION_VARIANTS } from "../../../utils/constants"

interface Batch {
  id: string
  name: string
  studentCount: number
  createdAt: string
}

interface BatchSelectorProps {
  batches: Batch[]
  selectedBatches: string[]
  onBatchSelectionChange: (batchIds: string[]) => void
  searchTerm: string
  onSearchChange: (term: string) => void
  onConfirm: () => void
  onCancel: () => void
  isOpen: boolean
}

const BatchSelector: React.FC<BatchSelectorProps> = ({
  batches,
  selectedBatches,
  onBatchSelectionChange,
  searchTerm,
  onSearchChange,
  onConfirm,
  onCancel,
  isOpen
}) => {
  const [localSelectedBatches, setLocalSelectedBatches] = useState<string[]>(selectedBatches)

  const filteredBatches = batches.filter(batch =>
    batch.name.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const handleBatchToggle = (batchId: string) => {
    setLocalSelectedBatches(prev =>
      prev.includes(batchId)
        ? prev.filter(id => id !== batchId)
        : [...prev, batchId]
    )
  }

  const handleSelectAll = () => {
    if (localSelectedBatches.length === filteredBatches.length) {
      setLocalSelectedBatches([])
    } else {
      setLocalSelectedBatches(filteredBatches.map(batch => batch.id))
    }
  }

  const handleConfirm = () => {
    onBatchSelectionChange(localSelectedBatches)
    onConfirm()
  }

  const handleCancel = () => {
    setLocalSelectedBatches(selectedBatches)
    onCancel()
  }

  if (!isOpen) return null

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        className="bg-blue-900/95 backdrop-blur-sm border border-blue-500/30 rounded-lg max-w-2xl w-full max-h-[80vh] overflow-y-auto"
      >
        <Card className="p-6">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-blue-200">Select Batches</h2>
            <Button variant="ghost" onClick={handleCancel} className="text-blue-300 hover:text-blue-200">
              ✕
            </Button>
          </div>

          {/* Search */}
          <div className="mb-4">
            <Input
              type="text"
              placeholder="Search batches..."
              value={searchTerm}
              onChange={(e) => onSearchChange(e.target.value)}
              className="w-full"
            />
          </div>

          {/* Select All */}
          <div className="mb-4">
            <Button
              variant="ghost"
              onClick={handleSelectAll}
              className="text-blue-300 hover:text-blue-200"
            >
              {localSelectedBatches.length === filteredBatches.length ? "Deselect All" : "Select All"}
            </Button>
            <span className="text-blue-300 text-sm ml-2">
              ({localSelectedBatches.length} selected)
            </span>
          </div>

          {/* Batch List */}
          <div className="max-h-96 overflow-y-auto space-y-2 mb-6">
            {filteredBatches.map((batch) => (
              <div
                key={batch.id}
                className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                  localSelectedBatches.includes(batch.id)
                    ? "bg-blue-500/20 border-blue-400/50"
                    : "bg-blue-900/20 border-blue-500/30 hover:border-blue-400/50"
                }`}
                onClick={() => handleBatchToggle(batch.id)}
              >
                <div className="flex items-center space-x-3">
                  <input
                    type="checkbox"
                    checked={localSelectedBatches.includes(batch.id)}
                    onChange={() => handleBatchToggle(batch.id)}
                    className="w-4 h-4 text-blue-500 bg-blue-900 border-blue-500 rounded focus:ring-blue-500"
                  />
                  <div className="flex-1">
                    <h4 className="text-blue-200 font-medium">{batch.name}</h4>
                    <p className="text-blue-300 text-sm">
                      {batch.studentCount} students • Created {new Date(batch.createdAt).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Selection Summary */}
          {localSelectedBatches.length > 0 && (
            <div className="mb-6 p-4 bg-blue-800/20 rounded-lg border border-blue-500/30">
              <h4 className="text-blue-200 font-medium mb-2">Selection Summary</h4>
              <p className="text-blue-300 text-sm">
                Selected {localSelectedBatches.length} batch{localSelectedBatches.length !== 1 ? 'es' : ''} with{" "}
                {localSelectedBatches.reduce((sum, batchId) => {
                  const batch = batches.find(b => b.id === batchId)
                  return sum + (batch?.studentCount || 0)
                }, 0)} total students
              </p>
            </div>
          )}

          {/* Actions */}
          <div className="flex justify-end space-x-3">
            <Button variant="ghost" onClick={handleCancel}>
              Cancel
            </Button>
            <Button
              variant="primary"
              onClick={handleConfirm}
              disabled={localSelectedBatches.length === 0}
            >
              Confirm Selection
            </Button>
          </div>
        </Card>
      </motion.div>
    </motion.div>
  )
}

export default BatchSelector
