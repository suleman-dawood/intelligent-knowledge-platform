"use client"

import React, { useState, useRef, useCallback, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Upload, 
  X, 
  File, 
  CheckCircle, 
  AlertCircle, 
  Image, 
  FileText, 
  Video, 
  Music,
  Globe,
  Type,
  GraduationCap
} from 'lucide-react'

interface FileUpload {
  id: string
  file: File
  progress: number
  status: 'uploading' | 'success' | 'error'
  error?: string
  fileId?: string
  url?: string
}

interface FormData {
  title: string
  description: string
  contentType: string
  url: string
  content: string
  tags: string[]
}

interface FormErrors {
  title?: string
  description?: string
  contentType?: string
  url?: string
  content?: string
  files?: string
  tags?: string
}

interface AddContentModalProps {
  isOpen: boolean
  onClose: () => void
  onSubmit?: (data: any) => Promise<void>
}

const CONTENT_TYPES = [
  { value: 'text', label: 'Text/Article', icon: Type, description: 'Plain text or article content' },
  { value: 'pdf', label: 'PDF Document', icon: FileText, description: 'Upload PDF files' },
  { value: 'url', label: 'Web URL', icon: Globe, description: 'Scrape content from web pages' },
  { value: 'academic', label: 'Academic Paper', icon: GraduationCap, description: 'Research papers and publications' },
]

const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB
const MAX_FILES = 5

const getFileIcon = (fileType: string) => {
  if (fileType.startsWith('image/')) return Image
  if (fileType.startsWith('video/')) return Video
  if (fileType.startsWith('audio/')) return Music
  if (fileType === 'application/pdf' || fileType.startsWith('text/')) return FileText
  return File
}

const validateFile = (file: File): string | null => {
  if (file.size > MAX_FILE_SIZE) {
    return `File size must be less than ${MAX_FILE_SIZE / 1024 / 1024}MB`
  }
  
  if (file.type !== 'application/pdf') {
    return 'Only PDF files are supported'
  }
  
  return null
}

export default function AddContentModal({ isOpen, onClose, onSubmit }: AddContentModalProps) {
  const [files, setFiles] = useState<FileUpload[]>([])
  const [isDragOver, setIsDragOver] = useState(false)
  const [formData, setFormData] = useState<FormData>({
    title: '',
    description: '',
    contentType: 'text',
    url: '',
    content: '',
    tags: []
  })
  const [errors, setErrors] = useState<FormErrors>({})
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitStatus, setSubmitStatus] = useState<'idle' | 'success' | 'error'>('idle')
  const [tagInput, setTagInput] = useState('')
  
  const fileInputRef = useRef<HTMLInputElement>(null)
  const dropZoneRef = useRef<HTMLDivElement>(null)

  const validateForm = useCallback((): FormErrors => {
    const newErrors: FormErrors = {}
    
    if (!formData.title.trim()) {
      newErrors.title = 'Title is required'
    } else if (formData.title.length < 3) {
      newErrors.title = 'Title must be at least 3 characters'
    }
    
    if (formData.contentType === 'url') {
      if (!formData.url.trim()) {
        newErrors.url = 'URL is required'
      } else if (!/^https?:\/\/.+/.test(formData.url)) {
        newErrors.url = 'Please enter a valid URL'
      }
    } else if (formData.contentType === 'text' || formData.contentType === 'academic') {
      if (!formData.content.trim()) {
        newErrors.content = 'Content is required'
      } else if (formData.content.length < 10) {
        newErrors.content = 'Content must be at least 10 characters'
      }
    } else if (formData.contentType === 'pdf') {
      if (files.length === 0) {
        newErrors.files = 'Please upload a PDF file'
      }
    }
    
    return newErrors
  }, [formData, files])

  const uploadFile = useCallback(async (fileUpload: FileUpload) => {
    const { fileStorageService } = await import('../../lib/fileStorage')
    
    try {
      const result = await fileStorageService.uploadFile(
        fileUpload.file,
        (progress) => {
          setFiles(prev => prev.map(f => 
            f.id === fileUpload.id 
              ? { ...f, progress: progress.percentage }
              : f
          ))
        }
      )

      if (result.success) {
        setFiles(prev => prev.map(f => 
          f.id === fileUpload.id 
            ? { ...f, progress: 100, status: 'success' as const, fileId: result.fileId, url: result.url }
            : f
        ))
      } else {
        setFiles(prev => prev.map(f => 
          f.id === fileUpload.id 
            ? { ...f, status: 'error' as const, error: result.error }
            : f
        ))
      }
    } catch (error) {
      setFiles(prev => prev.map(f => 
        f.id === fileUpload.id 
          ? { ...f, status: 'error' as const, error: 'Upload failed' }
          : f
      ))
    }
  }, [])

  const handleFiles = useCallback((newFiles: FileList | File[]) => {
    const fileArray = Array.from(newFiles)
    
    if (files.length + fileArray.length > MAX_FILES) {
      setErrors(prev => ({ ...prev, files: `Maximum ${MAX_FILES} files allowed` }))
      return
    }

    const validFiles: FileUpload[] = []
    
    fileArray.forEach(file => {
      const error = validateFile(file)
      if (error) {
        setErrors(prev => ({ ...prev, files: error }))
        return
      }
      
      const fileUpload: FileUpload = {
        id: Math.random().toString(36).substr(2, 9),
        file,
        progress: 0,
        status: 'uploading'
      }
      
      validFiles.push(fileUpload)
    })

    if (validFiles.length > 0) {
      setFiles(prev => [...prev, ...validFiles])
      setErrors(prev => ({ ...prev, files: undefined }))
      
      validFiles.forEach(fileUpload => {
        uploadFile(fileUpload)
      })
    }
  }, [files.length, uploadFile])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
    
    const droppedFiles = e.dataTransfer.files
    handleFiles(droppedFiles)
  }, [handleFiles])

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    if (!dropZoneRef.current?.contains(e.relatedTarget as Node)) {
      setIsDragOver(false)
    }
  }, [])

  const removeFile = useCallback((fileId: string) => {
    setFiles(prev => prev.filter(f => f.id !== fileId))
  }, [])

  const handleInputChange = useCallback((field: keyof FormData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    if (errors[field as keyof FormErrors]) {
      setErrors(prev => ({ ...prev, [field as keyof FormErrors]: undefined }))
    }
  }, [errors])

  const handleTagAdd = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && tagInput.trim()) {
      e.preventDefault()
      const newTag = tagInput.trim().toLowerCase()
      if (!formData.tags.includes(newTag)) {
        setFormData(prev => ({ ...prev, tags: [...prev.tags, newTag] }))
      }
      setTagInput('')
    }
  }, [tagInput, formData.tags])

  const removeTag = useCallback((tagToRemove: string) => {
    setFormData(prev => ({ 
      ...prev, 
      tags: prev.tags.filter(tag => tag !== tagToRemove) 
    }))
  }, [])

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault()
    
    const formErrors = validateForm()
    if (Object.keys(formErrors).length > 0) {
      setErrors(formErrors)
      return
    }

    setIsSubmitting(true)
    setSubmitStatus('idle')

    try {
      // Prepare submission data
      const submissionData = {
        type: formData.contentType,
        title: formData.title,
        content: formData.content,
        url: formData.url,
        file: files[0]?.file || null,
        tags: formData.tags
      }

      if (onSubmit) {
        await onSubmit(submissionData)
      } else {
        // Default submission logic
        const formDataToSend = new FormData()
        formDataToSend.append('type', formData.contentType)
        formDataToSend.append('title', formData.title)
        formDataToSend.append('content', formData.content)
        formDataToSend.append('url', formData.url)
        
        if (files[0]?.file) {
          formDataToSend.append('file', files[0].file)
        }

        const response = await fetch('/api/content', {
          method: 'POST',
          body: formDataToSend,
        })

        if (!response.ok) {
          throw new Error('Failed to add content')
        }
      }

      setSubmitStatus('success')
      setTimeout(() => {
        onClose()
        // Reset form
        setFormData({
          title: '',
          description: '',
          contentType: 'text',
          url: '',
          content: '',
          tags: []
        })
        setFiles([])
        setSubmitStatus('idle')
      }, 1500)
    } catch (error) {
      setSubmitStatus('error')
      setErrors({ ...errors, content: error instanceof Error ? error.message : 'An error occurred' })
    } finally {
      setIsSubmitting(false)
    }
  }, [validateForm, onSubmit, onClose, formData, files, errors])

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && !isSubmitting) {
        onClose()
      }
    }

    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown)
      return () => document.removeEventListener('keydown', handleKeyDown)
    }
  }, [isOpen, isSubmitting, onClose])

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
      />
      
      <motion.div
        initial={{ opacity: 0, scale: 0.9, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.9, y: 20 }}
        className="relative bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden"
      >
        <AnimatePresence mode="wait">
          {submitStatus === 'success' ? (
            <motion.div
              key="success"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              className="flex flex-col items-center justify-center py-16 px-8"
            >
              <div className="bg-green-100 p-4 rounded-full mb-6">
                <CheckCircle className="w-12 h-12 text-green-600" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-3">Content Added Successfully!</h3>
              <p className="text-gray-600 text-center">Your content has been uploaded and is being processed.</p>
            </motion.div>
          ) : (
            <motion.div
              key="form"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="overflow-y-auto max-h-[90vh]"
            >
              {/* Header */}
              <div className="sticky top-0 bg-white border-b border-gray-200 px-8 py-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900">Add New Content</h2>
                    <p className="text-gray-600 mt-1">Share knowledge with the platform</p>
                  </div>
                  <button
                    onClick={onClose}
                    className="p-2 hover:bg-gray-100 rounded-full transition-colors"
                  >
                    <X className="w-5 h-5 text-gray-500" />
                  </button>
                </div>
              </div>

              <form onSubmit={handleSubmit} className="p-8 space-y-8">
                {/* Content Type Selection */}
                <div className="space-y-4">
                  <label className="block text-sm font-semibold text-gray-900">Content Type</label>
                  <div className="grid grid-cols-2 gap-3">
                    {CONTENT_TYPES.map((type) => {
                      const IconComponent = type.icon
                      return (
                        <motion.button
                          key={type.value}
                          type="button"
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                          onClick={() => handleInputChange('contentType', type.value)}
                          className={`p-4 rounded-xl border-2 text-left transition-all ${
                            formData.contentType === type.value
                              ? 'border-primary-500 bg-primary-50'
                              : 'border-gray-200 hover:border-gray-300'
                          }`}
                        >
                          <div className="flex items-center mb-2">
                            <IconComponent className={`w-5 h-5 mr-2 ${
                              formData.contentType === type.value ? 'text-primary-600' : 'text-gray-500'
                            }`} />
                            <span className={`font-medium ${
                              formData.contentType === type.value ? 'text-primary-900' : 'text-gray-900'
                            }`}>
                              {type.label}
                            </span>
                          </div>
                          <p className="text-xs text-gray-600">{type.description}</p>
                        </motion.button>
                      )
                    })}
                  </div>
                </div>

                {/* Title */}
                <div className="space-y-2">
                  <label htmlFor="title" className="block text-sm font-semibold text-gray-900">
                    Title <span className="text-red-500">*</span>
                  </label>
                  <input
                    id="title"
                    type="text"
                    value={formData.title}
                    onChange={(e) => handleInputChange('title', e.target.value)}
                    placeholder="Enter a descriptive title"
                    className={`w-full px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 transition-colors ${
                      errors.title 
                        ? 'border-red-300 focus:ring-red-500' 
                        : 'border-gray-300 focus:ring-primary-500'
                    }`}
                  />
                  {errors.title && (
                    <p className="text-sm text-red-600 flex items-center">
                      <AlertCircle className="w-4 h-4 mr-1" />
                      {errors.title}
                    </p>
                  )}
                </div>

                {/* Conditional Content Fields */}
                {formData.contentType === 'url' && (
                  <div className="space-y-2">
                    <label htmlFor="url" className="block text-sm font-semibold text-gray-900">
                      URL <span className="text-red-500">*</span>
                    </label>
                    <input
                      id="url"
                      type="url"
                      value={formData.url}
                      onChange={(e) => handleInputChange('url', e.target.value)}
                      placeholder="https://example.com/article"
                      className={`w-full px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 transition-colors ${
                        errors.url 
                          ? 'border-red-300 focus:ring-red-500' 
                          : 'border-gray-300 focus:ring-primary-500'
                      }`}
                    />
                    {errors.url && (
                      <p className="text-sm text-red-600 flex items-center">
                        <AlertCircle className="w-4 h-4 mr-1" />
                        {errors.url}
                      </p>
                    )}
                  </div>
                )}

                {formData.contentType === 'pdf' && (
                  <div className="space-y-4">
                    <label className="block text-sm font-semibold text-gray-900">
                      PDF File <span className="text-red-500">*</span>
                    </label>
                    <div
                      ref={dropZoneRef}
                      onDrop={handleDrop}
                      onDragOver={handleDragOver}
                      onDragLeave={handleDragLeave}
                      className={`relative border-2 border-dashed rounded-xl p-8 text-center transition-all duration-200 ${
                        isDragOver 
                          ? 'border-primary-500 bg-primary-50 scale-105' 
                          : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
                      } ${errors.files ? 'border-red-300' : ''}`}
                    >
                      <input
                        ref={fileInputRef}
                        type="file"
                        accept=".pdf"
                        onChange={(e) => e.target.files && handleFiles(e.target.files)}
                        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                      />
                      
                      <motion.div
                        animate={{ scale: isDragOver ? 1.1 : 1 }}
                        transition={{ duration: 0.2 }}
                      >
                        <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                        <h3 className="text-lg font-medium mb-2 text-gray-900">
                          {isDragOver ? 'Drop PDF here' : 'Upload PDF file'}
                        </h3>
                        <p className="text-sm text-gray-600 mb-4">
                          Drag and drop your PDF file here, or click to browse
                        </p>
                        <p className="text-xs text-gray-500">
                          Maximum file size: 10MB
                        </p>
                      </motion.div>
                    </div>

                    {errors.files && (
                      <p className="text-sm text-red-600 flex items-center">
                        <AlertCircle className="w-4 h-4 mr-1" />
                        {errors.files}
                      </p>
                    )}

                    {/* File List */}
                    <AnimatePresence>
                      {files.length > 0 && (
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: 'auto' }}
                          exit={{ opacity: 0, height: 0 }}
                          className="space-y-3"
                        >
                          {files.map((fileUpload) => {
                            const IconComponent = getFileIcon(fileUpload.file.type)
                            return (
                              <motion.div
                                key={fileUpload.id}
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: 20 }}
                                className="flex items-center gap-3 p-4 bg-gray-50 rounded-xl"
                              >
                                <IconComponent className="w-8 h-8 text-gray-500 flex-shrink-0" />
                                <div className="flex-1 min-w-0">
                                  <p className="text-sm font-medium truncate">{fileUpload.file.name}</p>
                                  <p className="text-xs text-gray-500">
                                    {(fileUpload.file.size / 1024 / 1024).toFixed(2)} MB
                                  </p>
                                  {fileUpload.status === 'uploading' && (
                                    <div className="mt-2">
                                      <div className="bg-gray-200 rounded-full h-1">
                                        <div 
                                          className="bg-primary-500 h-1 rounded-full transition-all duration-300"
                                          style={{ width: `${fileUpload.progress}%` }}
                                        />
                                      </div>
                                    </div>
                                  )}
                                </div>
                                <div className="flex items-center gap-2">
                                  {fileUpload.status === 'success' && (
                                    <CheckCircle className="w-5 h-5 text-green-500" />
                                  )}
                                  {fileUpload.status === 'error' && (
                                    <AlertCircle className="w-5 h-5 text-red-500" />
                                  )}
                                  <button
                                    type="button"
                                    onClick={() => removeFile(fileUpload.id)}
                                    className="p-1 hover:bg-gray-200 rounded-full transition-colors"
                                  >
                                    <X className="w-4 h-4 text-gray-500" />
                                  </button>
                                </div>
                              </motion.div>
                            )
                          })}
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                )}

                {(formData.contentType === 'text' || formData.contentType === 'academic') && (
                  <div className="space-y-2">
                    <label htmlFor="content" className="block text-sm font-semibold text-gray-900">
                      Content <span className="text-red-500">*</span>
                    </label>
                    <textarea
                      id="content"
                      value={formData.content}
                      onChange={(e) => handleInputChange('content', e.target.value)}
                      placeholder="Enter your content here..."
                      rows={6}
                      className={`w-full px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 transition-colors resize-none ${
                        errors.content 
                          ? 'border-red-300 focus:ring-red-500' 
                          : 'border-gray-300 focus:ring-primary-500'
                      }`}
                    />
                    {errors.content && (
                      <p className="text-sm text-red-600 flex items-center">
                        <AlertCircle className="w-4 h-4 mr-1" />
                        {errors.content}
                      </p>
                    )}
                  </div>
                )}

                {/* Tags */}
                <div className="space-y-2">
                  <label htmlFor="tags" className="block text-sm font-semibold text-gray-900">
                    Tags
                  </label>
                  <input
                    id="tags"
                    value={tagInput}
                    onChange={(e) => setTagInput(e.target.value)}
                    onKeyDown={handleTagAdd}
                    placeholder="Add tags and press Enter"
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 transition-colors"
                  />
                  {formData.tags.length > 0 && (
                    <div className="flex flex-wrap gap-2 mt-3">
                      {formData.tags.map((tag) => (
                        <motion.span
                          key={tag}
                          initial={{ opacity: 0, scale: 0.8 }}
                          animate={{ opacity: 1, scale: 1 }}
                          className="inline-flex items-center px-3 py-1 bg-primary-100 text-primary-800 rounded-full text-sm"
                        >
                          {tag}
                          <button
                            type="button"
                            onClick={() => removeTag(tag)}
                            className="ml-2 hover:bg-primary-200 rounded-full p-0.5 transition-colors"
                          >
                            <X className="w-3 h-3" />
                          </button>
                        </motion.span>
                      ))}
                    </div>
                  )}
                </div>

                {/* Submit Buttons */}
                <div className="flex justify-end gap-4 pt-6 border-t border-gray-200">
                  <button
                    type="button"
                    onClick={onClose}
                    disabled={isSubmitting}
                    className="px-6 py-3 border border-gray-300 rounded-xl text-gray-700 hover:bg-gray-50 transition-colors disabled:opacity-50"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={isSubmitting || files.some(f => f.status === 'uploading')}
                    className="px-6 py-3 bg-primary-600 text-white rounded-xl hover:bg-primary-700 transition-colors disabled:opacity-50 min-w-[140px] flex items-center justify-center"
                  >
                    {isSubmitting ? (
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                        className="w-5 h-5 border-2 border-current border-t-transparent rounded-full"
                      />
                    ) : (
                      'Add Content'
                    )}
                  </button>
                </div>
              </form>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  )
} 