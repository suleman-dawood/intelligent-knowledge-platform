'use client'

import { useState, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  XMarkIcon,
  CloudArrowUpIcon,
  DocumentTextIcon,
  PhotoIcon,
  FilmIcon,
  MusicalNoteIcon,
  ArchiveBoxIcon,
  CheckCircleIcon,
  ExclamationCircleIcon
} from '@heroicons/react/24/outline'

interface UploadModalProps {
  isOpen: boolean
  onClose: () => void
  onUpload: (files: File[], displayNames: string[]) => Promise<void>
  title?: string
  description?: string
  acceptedTypes?: string[]
  maxFiles?: number
  maxSize?: number // in MB
}

interface FileWithMetadata {
  file: File
  displayName: string
  status: 'pending' | 'uploading' | 'success' | 'error'
  progress: number
  error?: string
}

export default function UploadModal({
  isOpen,
  onClose,
  onUpload,
  title = 'Upload Files',
  description = 'Add documents to your knowledge base',
  acceptedTypes = ['.pdf', '.docx', '.xlsx', '.txt', '.csv', '.png', '.jpg', '.jpeg'],
  maxFiles = 10,
  maxSize = 50 // 50MB default
}: UploadModalProps) {
  const [files, setFiles] = useState<FileWithMetadata[]>([])
  const [isDragOver, setIsDragOver] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const getFileIcon = (fileName: string) => {
    const extension = fileName.split('.').pop()?.toLowerCase()
    switch (extension) {
      case 'pdf':
      case 'doc':
      case 'docx':
      case 'txt':
        return <DocumentTextIcon className="h-6 w-6" />
      case 'jpg':
      case 'jpeg':
      case 'png':
      case 'gif':
        return <PhotoIcon className="h-6 w-6" />
      case 'mp4':
      case 'avi':
      case 'mov':
        return <FilmIcon className="h-6 w-6" />
      case 'mp3':
      case 'wav':
        return <MusicalNoteIcon className="h-6 w-6" />
      default:
        return <ArchiveBoxIcon className="h-6 w-6" />
    }
  }

  const validateFile = (file: File): string | null => {
    if (file.size > maxSize * 1024 * 1024) {
      return `File size exceeds ${maxSize}MB limit`
    }
    
    const extension = '.' + file.name.split('.').pop()?.toLowerCase()
    if (!acceptedTypes.includes(extension)) {
      return `File type ${extension} not supported`
    }
    
    return null
  }

  const handleFileSelect = (selectedFiles: FileList | null) => {
    if (!selectedFiles) return

    const newFiles: FileWithMetadata[] = []
    
    for (let i = 0; i < selectedFiles.length; i++) {
      const file = selectedFiles[i]
      
      if (files.length + newFiles.length >= maxFiles) {
        alert(`Maximum ${maxFiles} files allowed`)
        break
      }

      const error = validateFile(file)
      
      newFiles.push({
        file,
        displayName: file.name.replace(/\.[^/.]+$/, ''), // Remove extension for display name
        status: error ? 'error' : 'pending',
        progress: 0,
        error: error || undefined
      })
    }

    setFiles(prev => [...prev, ...newFiles])
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
    handleFileSelect(e.dataTransfer.files)
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
  }

  const updateDisplayName = (index: number, newName: string) => {
    setFiles(prev => prev.map((file, i) => 
      i === index ? { ...file, displayName: newName } : file
    ))
  }

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index))
  }

  const handleUpload = async () => {
    const validFiles = files.filter(f => f.status !== 'error')
    if (validFiles.length === 0) return

    setIsUploading(true)

    try {
      // Update status to uploading
      setFiles(prev => prev.map(f => 
        f.status !== 'error' ? { ...f, status: 'uploading' as const } : f
      ))

      // Simulate upload progress
      for (let progress = 0; progress <= 100; progress += 10) {
        await new Promise(resolve => setTimeout(resolve, 100))
        setFiles(prev => prev.map(f => 
          f.status === 'uploading' ? { ...f, progress } : f
        ))
      }

      // Call the upload function
      await onUpload(
        validFiles.map(f => f.file),
        validFiles.map(f => f.displayName)
      )

      // Mark as success
      setFiles(prev => prev.map(f => 
        f.status === 'uploading' ? { ...f, status: 'success' as const } : f
      ))

      // Close modal after a brief delay
      setTimeout(() => {
        onClose()
        setFiles([])
      }, 1500)

    } catch (error) {
      setFiles(prev => prev.map(f => 
        f.status === 'uploading' ? { 
          ...f, 
          status: 'error' as const, 
          error: 'Upload failed' 
        } : f
      ))
    } finally {
      setIsUploading(false)
    }
  }

  const handleClose = () => {
    if (!isUploading) {
      onClose()
      setFiles([])
    }
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
          onClick={handleClose}
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
                  <p className="text-sm text-gray-600 mt-1">{description}</p>
                </div>
                <button
                  onClick={handleClose}
                  disabled={isUploading}
                  className="p-2 text-gray-600 hover:text-gray-900 rounded-lg hover:bg-gray-100 transition-colors disabled:opacity-50"
                >
                  <XMarkIcon className="h-5 w-5" />
                </button>
              </div>
            </div>

            {/* Content */}
            <div className="p-6 overflow-y-auto max-h-[60vh]">
              {/* Drop Zone */}
              <div
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors ${
                  isDragOver
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-300 hover:border-gray-400'
                }`}
              >
                <CloudArrowUpIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-lg font-medium text-gray-900 mb-2">
                  Drag and drop files here
                </p>
                <p className="text-sm text-gray-600 mb-4">
                  or click to browse files
                </p>
                <button
                  onClick={() => fileInputRef.current?.click()}
                  disabled={isUploading}
                  className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50"
                >
                  Choose Files
                </button>
                <input
                  ref={fileInputRef}
                  type="file"
                  multiple
                  accept={acceptedTypes.join(',')}
                  onChange={(e) => handleFileSelect(e.target.files)}
                  className="hidden"
                />
                <p className="text-xs text-gray-500 mt-4">
                  Supported: {acceptedTypes.join(', ')} • Max {maxSize}MB per file • Up to {maxFiles} files
                </p>
              </div>

              {/* File List */}
              {files.length > 0 && (
                <div className="mt-6">
                  <h4 className="text-sm font-medium text-gray-900 mb-4">
                    Selected Files ({files.length})
                  </h4>
                  <div className="space-y-3">
                    {files.map((fileItem, index) => (
                      <div
                        key={index}
                        className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg"
                      >
                        {/* File Icon */}
                        <div className="text-gray-600">
                          {getFileIcon(fileItem.file.name)}
                        </div>

                        {/* File Info */}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center space-x-2 mb-1">
                            <input
                              type="text"
                              value={fileItem.displayName}
                              onChange={(e) => updateDisplayName(index, e.target.value)}
                              disabled={isUploading}
                              className="flex-1 text-sm font-medium text-gray-900 bg-transparent border-none focus:outline-none focus:ring-2 focus:ring-primary-500 rounded px-1 disabled:opacity-50"
                              placeholder="Display name"
                            />
                            <span className="text-xs text-gray-500">
                              {fileItem.file.name.split('.').pop()?.toUpperCase()}
                            </span>
                          </div>
                          <div className="text-xs text-gray-500">
                            {(fileItem.file.size / 1024 / 1024).toFixed(2)} MB
                          </div>

                          {/* Progress Bar */}
                          {fileItem.status === 'uploading' && (
                            <div className="mt-2">
                              <div className="w-full bg-gray-200 rounded-full h-1.5">
                                <div
                                  className="bg-primary-600 h-1.5 rounded-full transition-all duration-300"
                                  style={{ width: `${fileItem.progress}%` }}
                                />
                              </div>
                            </div>
                          )}

                          {/* Error Message */}
                          {fileItem.error && (
                            <div className="text-xs text-red-600 mt-1">
                              {fileItem.error}
                            </div>
                          )}
                        </div>

                        {/* Status Icon */}
                        <div className="flex-shrink-0">
                          {fileItem.status === 'success' && (
                            <CheckCircleIcon className="h-5 w-5 text-green-500" />
                          )}
                          {fileItem.status === 'error' && (
                            <ExclamationCircleIcon className="h-5 w-5 text-red-500" />
                          )}
                          {fileItem.status === 'pending' && !isUploading && (
                            <button
                              onClick={() => removeFile(index)}
                              className="p-1 text-gray-400 hover:text-gray-600 rounded"
                            >
                              <XMarkIcon className="h-4 w-4" />
                            </button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="p-6 border-t border-gray-200">
              <div className="flex items-center justify-between">
                <div className="text-sm text-gray-600">
                  {files.filter(f => f.status !== 'error').length} files ready to upload
                </div>
                <div className="flex space-x-3">
                  <button
                    onClick={handleClose}
                    disabled={isUploading}
                    className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleUpload}
                    disabled={files.filter(f => f.status !== 'error').length === 0 || isUploading}
                    className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50"
                  >
                    {isUploading ? 'Uploading...' : 'Upload Files'}
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
} 