'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  TrendingUp, 
  TrendingDown, 
  Users, 
  Search, 
  Database, 
  Activity,
  Clock,
  BarChart3
} from 'lucide-react';
import SystemStatus from '../../components/ui/SystemStatus';

interface MetricCard {
  title: string;
  value: string;
  change: number;
  trend: 'up' | 'down';
  icon: React.ComponentType<any>;
  color: string;
}

interface ChartData {
  label: string;
  value: number;
}

const AnalyticsPage: React.FC = () => {
  const [metrics, setMetrics] = useState<MetricCard[]>([
    {
      title: 'Total Queries',
      value: '2,847',
      change: 12.5,
      trend: 'up',
      icon: Search,
      color: 'blue'
    },
    {
      title: 'Knowledge Entries',
      value: '15,432',
      change: 8.2,
      trend: 'up',
      icon: Database,
      color: 'green'
    },
    {
      title: 'Active Users',
      value: '342',
      change: -2.1,
      trend: 'down',
      icon: Users,
      color: 'purple'
    },
    {
      title: 'Avg Response Time',
      value: '248ms',
      change: -15.3,
      trend: 'up',
      icon: Clock,
      color: 'orange'
    }
  ]);

  const [queryData, setQueryData] = useState<ChartData[]>([
    { label: 'Mon', value: 120 },
    { label: 'Tue', value: 98 },
    { label: 'Wed', value: 145 },
    { label: 'Thu', value: 167 },
    { label: 'Fri', value: 189 },
    { label: 'Sat', value: 156 },
    { label: 'Sun', value: 134 }
  ]);

  const [topQueries, setTopQueries] = useState([
    { query: 'machine learning algorithms', count: 45, trend: 'up' },
    { query: 'data visualization techniques', count: 38, trend: 'up' },
    { query: 'neural network architectures', count: 32, trend: 'down' },
    { query: 'natural language processing', count: 29, trend: 'up' },
    { query: 'computer vision applications', count: 24, trend: 'up' }
  ]);

  const getColorClasses = (color: string) => {
    switch (color) {
      case 'blue':
        return {
          bg: 'bg-blue-50 dark:bg-blue-900/20',
          border: 'border-blue-200 dark:border-blue-800',
          icon: 'text-blue-600 dark:text-blue-400',
          text: 'text-blue-700 dark:text-blue-300'
        };
      case 'green':
        return {
          bg: 'bg-green-50 dark:bg-green-900/20',
          border: 'border-green-200 dark:border-green-800',
          icon: 'text-green-600 dark:text-green-400',
          text: 'text-green-700 dark:text-green-300'
        };
      case 'purple':
        return {
          bg: 'bg-purple-50 dark:bg-purple-900/20',
          border: 'border-purple-200 dark:border-purple-800',
          icon: 'text-purple-600 dark:text-purple-400',
          text: 'text-purple-700 dark:text-purple-300'
        };
      case 'orange':
        return {
          bg: 'bg-orange-50 dark:bg-orange-900/20',
          border: 'border-orange-200 dark:border-orange-800',
          icon: 'text-orange-600 dark:text-orange-400',
          text: 'text-orange-700 dark:text-orange-300'
        };
      default:
        return {
          bg: 'bg-gray-50 dark:bg-gray-900/20',
          border: 'border-gray-200 dark:border-gray-800',
          icon: 'text-gray-600 dark:text-gray-400',
          text: 'text-gray-700 dark:text-gray-300'
        };
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Analytics Dashboard
          </h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Monitor system performance and usage metrics
          </p>
        </div>
        
        <div className="flex items-center space-x-4">
          <select className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white">
            <option>Last 7 days</option>
            <option>Last 30 days</option>
            <option>Last 90 days</option>
          </select>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {metrics.map((metric, index) => {
          const Icon = metric.icon;
          const colors = getColorClasses(metric.color);
          
          return (
            <motion.div
              key={metric.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className={`p-6 rounded-lg border ${colors.bg} ${colors.border}`}
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                    {metric.title}
                  </p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    {metric.value}
                  </p>
                </div>
                <div className={`p-3 rounded-full ${colors.bg}`}>
                  <Icon className={`h-6 w-6 ${colors.icon}`} />
                </div>
              </div>
              
              <div className="mt-4 flex items-center">
                {metric.trend === 'up' ? (
                  <TrendingUp className="h-4 w-4 text-green-500" />
                ) : (
                  <TrendingDown className="h-4 w-4 text-red-500" />
                )}
                <span className={`ml-1 text-sm font-medium ${
                  metric.trend === 'up' ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
                }`}>
                  {Math.abs(metric.change)}%
                </span>
                <span className="ml-1 text-sm text-gray-500 dark:text-gray-400">
                  vs last period
                </span>
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Charts and Tables */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Query Volume Chart */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6"
        >
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Query Volume (Last 7 Days)
          </h3>
          
          <div className="space-y-4">
            {queryData.map((item, index) => (
              <div key={item.label} className="flex items-center space-x-3">
                <div className="w-12 text-sm text-gray-600 dark:text-gray-400">
                  {item.label}
                </div>
                <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <motion.div
                    className="bg-blue-500 h-2 rounded-full"
                    initial={{ width: 0 }}
                    animate={{ width: `${(item.value / Math.max(...queryData.map(d => d.value))) * 100}%` }}
                    transition={{ delay: 0.5 + index * 0.1, duration: 0.8 }}
                  />
                </div>
                <div className="w-12 text-sm text-gray-900 dark:text-white text-right">
                  {item.value}
                </div>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Top Queries */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6"
        >
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Top Search Queries
          </h3>
          
          <div className="space-y-4">
            {topQueries.map((item, index) => (
              <motion.div
                key={item.query}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 + index * 0.1 }}
                className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 rounded-md"
              >
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                    {item.query}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {item.count} searches
                  </p>
                </div>
                
                <div className="flex items-center space-x-2">
                  {item.trend === 'up' ? (
                    <TrendingUp className="h-4 w-4 text-green-500" />
                  ) : (
                    <TrendingDown className="h-4 w-4 text-red-500" />
                  )}
                  <span className="text-sm font-medium text-gray-600 dark:text-gray-400">
                    #{index + 1}
                  </span>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* System Status */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8 }}
      >
        <SystemStatus />
      </motion.div>
    </div>
  );
};

export default AnalyticsPage; 