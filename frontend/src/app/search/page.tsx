'use client';

import React, { useState, useEffect } from 'react';
import { searchKnowledge, SearchResult } from '../../lib/api';
import Link from 'next/link';
import { PlusIcon } from '@heroicons/react/24/outline';

export default function SearchPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showAddContent, setShowAddContent] = useState(false);
  const [contentType, setContentType] = useState('text');
  const [contentData, setContentData] = useState({
    title: '',
    content: '',
    url: '',
    file: null as File | null
  });

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

  // Handle content submission
  const handleAddContent = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const formData = new FormData();
      formData.append('type', contentType);
      formData.append('title', contentData.title);
      formData.append('content', contentData.content);
      formData.append('url', contentData.url);
      
      if (contentData.file) {
        formData.append('file', contentData.file);
      }

      const response = await fetch('/api/content', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        alert('Content added successfully!');
        setShowAddContent(false);
        setContentData({ title: '', content: '', url: '', file: null });
      } else {
        throw new Error('Failed to add content');
      }
    } catch (err) {
      alert('Error adding content: ' + (err instanceof Error ? err.message : 'Unknown error'));
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Knowledge Search</h1>
        <button
          onClick={() => setShowAddContent(true)}
          className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 flex items-center gap-2"
        >
          <PlusIcon className="h-5 w-5" />
          Add Content
        </button>
      </div>
      
      <form onSubmit={handleSearch} className="mb-8">
        <div className="flex">
          <input
            type="text"
            className="flex-grow px-4 py-2 border border-gray-300 rounded-l focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Search for concepts, entities, or documents..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <button
            type="submit"
            className="bg-blue-600 text-white px-6 py-2 rounded-r hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={loading}
          >
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>
      </form>

      {/* Add Content Modal */}
      {showAddContent && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md max-h-[90vh] overflow-y-auto">
            <h2 className="text-xl font-bold mb-4">Add New Content</h2>
            
            <form onSubmit={handleAddContent}>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Content Type</label>
                <select
                  value={contentType}
                  onChange={(e) => setContentType(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="text">Text/Article</option>
                  <option value="pdf">PDF Document</option>
                  <option value="url">Web URL</option>
                  <option value="academic">Academic Paper</option>
                </select>
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Title</label>
                <input
                  type="text"
                  value={contentData.title}
                  onChange={(e) => setContentData({...contentData, title: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              {contentType === 'url' && (
                <div className="mb-4">
                  <label className="block text-sm font-medium mb-2">URL</label>
                  <input
                    type="url"
                    value={contentData.url}
                    onChange={(e) => setContentData({...contentData, url: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
              )}

              {contentType === 'pdf' && (
                <div className="mb-4">
                  <label className="block text-sm font-medium mb-2">PDF File</label>
                  <input
                    type="file"
                    accept=".pdf"
                    onChange={(e) => setContentData({...contentData, file: e.target.files?.[0] || null})}
                    className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
              )}

              {(contentType === 'text' || contentType === 'academic') && (
                <div className="mb-4">
                  <label className="block text-sm font-medium mb-2">Content</label>
                  <textarea
                    value={contentData.content}
                    onChange={(e) => setContentData({...contentData, content: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 h-32"
                    required
                  />
                </div>
              )}

              <div className="flex gap-2">
                <button
                  type="submit"
                  className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 flex-1"
                >
                  Add Content
                </button>
                <button
                  type="button"
                  onClick={() => setShowAddContent(false)}
                  className="bg-gray-300 text-gray-700 px-4 py-2 rounded hover:bg-gray-400 flex-1"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}
      
      {results.length > 0 ? (
        <div>
          <h2 className="text-xl font-semibold mb-4">Search Results ({results.length})</h2>
          <div className="space-y-6">
            {results.map((result) => (
              <div 
                key={result.id} 
                className="p-4 border border-gray-200 rounded shadow-sm hover:shadow"
              >
                <h3 className="text-lg font-medium text-blue-600 mb-2">
                  <Link href={`/explore/entity/${result.id}`}>
                    {result.title}
                  </Link>
                </h3>
                
                <p className="text-gray-600 mb-2">{result.content}</p>
                
                <div className="flex items-center text-sm text-gray-500">
                  <span className="mr-4">Source: {result.source}</span>
                  <span>Relevance: {Math.round(result.score * 100)}%</span>
                </div>
                
                {result.entities.length > 0 && (
                  <div className="mt-3">
                    <span className="text-xs font-medium text-gray-500">Related entities:</span>
                    <div className="mt-1 flex flex-wrap gap-2">
                      {result.entities.map((entity) => (
                        <Link
                          href={`/explore/entity/${entity.id}`}
                          key={entity.id}
                          className="inline-block px-2 py-1 bg-gray-100 text-xs rounded hover:bg-gray-200"
                        >
                          {entity.name} ({entity.type})
                        </Link>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      ) : (
        !loading && query.trim() !== '' && (
          <div className="text-center py-12">
            <p className="text-gray-500">No results found for "{query}"</p>
            <p className="text-sm text-gray-400 mt-2">
              Try different keywords or broaden your search terms
            </p>
          </div>
        )
      )}
      
      {!query.trim() && !loading && (
        <div className="text-center py-12">
          <p className="text-gray-500">Enter a search term to find knowledge in the system</p>
          <p className="text-sm text-gray-400 mt-2">
            Or use the "Add Content" button above to contribute new knowledge
          </p>
        </div>
      )}
    </div>
  );
} 