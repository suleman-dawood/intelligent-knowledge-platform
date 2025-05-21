'use client';

import React, { useState, useEffect } from 'react';
import { searchKnowledge, SearchResult } from '../../lib/api';
import Link from 'next/link';

export default function SearchPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

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

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Knowledge Search</h1>
      
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
        </div>
      )}
    </div>
  );
} 