'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  DocumentTextIcon,
  MagnifyingGlassIcon,
  EyeIcon,
  PencilIcon,
  TrashIcon,
  FunnelIcon,
  CalendarIcon,
  DocumentIcon,
  PhotoIcon,
  FilmIcon,
  MusicalNoteIcon,
  ArchiveBoxIcon,
  XMarkIcon,
  CheckIcon,
  ExclamationTriangleIcon,
  PlusIcon,
  CloudArrowUpIcon,
} from '@heroicons/react/24/outline';

interface ContentItem {
  id: string;
  name: string;
  type: 'pdf' | 'docx' | 'xlsx' | 'image' | 'video' | 'audio' | 'other';
  size: number;
  uploadDate: string;
  lastModified: string;
  tags: string[];
  summary?: string;
  url?: string;
}

const ContentPage = () => {
  const [contentItems, setContentItems] = useState<ContentItem[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFilter, setSelectedFilter] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'name' | 'date' | 'size'>('date');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [selectedItems, setSelectedItems] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [previewItem, setPreviewItem] = useState<ContentItem | null>(null);
  const [editingItem, setEditingItem] = useState<ContentItem | null>(null);
  const [editName, setEditName] = useState('');
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<string | null>(null);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [uploadFiles, setUploadFiles] = useState<FileList | null>(null);
  const [uploading, setUploading] = useState(false);

  // Fetch content from backend
  useEffect(() => {
    const fetchContent = async () => {
      setIsLoading(true);
      try {
        const response = await fetch('http://localhost:3100/api/content');
        if (response.ok) {
          const data = await response.json();
          setContentItems(data.files || []);
        } else {
          // Fallback to mock data if API fails
          const mockData: ContentItem[] = [
            {
              id: '1',
              name: 'Machine Learning Fundamentals.pdf',
              type: 'pdf',
              size: 2048000,
              uploadDate: '2024-01-15T10:30:00Z',
              lastModified: '2024-01-15T10:30:00Z',
              tags: ['machine learning', 'AI', 'fundamentals'],
              summary: 'Comprehensive guide to machine learning concepts and algorithms.',
            },
            {
              id: '2',
              name: 'Data Analysis Report.xlsx',
              type: 'xlsx',
              size: 512000,
              uploadDate: '2024-01-14T14:20:00Z',
              lastModified: '2024-01-16T09:15:00Z',
              tags: ['data analysis', 'statistics', 'report'],
              summary: 'Statistical analysis of user behavior data with visualizations.',
            },
            {
              id: '3',
              name: 'Project Proposal.docx',
              type: 'docx',
              size: 256000,
              uploadDate: '2024-01-13T16:45:00Z',
              lastModified: '2024-01-13T16:45:00Z',
              tags: ['proposal', 'project', 'business'],
              summary: 'Detailed project proposal for the new AI initiative.',
            },
          ];
          setContentItems(mockData);
        }
      } catch (error) {
        console.error('Failed to fetch content:', error);
        // Fallback to empty array
        setContentItems([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchContent();
  }, []);

  const handleFileUpload = async () => {
    if (!uploadFiles || uploadFiles.length === 0) return;
    
    setUploading(true);
    const formData = new FormData();
    
    Array.from(uploadFiles).forEach((file) => {
      formData.append('files', file);
    });

    try {
      const response = await fetch('http://localhost:3100/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        // Refresh content list
        const contentResponse = await fetch('http://localhost:3100/api/content');
        if (contentResponse.ok) {
          const data = await contentResponse.json();
          setContentItems(data.files || []);
        }
        setShowUploadModal(false);
        setUploadFiles(null);
      } else {
        console.error('Upload failed');
      }
    } catch (error) {
      console.error('Upload error:', error);
    } finally {
      setUploading(false);
    }
  };

  const getFileIcon = (type: string) => {
    switch (type) {
      case 'pdf':
      case 'docx':
        return <DocumentTextIcon className="h-8 w-8" />;
      case 'xlsx':
        return <DocumentIcon className="h-8 w-8" />;
      case 'image':
        return <PhotoIcon className="h-8 w-8" />;
      case 'video':
        return <FilmIcon className="h-8 w-8" />;
      case 'audio':
        return <MusicalNoteIcon className="h-8 w-8" />;
      default:
        return <ArchiveBoxIcon className="h-8 w-8" />;
    }
  };

  const getFileTypeColor = (type: string) => {
    switch (type) {
      case 'pdf':
        return 'text-red-600 bg-red-50';
      case 'docx':
        return 'text-blue-600 bg-blue-50';
      case 'xlsx':
        return 'text-green-600 bg-green-50';
      case 'image':
        return 'text-purple-600 bg-purple-50';
      case 'video':
        return 'text-orange-600 bg-orange-50';
      case 'audio':
        return 'text-pink-600 bg-pink-50';
      default:
        return 'text-secondary-600 bg-secondary-50';
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const filteredAndSortedItems = contentItems
    .filter(item => {
      const matchesSearch = item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                           item.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
      const matchesFilter = selectedFilter === 'all' || item.type === selectedFilter;
      return matchesSearch && matchesFilter;
    })
    .sort((a, b) => {
      let comparison = 0;
      switch (sortBy) {
        case 'name':
          comparison = a.name.localeCompare(b.name);
          break;
        case 'date':
          comparison = new Date(a.uploadDate).getTime() - new Date(b.uploadDate).getTime();
          break;
        case 'size':
          comparison = a.size - b.size;
          break;
      }
      return sortOrder === 'asc' ? comparison : -comparison;
    });

  const handleSelectItem = (id: string) => {
    setSelectedItems(prev => 
      prev.includes(id) 
        ? prev.filter(item => item !== id)
        : [...prev, id]
    );
  };

  const handleSelectAll = () => {
    if (selectedItems.length === filteredAndSortedItems.length) {
      setSelectedItems([]);
    } else {
      setSelectedItems(filteredAndSortedItems.map(item => item.id));
    }
  };

  const handleRename = (item: ContentItem) => {
    setEditingItem(item);
    setEditName(item.name);
  };

  const handleSaveRename = () => {
    if (editingItem && editName.trim()) {
      setContentItems(prev => 
        prev.map(item => 
          item.id === editingItem.id 
            ? { ...item, name: editName.trim() }
            : item
        )
      );
      setEditingItem(null);
      setEditName('');
    }
  };

  const handleDelete = (id: string) => {
    setContentItems(prev => prev.filter(item => item.id !== id));
    setShowDeleteConfirm(null);
  };

  const handleBulkDelete = () => {
    setContentItems(prev => prev.filter(item => !selectedItems.includes(item.id)));
    setSelectedItems([]);
  };

  const filterOptions = [
    { value: 'all', label: 'All Files', count: contentItems.length },
    { value: 'pdf', label: 'PDF', count: contentItems.filter(item => item.type === 'pdf').length },
    { value: 'docx', label: 'Word', count: contentItems.filter(item => item.type === 'docx').length },
    { value: 'xlsx', label: 'Excel', count: contentItems.filter(item => item.type === 'xlsx').length },
  ];

  return (
    <div className="min-h-screen bg-secondary-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-secondary-900 mb-2">Content Library</h1>
            <p className="text-secondary-600">Manage your uploaded documents and files</p>
          </div>
          <button
            onClick={() => setShowUploadModal(true)}
            className="inline-flex items-center px-6 py-3 bg-primary-600 text-white font-semibold rounded-xl hover:bg-primary-700 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-1"
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            Add Content
          </button>
        </div>

        {/* Controls */}
        <div className="bg-white rounded-2xl shadow-sm border border-secondary-200 p-6 mb-6">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
            {/* Search */}
            <div className="relative flex-1 max-w-md">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-secondary-400" />
              <input
                type="text"
                placeholder="Search files..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent text-gray-900 placeholder-gray-500"
              />
            </div>

            {/* Filters and Sort */}
            <div className="flex items-center space-x-4">
              {/* Filter */}
              <div className="relative">
                <select
                  value={selectedFilter}
                  onChange={(e) => setSelectedFilter(e.target.value)}
                  className="appearance-none bg-white border border-gray-300 rounded-lg px-4 py-2 pr-8 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent text-gray-900"
                >
                  {filterOptions.map(option => (
                    <option key={option.value} value={option.value}>
                      {option.label} ({option.count})
                    </option>
                  ))}
                </select>
                <FunnelIcon className="absolute right-2 top-1/2 transform -translate-y-1/2 h-4 w-4 text-secondary-400 pointer-events-none" />
              </div>

              {/* Sort */}
              <div className="flex items-center space-x-2">
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as 'name' | 'date' | 'size')}
                  className="appearance-none bg-white border border-gray-300 rounded-lg px-3 py-2 pr-8 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent text-gray-900"
                >
                  <option value="date">Sort by Date</option>
                  <option value="name">Sort by Name</option>
                  <option value="size">Sort by Size</option>
                </select>
                <button
                  onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                  className="p-2 border border-secondary-300 rounded-lg hover:bg-secondary-50 transition-colors text-secondary-700"
                  title={`Sort ${sortOrder === 'asc' ? 'Descending' : 'Ascending'}`}
                >
                  {sortOrder === 'asc' ? '↑' : '↓'}
                </button>
              </div>
            </div>
          </div>

          {/* Bulk Actions */}
          {selectedItems.length > 0 && (
            <div className="mt-4 pt-4 border-t border-secondary-200">
              <div className="flex items-center justify-between">
                <span className="text-sm text-secondary-600">
                  {selectedItems.length} item{selectedItems.length !== 1 ? 's' : ''} selected
                </span>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => setSelectedItems([])}
                    className="px-3 py-1 text-sm text-secondary-600 hover:text-secondary-900 transition-colors"
                  >
                    Clear selection
                  </button>
                  <button
                    onClick={handleBulkDelete}
                    className="px-4 py-2 bg-error-600 text-white text-sm rounded-lg hover:bg-error-700 transition-colors"
                  >
                    Delete selected
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Content Grid */}
        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="bg-white rounded-2xl p-6 animate-pulse">
                <div className="h-8 w-8 bg-secondary-200 rounded mb-4"></div>
                <div className="h-4 bg-secondary-200 rounded mb-2"></div>
                <div className="h-3 bg-secondary-200 rounded w-3/4 mb-4"></div>
                <div className="flex space-x-2">
                  <div className="h-6 w-16 bg-secondary-200 rounded"></div>
                  <div className="h-6 w-12 bg-secondary-200 rounded"></div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredAndSortedItems.map((item) => (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className={`bg-white rounded-2xl shadow-sm border-2 transition-all duration-200 hover:shadow-md ${
                  selectedItems.includes(item.id) 
                    ? 'border-primary-500 bg-primary-50' 
                    : 'border-secondary-200 hover:border-secondary-300'
                }`}
              >
                <div className="p-6">
                  {/* Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <div className={`p-2 rounded-lg ${getFileTypeColor(item.type)}`}>
                        {getFileIcon(item.type)}
                      </div>
                      <div className="flex-1 min-w-0">
                        {editingItem?.id === item.id ? (
                          <div className="flex items-center space-x-2">
                            <input
                              type="text"
                              value={editName}
                              onChange={(e) => setEditName(e.target.value)}
                              className="flex-1 px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 text-gray-900"
                              onKeyPress={(e) => e.key === 'Enter' && handleSaveRename()}
                              autoFocus
                            />
                            <button
                              onClick={handleSaveRename}
                              className="p-1 text-success-600 hover:text-success-700"
                            >
                              <CheckIcon className="h-4 w-4" />
                            </button>
                            <button
                              onClick={() => setEditingItem(null)}
                              className="p-1 text-secondary-600 hover:text-secondary-700"
                            >
                              <XMarkIcon className="h-4 w-4" />
                            </button>
                          </div>
                        ) : (
                          <h3 className="font-medium text-secondary-900 truncate" title={item.name}>
                            {item.name}
                          </h3>
                        )}
                      </div>
                    </div>
                    <input
                      type="checkbox"
                      checked={selectedItems.includes(item.id)}
                      onChange={() => handleSelectItem(item.id)}
                      className="rounded border-secondary-300 text-primary-600 focus:ring-primary-500"
                    />
                  </div>

                  {/* Summary */}
                  {item.summary && (
                    <p className="text-sm text-secondary-600 mb-4 line-clamp-2">
                      {item.summary}
                    </p>
                  )}

                  {/* Tags */}
                  <div className="flex flex-wrap gap-1 mb-4">
                    {item.tags.slice(0, 3).map((tag) => (
                      <span
                        key={tag}
                        className="px-2 py-1 bg-secondary-100 text-secondary-700 text-xs rounded-full"
                      >
                        {tag}
                      </span>
                    ))}
                    {item.tags.length > 3 && (
                      <span className="px-2 py-1 bg-secondary-100 text-secondary-700 text-xs rounded-full">
                        +{item.tags.length - 3}
                      </span>
                    )}
                  </div>

                  {/* Metadata */}
                  <div className="text-xs text-secondary-500 mb-4 space-y-1">
                    <div className="flex items-center space-x-1">
                      <CalendarIcon className="h-3 w-3" />
                      <span>{formatDate(item.uploadDate)}</span>
                    </div>
                    <div>Size: {formatFileSize(item.size)}</div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => setPreviewItem(item)}
                        className="p-2 text-secondary-600 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                        title="Preview"
                      >
                        <EyeIcon className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => handleRename(item)}
                        className="p-2 text-secondary-600 hover:text-accent-600 hover:bg-accent-50 rounded-lg transition-colors"
                        title="Rename"
                      >
                        <PencilIcon className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => setShowDeleteConfirm(item.id)}
                        className="p-2 text-secondary-600 hover:text-error-600 hover:bg-error-50 rounded-lg transition-colors"
                        title="Delete"
                      >
                        <TrashIcon className="h-4 w-4" />
                      </button>
                    </div>
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getFileTypeColor(item.type)}`}>
                      {item.type.toUpperCase()}
                    </span>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}

        {/* Empty State */}
        {!isLoading && filteredAndSortedItems.length === 0 && (
          <div className="text-center py-12">
            <ArchiveBoxIcon className="h-16 w-16 text-secondary-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-secondary-900 mb-2">No files found</h3>
            <p className="text-secondary-600">
              {searchQuery || selectedFilter !== 'all' 
                ? 'Try adjusting your search or filter criteria.'
                : 'Upload some files to get started.'}
            </p>
          </div>
        )}
      </div>

      {/* Preview Modal */}
      <AnimatePresence>
        {previewItem && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
            onClick={() => setPreviewItem(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white rounded-2xl max-w-2xl w-full max-h-[80vh] overflow-hidden"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="p-6 border-b border-secondary-200">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className={`p-2 rounded-lg ${getFileTypeColor(previewItem.type)}`}>
                      {getFileIcon(previewItem.type)}
                    </div>
                    <div>
                      <h3 className="font-semibold text-secondary-900">{previewItem.name}</h3>
                      <p className="text-sm text-secondary-600">{formatFileSize(previewItem.size)}</p>
                    </div>
                  </div>
                  <button
                    onClick={() => setPreviewItem(null)}
                    className="p-2 text-secondary-600 hover:text-secondary-900 rounded-lg hover:bg-secondary-100 transition-colors"
                  >
                    <XMarkIcon className="h-5 w-5" />
                  </button>
                </div>
              </div>
              <div className="p-6 overflow-y-auto">
                <div className="space-y-4">
                  <div>
                    <h4 className="font-medium text-secondary-900 mb-2">Summary</h4>
                    <p className="text-secondary-700">{previewItem.summary}</p>
                  </div>
                  <div>
                    <h4 className="font-medium text-secondary-900 mb-2">Tags</h4>
                    <div className="flex flex-wrap gap-2">
                      {previewItem.tags.map((tag) => (
                        <span
                          key={tag}
                          className="px-3 py-1 bg-primary-100 text-primary-700 text-sm rounded-full"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div>
                    <h4 className="font-medium text-secondary-900 mb-2">Details</h4>
                    <div className="space-y-2 text-sm text-secondary-600">
                      <div>Uploaded: {formatDate(previewItem.uploadDate)}</div>
                      <div>Last modified: {formatDate(previewItem.lastModified)}</div>
                      <div>File type: {previewItem.type.toUpperCase()}</div>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Upload Modal */}
      <AnimatePresence>
        {showUploadModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
            onClick={() => !uploading && setShowUploadModal(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white rounded-2xl max-w-md w-full p-6"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center space-x-3 mb-4">
                <div className="p-2 bg-primary-100 rounded-lg">
                  <CloudArrowUpIcon className="h-6 w-6 text-primary-600" />
                </div>
                <h3 className="text-lg font-semibold text-secondary-900">Upload Files</h3>
              </div>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    Select files to upload
                  </label>
                  <input
                    type="file"
                    multiple
                    accept=".pdf,.doc,.docx,.xls,.xlsx,.txt,.md"
                    onChange={(e) => setUploadFiles(e.target.files)}
                    className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent text-secondary-900"
                    disabled={uploading}
                  />
                  <p className="text-xs text-secondary-500 mt-1">
                    Supported formats: PDF, Word, Excel, Text, Markdown
                  </p>
                </div>
                {uploadFiles && uploadFiles.length > 0 && (
                  <div className="bg-secondary-50 rounded-lg p-3">
                    <p className="text-sm font-medium text-secondary-700 mb-2">
                      Selected files ({uploadFiles.length}):
                    </p>
                    <div className="space-y-1">
                      {Array.from(uploadFiles).map((file, index) => (
                        <div key={index} className="text-sm text-secondary-600">
                          {file.name} ({Math.round(file.size / 1024)} KB)
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
              <div className="flex items-center justify-end space-x-3 mt-6">
                <button
                  onClick={() => setShowUploadModal(false)}
                  className="px-4 py-2 text-secondary-600 hover:text-secondary-900 transition-colors"
                  disabled={uploading}
                >
                  Cancel
                </button>
                <button
                  onClick={handleFileUpload}
                  disabled={!uploadFiles || uploadFiles.length === 0 || uploading}
                  className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {uploading ? 'Uploading...' : 'Upload'}
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Delete Confirmation Modal */}
      <AnimatePresence>
        {showDeleteConfirm && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white rounded-2xl max-w-md w-full p-6"
            >
              <div className="flex items-center space-x-3 mb-4">
                <div className="p-2 bg-error-100 rounded-lg">
                  <ExclamationTriangleIcon className="h-6 w-6 text-error-600" />
                </div>
                <h3 className="text-lg font-semibold text-secondary-900">Delete File</h3>
              </div>
              <p className="text-secondary-600 mb-6">
                Are you sure you want to delete this file? This action cannot be undone.
              </p>
              <div className="flex items-center justify-end space-x-3">
                <button
                  onClick={() => setShowDeleteConfirm(null)}
                  className="px-4 py-2 text-secondary-600 hover:text-secondary-900 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={() => handleDelete(showDeleteConfirm)}
                  className="px-4 py-2 bg-error-600 text-white rounded-lg hover:bg-error-700 transition-colors"
                >
                  Delete
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default ContentPage; 