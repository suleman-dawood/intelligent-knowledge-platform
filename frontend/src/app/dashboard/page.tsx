'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  ArrowTrendingUpIcon, 
  UsersIcon, 
  DocumentTextIcon, 
  LinkIcon,
  ChartBarIcon,
  ClockIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  EyeIcon,
  MagnifyingGlassIcon as SearchIcon
} from '@heroicons/react/24/outline'

import { databaseService, DashboardData } from '../../lib/database'

const StatCard = ({ title, value, icon: Icon, change, changeType = 'positive' }: {
  title: string
  value: string | number
  icon: any
  change?: number
  changeType?: 'positive' | 'negative' | 'neutral'
}) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
  >
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm font-medium text-gray-600">{title}</p>
        <p className="text-3xl font-bold text-gray-900 mt-2">
          {typeof value === 'number' ? value.toLocaleString() : value}
        </p>
        {change !== undefined && (
          <div className="flex items-center mt-2">
            {changeType === 'positive' ? (
              <ArrowUpIcon className="h-4 w-4 text-green-500 mr-1" />
            ) : changeType === 'negative' ? (
              <ArrowDownIcon className="h-4 w-4 text-red-500 mr-1" />
            ) : null}
            <span className={`text-sm font-medium ${
              changeType === 'positive' ? 'text-green-600' : 
              changeType === 'negative' ? 'text-red-600' : 'text-gray-600'
            }`}>
              {change > 0 ? '+' : ''}{change}%
            </span>
            <span className="text-sm text-gray-500 ml-1">vs last week</span>
          </div>
        )}
      </div>
      <div className="bg-primary-50 p-3 rounded-lg">
        <Icon className="h-6 w-6 text-primary-600" />
      </div>
    </div>
  </motion.div>
)

export default function Dashboard() {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  
  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true)
        const data = await databaseService.getDashboardData()
        setDashboardData(data)
      } catch (error) {
        console.error('Error fetching dashboard data:', error)
      } finally {
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
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <motion.div 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
              <p className="mt-2 text-gray-600">
                Welcome back! Here's what's happening with your knowledge platform.
              </p>
            </div>
            <div className="flex gap-3">
              <button className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition-colors">
                <DocumentTextIcon className="h-4 w-4 mr-2" />
                Export Report
              </button>
              <button className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700 transition-colors">
                <ChartBarIcon className="h-4 w-4 mr-2" />
                Analytics
              </button>
            </div>
          </div>
        </motion.div>

        {isLoading || !dashboardData ? (
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4 mb-8">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="bg-white rounded-xl p-6 animate-pulse">
                <div className="h-4 bg-gray-200 rounded mb-4 w-2/3"></div>
                <div className="h-8 bg-gray-200 rounded mb-4"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2"></div>
              </div>
            ))}
          </div>
        ) : (
          <>
            {/* Stats Grid */}
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4 mb-8">
              <StatCard
                title="Total Entities"
                value={dashboardData.stats.totalEntities}
                icon={UsersIcon}
                change={dashboardData.stats.weeklyGrowth.entities}
                changeType="positive"
              />
              <StatCard
                title="Relationships"
                value={dashboardData.stats.totalRelations}
                icon={LinkIcon}
                change={dashboardData.stats.weeklyGrowth.relations}
                changeType="positive"
              />
              <StatCard
                title="New Entities (30d)"
                value={dashboardData.stats.recentEntities}
                icon={ArrowTrendingUpIcon}
                change={dashboardData.stats.weeklyGrowth.sources}
                changeType="positive"
              />
              <StatCard
                title="Active Sources"
                value={dashboardData.stats.recentSources}
                icon={DocumentTextIcon}
                change={dashboardData.stats.weeklyGrowth.queries}
                changeType="positive"
              />
            </div>
            
            {/* Content Grid */}
            <div className="grid gap-8 lg:grid-cols-3">
              {/* Trending Topics */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.1 }}
                className="bg-white rounded-xl shadow-sm border border-gray-200"
              >
                <div className="p-6 border-b border-gray-200">
                  <h3 className="text-lg font-semibold text-gray-900">Trending Topics</h3>
                  <p className="text-sm text-gray-600 mt-1">Most popular topics being explored</p>
                </div>
                <div className="p-6">
                  <div className="space-y-4">
                    {dashboardData.trendingTopics.map((topic, index) => (
                      <div key={topic.name} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                        <div className="flex items-center">
                          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary-100 text-primary-600 text-sm font-medium mr-3">
                            {index + 1}
                          </div>
                          <div>
                            <p className="text-sm font-medium text-gray-900">{topic.name}</p>
                            <p className="text-xs text-gray-500">Score: {topic.score.toFixed(2)}</p>
                          </div>
                        </div>
                        <div className="flex items-center">
                          {topic.change > 0 ? (
                            <ArrowUpIcon className="h-4 w-4 text-green-500 mr-1" />
                          ) : (
                            <ArrowDownIcon className="h-4 w-4 text-red-500 mr-1" />
                          )}
                          <span className={`text-xs font-medium ${topic.change > 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {topic.change > 0 ? '+' : ''}{topic.change}%
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </motion.div>
              
              {/* Recent Queries */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="bg-white rounded-xl shadow-sm border border-gray-200 lg:col-span-2"
              >
                <div className="p-6 border-b border-gray-200">
                  <h3 className="text-lg font-semibold text-gray-900">Recent Queries</h3>
                  <p className="text-sm text-gray-600 mt-1">Latest questions asked in the platform</p>
                </div>
                <div className="p-6">
                  <div className="space-y-4">
                    {dashboardData.recentQueries.map((query) => (
                      <div key={query.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                        <div className="flex items-center flex-1">
                          <div className="bg-primary-100 p-2 rounded-lg mr-3">
                            <SearchIcon className="h-4 w-4 text-primary-600" />
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-gray-900 truncate">{query.text}</p>
                            <div className="flex items-center mt-1 text-xs text-gray-500">
                              <ClockIcon className="h-3 w-3 mr-1" />
                              <span>{formatDate(query.timestamp)}</span>
                              <span className="mx-2">•</span>
                              <EyeIcon className="h-3 w-3 mr-1" />
                              <span>{query.results} results</span>
                            </div>
                          </div>
                        </div>
                        <div className="flex gap-2 ml-4">
                          <button className="text-xs text-primary-600 hover:text-primary-700 font-medium px-2 py-1 rounded hover:bg-primary-50 transition-colors">
                            View Results
                          </button>
                          <button className="text-xs text-gray-600 hover:text-gray-700 font-medium px-2 py-1 rounded hover:bg-gray-100 transition-colors">
                            Similar
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </motion.div>
            </div>

            {/* Activity Feed */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="mt-8 bg-white rounded-xl shadow-sm border border-gray-200"
            >
              <div className="p-6 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">Recent Activity</h3>
                <p className="text-sm text-gray-600 mt-1">Latest system activities and updates</p>
              </div>
              <div className="p-6">
                <div className="space-y-4">
                  {dashboardData.activityFeed.map((activity, index) => (
                    <div key={index} className="flex items-center p-3 bg-gray-50 rounded-lg">
                      <div className={`w-2 h-2 rounded-full mr-3 ${
                        activity.type === 'content_added' ? 'bg-green-500' :
                        activity.type === 'query_processed' ? 'bg-blue-500' :
                        activity.type === 'knowledge_extracted' ? 'bg-purple-500' :
                        'bg-orange-500'
                      }`} />
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900">{activity.title}</p>
                        <p className="text-xs text-gray-500">{activity.time}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          </>
        )}
      </div>
    </div>
  )
} 