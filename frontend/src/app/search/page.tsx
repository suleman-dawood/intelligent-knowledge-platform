'use client';

import React, { useState, useEffect } from 'react';
import { searchKnowledge, SearchResult } from '../../lib/api';
import Link from 'next/link';
import { PlusIcon, MagnifyingGlassIcon, ClockIcon, DocumentTextIcon, TagIcon } from '@heroicons/react/24/outline';
import { motion, AnimatePresence } from 'framer-motion';
import AddContentModal from '../../components/ui/AddContentModal';

export default function SearchPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showAddContent, setShowAddContent] = useState(false);

  // Handle search submission
  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!query.trim()) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const searchResults = await searchKnowledge(query);
      setResults(searchResults);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred during search');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Handle content submission from modal
  const handleAddContent = async (data: any) => {
    try {
      // Handle different content types with appropriate endpoints
      if (data.type === 'word' || data.type === 'excel') {
        // Use the document upload endpoint for Word and Excel files
        if (!data.file) {
          throw new Error('No file selected')
        }
        
        const formData = new FormData()
        formData.append('file', data.file)
        
        const response = await fetch('/api/upload-document', {
          method: 'POST',
          body: formData,
        })
        
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}))
          throw new Error(errorData.detail || 'Failed to upload document')
        }
      } else {
        // Default submission logic for other content types
        const formData = new FormData()
        formData.append('type', data.type)
        formData.append('title', data.title)
        formData.append('content', data.content)
        formData.append('url', data.url)
        
        if (data.file) {
          formData.append('file', data.file)
        }

        const response = await fetch('/api/content', {
          method: 'POST',
          body: formData,
        })

        if (!response.ok) {
          throw new Error('Failed to add content')
        }
      }

      // Optionally refresh search results or show success message
    } catch (err) {
      throw err // Re-throw to let modal handle the error
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <motion.div 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Knowledge Search</h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Discover insights from our comprehensive knowledge base. Search through documents, 
            research papers, and curated content to find the information you need.
          </p>
        </motion.div>

        {/* Search Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-2xl shadow-sm border border-gray-200 p-8 mb-8"
        >
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900">Search Knowledge</h2>
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => setShowAddContent(true)}
              className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-xl hover:bg-primary-700 transition-colors shadow-sm"
            >
              <PlusIcon className="h-5 w-5 mr-2" />
              Add Content
            </motion.button>
          </div>
          
          <form onSubmit={handleSearch} className="space-y-4">
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                className="block w-full pl-12 pr-4 py-4 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent text-lg placeholder-gray-500"
                placeholder="Search for concepts, entities, documents, or ask a question..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
              />
            </div>
            <div className="flex justify-center">
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                type="submit"
                className="inline-flex items-center px-8 py-3 bg-primary-600 text-white rounded-xl hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 transition-colors shadow-sm disabled:opacity-50"
                disabled={loading}
              >
                {loading ? (
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                    className="w-5 h-5 border-2 border-current border-t-transparent rounded-full mr-2"
                  />
                ) : (
                  <MagnifyingGlassIcon className="h-5 w-5 mr-2" />
                )}
                {loading ? 'Searching...' : 'Search'}
              </motion.button>
            </div>
          </form>
        </motion.div>

        {/* Error Display */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="bg-red-50 border border-red-200 rounded-xl p-4 mb-6"
            >
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-red-800">Search Error</h3>
                  <p className="text-sm text-red-700 mt-1">{error}</p>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Results Section */}
        <AnimatePresence>
          {results.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              className="space-y-6"
            >
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-gray-900">
                  Search Results ({results.length})
                </h2>
                <div className="text-sm text-gray-500">
                  Found {results.length} result{results.length !== 1 ? 's' : ''} for "{query}"
                </div>
              </div>

              <div className="grid gap-6">
                {results.map((result, index) => (
                  <motion.div
                    key={result.id || index}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">
                          {result.title || 'Untitled'}
                        </h3>
                        <p className="text-gray-600 mb-4 line-clamp-3">
                          {result.content || result.summary || 'No description available.'}
                        </p>
                        
                        <div className="flex items-center text-sm text-gray-500 space-x-4">
                          <div className="flex items-center">
                            <DocumentTextIcon className="h-4 w-4 mr-1" />
                            <span>{result.type || 'Document'}</span>
                          </div>
                          {result.score && (
                            <div className="flex items-center">
                              <span>Relevance: {(result.score * 100).toFixed(1)}%</span>
                            </div>
                          )}
                          {result.timestamp && (
                            <div className="flex items-center">
                              <ClockIcon className="h-4 w-4 mr-1" />
                              <span>{new Date(result.timestamp).toLocaleDateString()}</span>
                            </div>
                          )}
                        </div>

                        {result.tags && result.tags.length > 0 && (
                          <div className="flex items-center mt-3">
                            <TagIcon className="h-4 w-4 text-gray-400 mr-2" />
                            <div className="flex flex-wrap gap-2">
                              {result.tags.slice(0, 5).map((tag, tagIndex) => (
                                <span
                                  key={tagIndex}
                                  className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-primary-100 text-primary-800"
                                >
                                  {tag}
                                </span>
                              ))}
                              {result.tags.length > 5 && (
                                <span className="text-xs text-gray-500">
                                  +{result.tags.length - 5} more
                                </span>
                              )}
                            </div>
                          </div>
                        )}
                      </div>
                      
                      {result.url && (
                        <Link
                          href={result.url}
                          className="ml-4 inline-flex items-center px-3 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition-colors"
                        >
                          View Details
                        </Link>
                      )}
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Empty States */}
        <AnimatePresence>
          {!loading && query.trim() !== '' && results.length === 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              className="text-center py-16"
            >
              <div className="bg-gray-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <MagnifyingGlassIcon className="h-8 w-8 text-gray-400" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No results found</h3>
              <p className="text-gray-600 mb-6">
                We couldn't find anything matching "{query}". Try different keywords or check your spelling.
              </p>
              <div className="space-y-2 text-sm text-gray-500">
                <p>Suggestions:</p>
                <ul className="list-disc list-inside space-y-1">
                  <li>Try broader or more general terms</li>
                  <li>Check for typos in your search query</li>
                  <li>Use different keywords or synonyms</li>
                  <li>Add more content to expand the knowledge base</li>
                </ul>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <AnimatePresence>
          {!query.trim() && !loading && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              className="text-center py-16"
            >
              <div className="bg-primary-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <MagnifyingGlassIcon className="h-8 w-8 text-primary-600" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Start your knowledge search</h3>
              <p className="text-gray-600 mb-6">
                Enter a search term above to explore our comprehensive knowledge base
              </p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-3xl mx-auto text-left">
                <div className="bg-white p-4 rounded-xl border border-gray-200">
                  <h4 className="font-medium text-gray-900 mb-2">Example Searches</h4>
                  <ul className="text-sm text-gray-600 space-y-1">
                    <li>• "artificial intelligence"</li>
                    <li>• "climate change impacts"</li>
                    <li>• "quantum computing basics"</li>
                  </ul>
                </div>
                <div className="bg-white p-4 rounded-xl border border-gray-200">
                  <h4 className="font-medium text-gray-900 mb-2">Search Tips</h4>
                  <ul className="text-sm text-gray-600 space-y-1">
                    <li>• Use specific keywords</li>
                    <li>• Try related terms</li>
                    <li>• Ask questions naturally</li>
                  </ul>
                </div>
                <div className="bg-white p-4 rounded-xl border border-gray-200">
                  <h4 className="font-medium text-gray-900 mb-2">Content Types</h4>
                  <ul className="text-sm text-gray-600 space-y-1">
                    <li>• Research papers</li>
                    <li>• Web articles</li>
                    <li>• PDF documents</li>
                  </ul>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Add Content Modal */}
      <AddContentModal
        isOpen={showAddContent}
        onClose={() => setShowAddContent(false)}
        onSubmit={handleAddContent}
      />
    </div>
  );
} 