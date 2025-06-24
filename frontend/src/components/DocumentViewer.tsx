'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  XMarkIcon,
  ArrowDownTrayIcon,
  DocumentTextIcon,
  PhotoIcon,
  TableCellsIcon,
  FilmIcon,
  MusicalNoteIcon,
  ArchiveBoxIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline'

interface DocumentViewerProps {
  isOpen: boolean
  onClose: () => void
  document: {
    id: string
    name: string
    displayName?: string
    type: string
    size: number
    url?: string
    content?: string
  }
}

export default function DocumentViewer({ isOpen, onClose, document }: DocumentViewerProps) {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [content, setContent] = useState<string | null>(null)

  useEffect(() => {
    if (isOpen && document) {
      loadDocument()
    }
  }, [isOpen, document])

  const loadDocument = async () => {
    setLoading(true)
    setError(null)
    setContent(null)

    try {
      // If content is already provided, use it
      if (document.content) {
        setContent(document.content)
        setLoading(false)
        return
      }

      // For uploaded files, try to load from the uploads directory
      const fileUrl = document.url || `/api/files/${document.id}`
      
      // Handle different file types
      const fileExtension = document.name.split('.').pop()?.toLowerCase()
      
      if (['txt', 'csv', 'json', 'xml', 'html', 'css', 'js', 'py', 'md'].includes(fileExtension || '')) {
        // Load text-based files
        const response = await fetch(fileUrl)
        if (response.ok) {
          const textContent = await response.text()
          setContent(textContent)
        } else {
          throw new Error('Failed to load document')
        }
      } else if (['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'].includes(fileExtension || '')) {
        // For images, set the URL as content
        setContent(fileUrl)
      } else if (fileExtension === 'pdf') {
        // For PDFs, we'll show a message to download or use browser's built-in viewer
        setContent('PDF_VIEWER')
      } else {
        // For other file types, show download option
        setContent('DOWNLOAD_ONLY')
      }
    } catch (err) {
      console.error('Error loading document:', err)
      setError('Failed to load document. The file might not be available.')
    } finally {
      setLoading(false)
    }
  }

  const handleDownload = () => {
    const fileUrl = document.url || `/api/files/${document.id}`
    const link = window.document.createElement('a')
    link.href = fileUrl
    link.download = document.name
    window.document.body.appendChild(link)
    link.click()
    window.document.body.removeChild(link)
  }

  const getFileIcon = (type: string) => {
    const extension = type.toLowerCase()
    switch (extension) {
      case 'pdf':
      case 'doc':
      case 'docx':
      case 'txt':
      case 'md':
        return <DocumentTextIcon className="h-8 w-8" />
      case 'jpg':
      case 'jpeg':
      case 'png':
      case 'gif':
      case 'svg':
      case 'webp':
        return <PhotoIcon className="h-8 w-8" />
      case 'xlsx':
      case 'xls':
      case 'csv':
        return <TableCellsIcon className="h-8 w-8" />
      case 'mp4':
      case 'avi':
      case 'mov':
      case 'webm':
        return <FilmIcon className="h-8 w-8" />
      case 'mp3':
      case 'wav':
      case 'ogg':
        return <MusicalNoteIcon className="h-8 w-8" />
      default:
        return <ArchiveBoxIcon className="h-8 w-8" />
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const renderContent = () => {
    if (loading) {
      return (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          <span className="ml-3 text-gray-600">Loading document...</span>
        </div>
      )
    }

    if (error) {
      return (
        <div className="flex flex-col items-center justify-center h-64 text-center">
          <ExclamationTriangleIcon className="h-12 w-12 text-red-500 mb-4" />
          <p className="text-red-600 mb-4">{error}</p>
          <button
            onClick={handleDownload}
            className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            Download File
          </button>
        </div>
      )
    }

    const fileExtension = document.name.split('.').pop()?.toLowerCase()

    // Handle different content types
    if (content === 'PDF_VIEWER') {
      return (
        <div className="text-center py-8">
          <DocumentTextIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">PDF Document</h3>
          <p className="text-gray-600 mb-6">
            This PDF can be viewed in your browser or downloaded to your device.
          </p>
          <div className="space-y-3">
            <button
              onClick={() => window.open(document.url || `/api/files/${document.id}`, '_blank')}
              className="block w-full px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
            >
              Open in New Tab
            </button>
            <button
              onClick={handleDownload}
              className="block w-full px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Download PDF
            </button>
          </div>
        </div>
      )
    }

    if (content === 'DOWNLOAD_ONLY') {
      return (
        <div className="text-center py-8">
          {getFileIcon(fileExtension || '')}
          <h3 className="text-lg font-medium text-gray-900 mb-2 mt-4">
            {document.displayName || document.name}
          </h3>
          <p className="text-gray-600 mb-6">
            This file type cannot be previewed. Click below to download.
          </p>
          <button
            onClick={handleDownload}
            className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors inline-flex items-center"
          >
            <ArrowDownTrayIcon className="h-4 w-4 mr-2" />
            Download File
          </button>
        </div>
      )
    }

    // Handle images
    if (['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'].includes(fileExtension || '')) {
      return (
        <div className="text-center">
          <img
            src={content || ''}
            alt={document.displayName || document.name}
            className="max-w-full max-h-96 mx-auto rounded-lg shadow-lg"
            onError={() => setError('Failed to load image')}
          />
        </div>
      )
    }

    // Handle text content
    if (content && typeof content === 'string') {
      return (
        <div className="max-h-96 overflow-y-auto">
          <pre className="whitespace-pre-wrap text-sm text-gray-800 font-mono bg-gray-50 p-4 rounded-lg">
            {content}
          </pre>
        </div>
      )
    }

    return (
      <div className="text-center py-8">
        <ExclamationTriangleIcon className="h-12 w-12 text-yellow-500 mx-auto mb-4" />
        <p className="text-gray-600">Unable to preview this document.</p>
      </div>
    )
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
          onClick={onClose}
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            className="bg-white rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="text-gray-600">
                    {getFileIcon(document.name.split('.').pop() || '')}
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">
                      {document.displayName || document.name}
                    </h3>
                    <div className="flex items-center space-x-4 text-sm text-gray-600">
                      <span>{formatFileSize(document.size)}</span>
                      <span>{document.type.toUpperCase()}</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={handleDownload}
                    className="p-2 text-gray-600 hover:text-gray-900 rounded-lg hover:bg-gray-100 transition-colors"
                    title="Download"
                  >
                    <ArrowDownTrayIcon className="h-5 w-5" />
                  </button>
                  <button
                    onClick={onClose}
                    className="p-2 text-gray-600 hover:text-gray-900 rounded-lg hover:bg-gray-100 transition-colors"
                  >
                    <XMarkIcon className="h-5 w-5" />
                  </button>
                </div>
              </div>
            </div>

            {/* Content */}
            <div className="p-6 overflow-y-auto max-h-[70vh]">
              {renderContent()}
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
} 