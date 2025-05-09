'use client'

import { useState, useEffect } from 'react'
import Header from '@/components/Header'
import Footer from '@/components/Footer'

// Sample dashboard data
const SAMPLE_DATA = {
  recentQueries: [
    { id: 'q1', text: 'What is knowledge integration?', timestamp: '2023-05-08T14:32:15Z' },
    { id: 'q2', text: 'Show me quantum physics concepts', timestamp: '2023-05-08T10:15:42Z' },
    { id: 'q3', text: 'Explain artificial intelligence', timestamp: '2023-05-07T16:45:12Z' },
    { id: 'q4', text: 'Knowledge graph vs database', timestamp: '2023-05-07T09:22:18Z' },
    { id: 'q5', text: 'Machine learning algorithms', timestamp: '2023-05-06T14:12:39Z' },
  ],
  knowledgeStats: {
    totalEntities: 12580,
    totalRelations: 35624,
    recentEntities: 156,
    recentSources: 42,
  },
  trendingTopics: [
    { name: 'Quantum Computing', score: 0.95 },
    { name: 'Neural Networks', score: 0.87 },
    { name: 'Climate Science', score: 0.82 },
    { name: 'Vaccine Research', score: 0.78 },
    { name: 'Space Exploration', score: 0.76 },
  ],
}

export default function Dashboard() {
  const [dashboardData, setDashboardData] = useState(SAMPLE_DATA)
  const [isLoading, setIsLoading] = useState(false)
  
  // In a real app, this would fetch actual data from the backend
  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true)
        // Mock API call delay
        await new Promise(resolve => setTimeout(resolve, 500))
        
        // In a real app, this would be:
        // const response = await fetch('/api/dashboard')
        // const data = await response.json()
        // setDashboardData(data)
        
        setIsLoading(false)
      } catch (error) {
        console.error('Error fetching dashboard data:', error)
        setIsLoading(false)
      }
    }
    
    fetchData()
  }, [])
  
  // Format date for display
  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }
  
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      
      <main className="flex-grow bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="md:flex md:items-center md:justify-between">
            <div className="min-w-0 flex-1">
              <h1 className="text-2xl font-bold leading-7 text-gray-900 sm:truncate sm:leading-9">
                Dashboard
              </h1>
              <p className="mt-1 text-sm text-gray-500">
                Overview of your knowledge platform usage and statistics
              </p>
            </div>
            <div className="mt-4 flex md:ml-4 md:mt-0">
              <button
                type="button"
                className="btn btn-outline ml-3"
              >
                Export Data
              </button>
              <button
                type="button"
                className="btn btn-primary ml-3"
              >
                Generate Report
              </button>
            </div>
          </div>
          
          {isLoading ? (
            <div className="mt-10 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="bg-white shadow rounded-lg p-6 animate-pulse">
                  <div className="h-6 bg-gray-200 rounded mb-4 w-1/2"></div>
                  <div className="h-10 bg-gray-200 rounded mb-4"></div>
                  <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                </div>
              ))}
            </div>
          ) : (
            <>
              {/* Stats Grid */}
              <div className="mt-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
                {/* Entities Stat */}
                <div className="bg-white shadow rounded-lg p-6">
                  <div className="flex items-center">
                    <div className="flex-shrink-0 bg-primary-100 rounded-md p-3">
                      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6 text-primary-600">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M18 18.72a9.094 9.094 0 003.741-.479 3 3 0 00-4.682-2.72m.94 3.198l.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0112 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 016 18.719m12 0a5.971 5.971 0 00-.941-3.197m0 0A5.995 5.995 0 0012 12.75a5.995 5.995 0 00-5.058 2.772m0 0a3 3 0 00-4.681 2.72 8.986 8.986 0 003.74.477m.94-3.197a5.971 5.971 0 00-.94 3.197M15 6.75a3 3 0 11-6 0 3 3 0 016 0zm6 3a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0zm-13.5 0a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0z" />
                      </svg>
                    </div>
                    <div className="ml-5">
                      <p className="text-sm font-medium text-gray-500 truncate">Entities</p>
                      <p className="text-3xl font-semibold text-gray-900">{dashboardData.knowledgeStats.totalEntities.toLocaleString()}</p>
                    </div>
                  </div>
                </div>
                
                {/* Relationships Stat */}
                <div className="bg-white shadow rounded-lg p-6">
                  <div className="flex items-center">
                    <div className="flex-shrink-0 bg-primary-100 rounded-md p-3">
                      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6 text-primary-600">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M13.19 8.688a4.5 4.5 0 011.242 7.244l-4.5 4.5a4.5 4.5 0 01-6.364-6.364l1.757-1.757m13.35-.622l1.757-1.757a4.5 4.5 0 00-6.364-6.364l-4.5 4.5a4.5 4.5 0 001.242 7.244" />
                      </svg>
                    </div>
                    <div className="ml-5">
                      <p className="text-sm font-medium text-gray-500 truncate">Relationships</p>
                      <p className="text-3xl font-semibold text-gray-900">{dashboardData.knowledgeStats.totalRelations.toLocaleString()}</p>
                    </div>
                  </div>
                </div>
                
                {/* New Entities Stat */}
                <div className="bg-white shadow rounded-lg p-6">
                  <div className="flex items-center">
                    <div className="flex-shrink-0 bg-primary-100 rounded-md p-3">
                      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6 text-primary-600">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v6m3-3H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <div className="ml-5">
                      <p className="text-sm font-medium text-gray-500 truncate">New Entities (30d)</p>
                      <p className="text-3xl font-semibold text-gray-900">{dashboardData.knowledgeStats.recentEntities.toLocaleString()}</p>
                    </div>
                  </div>
                </div>
                
                {/* Sources Stat */}
                <div className="bg-white shadow rounded-lg p-6">
                  <div className="flex items-center">
                    <div className="flex-shrink-0 bg-primary-100 rounded-md p-3">
                      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6 text-primary-600">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
                      </svg>
                    </div>
                    <div className="ml-5">
                      <p className="text-sm font-medium text-gray-500 truncate">New Sources (30d)</p>
                      <p className="text-3xl font-semibold text-gray-900">{dashboardData.knowledgeStats.recentSources.toLocaleString()}</p>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Content Grid */}
              <div className="mt-8 grid gap-8 grid-cols-1 lg:grid-cols-3">
                {/* Trending Topics */}
                <div className="bg-white rounded-lg shadow">
                  <div className="px-6 py-5 border-b border-gray-200">
                    <h3 className="text-lg font-medium leading-6 text-gray-900">Trending Topics</h3>
                    <p className="mt-1 text-sm text-gray-500">The most popular topics being explored.</p>
                  </div>
                  <div className="px-6 py-5">
                    <ul className="divide-y divide-gray-200">
                      {dashboardData.trendingTopics.map((topic, index) => (
                        <li key={topic.name} className="py-4">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center">
                              <span className="flex h-8 w-8 items-center justify-center rounded-full bg-primary-100 text-primary-600 text-sm font-medium">
                                {index + 1}
                              </span>
                              <p className="ml-4 text-sm font-medium text-gray-900">{topic.name}</p>
                            </div>
                            <div className="ml-2 flex-shrink-0 flex">
                              <div className="text-sm text-gray-500 bg-gray-100 rounded-full px-3 py-1">
                                Score: {topic.score.toFixed(2)}
                              </div>
                            </div>
                          </div>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
                
                {/* Recent Queries */}
                <div className="bg-white rounded-lg shadow lg:col-span-2">
                  <div className="px-6 py-5 border-b border-gray-200">
                    <h3 className="text-lg font-medium leading-6 text-gray-900">Recent Queries</h3>
                    <p className="mt-1 text-sm text-gray-500">The most recent questions asked in the platform.</p>
                  </div>
                  <div className="px-6 py-5">
                    <ul className="divide-y divide-gray-200">
                      {dashboardData.recentQueries.map((query) => (
                        <li key={query.id} className="py-4">
                          <div className="flex flex-col space-y-2">
                            <div className="flex items-center justify-between">
                              <p className="text-sm font-medium text-primary-600">{query.text}</p>
                              <p className="text-sm text-gray-500">{formatDate(query.timestamp)}</p>
                            </div>
                            <div className="flex">
                              <button
                                type="button"
                                className="text-xs text-gray-600 hover:text-primary-600"
                              >
                                View Results
                              </button>
                              <span className="mx-1 text-gray-500">•</span>
                              <button
                                type="button"
                                className="text-xs text-gray-600 hover:text-primary-600"
                              >
                                Similar Queries
                              </button>
                            </div>
                          </div>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      </main>
      
      <Footer />
    </div>
  )
} 