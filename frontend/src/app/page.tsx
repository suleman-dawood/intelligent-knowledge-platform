'use client'

import { useState } from 'react'
import Link from 'next/link'
import { MagnifyingGlassIcon, ChartBarIcon, CircleStackIcon, MapIcon } from '@heroicons/react/24/outline'
import SearchBox from '@/components/SearchBox'

export default function Home() {
  const [query, setQuery] = useState('')
  
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim()) {
      window.location.href = `/search?q=${encodeURIComponent(query)}`
    }
  }
  
  return (
    <>
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 py-20 px-4 sm:px-6 lg:px-8 text-center">
        <h1 className="text-4xl font-extrabold text-white sm:text-5xl md:text-6xl">
          <span className="block">Intelligent Knowledge</span>
          <span className="block">Aggregation Platform</span>
        </h1>
        <p className="mt-3 max-w-md mx-auto text-lg text-blue-100 sm:text-xl md:mt-5 md:max-w-3xl">
          Discover, explore, and learn from our vast knowledge graph. Connect concepts, find insights, and expand your understanding.
        </p>
        
        <div className="mt-10 max-w-2xl mx-auto">
          <SearchBox 
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onSubmit={handleSearch}
            placeholder="Search for concepts, entities, or ask a question..."
            fullWidth
          />
        </div>
        
        <div className="mt-10 max-w-md mx-auto grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4 lg:max-w-4xl">
          <Link href="/explore" className="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md bg-white text-blue-800 hover:bg-gray-100 transition-colors">
            <MapIcon className="h-5 w-5 mr-2" />
            Explore Knowledge Graph
          </Link>
          <Link href="/search" className="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md bg-white text-blue-800 hover:bg-gray-100 transition-colors">
            <MagnifyingGlassIcon className="h-5 w-5 mr-2" />
            Advanced Search
          </Link>
          <Link href="/dashboard" className="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md bg-white text-blue-800 hover:bg-gray-100 transition-colors">
            <ChartBarIcon className="h-5 w-5 mr-2" />
            Visualize Data
          </Link>
          <Link href="/dashboard" className="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md bg-white text-blue-800 hover:bg-gray-100 transition-colors">
            <CircleStackIcon className="h-5 w-5 mr-2" />
            Dashboard
          </Link>
        </div>
      </div>
      
      {/* Features Section */}
      <div className="py-16 px-4 sm:px-6 lg:px-8 bg-white">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-extrabold text-gray-900 text-center">
            Powerful Knowledge Platform
          </h2>
          <p className="mt-4 max-w-3xl mx-auto text-center text-lg text-gray-500">
            Our platform combines advanced AI, knowledge graphs, and learning agents to create a comprehensive knowledge system.
          </p>
          
          <div className="mt-10">
            <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
              {/* Feature 1 */}
              <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
                <div className="flex items-center justify-center h-12 w-12 rounded-md bg-blue-500 text-white">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z" />
                  </svg>
                </div>
                <h3 className="mt-5 text-lg font-medium text-gray-900">Intelligent Processing</h3>
                <p className="mt-2 text-base text-gray-500">
                  Our system processes information from diverse sources, extracting meaning, concepts, and entities.
                </p>
              </div>
              
              {/* Feature 2 */}
              <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
                <div className="flex items-center justify-center h-12 w-12 rounded-md bg-blue-500 text-white">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M7.5 14.25v2.25m3-4.5v4.5m3-6.75v6.75m3-9v9M6 20.25h12A2.25 2.25 0 0020.25 18V6A2.25 2.25 0 0018 3.75H6A2.25 2.25 0 003.75 6v12A2.25 2.25 0 006 20.25z" />
                  </svg>
                </div>
                <h3 className="mt-5 text-lg font-medium text-gray-900">Knowledge Graph</h3>
                <p className="mt-2 text-base text-gray-500">
                  Explore relationships between concepts, entities, and ideas through our interactive knowledge graph.
                </p>
              </div>
              
              {/* Feature 3 */}
              <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
                <div className="flex items-center justify-center h-12 w-12 rounded-md bg-blue-500 text-white">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 3v11.25A2.25 2.25 0 006 16.5h2.25M3.75 3h-1.5m1.5 0h16.5m0 0h1.5m-1.5 0v11.25A2.25 2.25 0 0118 16.5h-2.25m-7.5 0h7.5m-7.5 0l-1 3m8.5-3l1 3m0 0l.5 1.5m-.5-1.5h-9.5m0 0l-.5 1.5m.75-9l3-3 2.148 2.148A12.061 12.061 0 0116.5 7.605" />
                  </svg>
                </div>
                <h3 className="mt-5 text-lg font-medium text-gray-900">Continuous Learning</h3>
                <p className="mt-2 text-base text-gray-500">
                  Our platform continuously learns from new information and user interactions to improve over time.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Stats Section */}
      <div className="bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-2xl font-semibold text-gray-900 text-center">Platform Statistics</h2>
          
          <div className="mt-10 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
            {/* Stat 1 */}
            <div className="bg-white shadow rounded-lg p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0 bg-blue-100 rounded-md p-3">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6 text-blue-600">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M18 18.72a9.094 9.094 0 003.741-.479 3 3 0 00-4.682-2.72m.94 3.198l.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0112 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 016 18.719m12 0a5.971 5.971 0 00-.941-3.197m0 0A5.995 5.995 0 0012 12.75a5.995 5.995 0 00-5.058 2.772m0 0a3 3 0 00-4.681 2.72 8.986 8.986 0 003.74.477m.94-3.197a5.971 5.971 0 00-.94 3.197M15 6.75a3 3 0 11-6 0 3 3 0 016 0zm6 3a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0zm-13.5 0a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0z" />
                  </svg>
                </div>
                <div className="ml-5">
                  <p className="text-sm font-medium text-gray-500 truncate">Entities</p>
                  <p className="text-3xl font-semibold text-gray-900">12,580+</p>
                </div>
              </div>
            </div>
            
            {/* Stat 2 */}
            <div className="bg-white shadow rounded-lg p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0 bg-blue-100 rounded-md p-3">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6 text-blue-600">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M13.19 8.688a4.5 4.5 0 011.242 7.244l-4.5 4.5a4.5 4.5 0 01-6.364-6.364l1.757-1.757m13.35-.622l1.757-1.757a4.5 4.5 0 00-6.364-6.364l-4.5 4.5a4.5 4.5 0 001.242 7.244" />
                  </svg>
                </div>
                <div className="ml-5">
                  <p className="text-sm font-medium text-gray-500 truncate">Relationships</p>
                  <p className="text-3xl font-semibold text-gray-900">35,624+</p>
                </div>
              </div>
            </div>
            
            {/* Stat 3 */}
            <div className="bg-white shadow rounded-lg p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0 bg-blue-100 rounded-md p-3">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6 text-blue-600">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
                  </svg>
                </div>
                <div className="ml-5">
                  <p className="text-sm font-medium text-gray-500 truncate">Sources</p>
                  <p className="text-3xl font-semibold text-gray-900">1,250+</p>
                </div>
              </div>
            </div>
            
            {/* Stat 4 */}
            <div className="bg-white shadow rounded-lg p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0 bg-blue-100 rounded-md p-3">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6 text-blue-600">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9.879 7.519c1.171-1.025 3.071-1.025 4.242 0 1.172 1.025 1.172 2.687 0 3.712-.203.179-.43.326-.67.442-.745.361-1.45.999-1.45 1.827v.75M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9 5.25h.008v.008H12v-.008z" />
                  </svg>
                </div>
                <div className="ml-5">
                  <p className="text-sm font-medium text-gray-500 truncate">Queries</p>
                  <p className="text-3xl font-semibold text-gray-900">250k+</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  )
} 