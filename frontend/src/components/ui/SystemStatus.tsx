'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Wifi, 
  WifiOff, 
  Server, 
  Database, 
  Activity,
  CheckCircle,
  AlertCircle,
  Clock
} from 'lucide-react';
import { useWebSocketEvent } from '../../lib/websocket';

interface SystemStatusProps {
  className?: string;
  compact?: boolean;
}

interface ServiceStatus {
  name: string;
  status: 'healthy' | 'degraded' | 'down';
  lastCheck: string;
  responseTime?: number;
}

const SystemStatus: React.FC<SystemStatusProps> = ({ 
  className = '', 
  compact = false 
}) => {
  const [systemHealth, setSystemHealth] = useState<{
    overall: 'healthy' | 'degraded' | 'down';
    services: ServiceStatus[];
    uptime: string;
    lastUpdate: string;
  }>({
    overall: 'healthy',
    services: [
      { name: 'API Server', status: 'healthy', lastCheck: new Date().toISOString() },
      { name: 'Database', status: 'healthy', lastCheck: new Date().toISOString() },
      { name: 'Message Queue', status: 'healthy', lastCheck: new Date().toISOString() },
      { name: 'Vector DB', status: 'healthy', lastCheck: new Date().toISOString() },
    ],
    uptime: '0m',
    lastUpdate: new Date().toISOString(),
  });
  
  // WebSocket connection status
  const { isConnected } = useWebSocketEvent('system.status');
  const { data: systemUpdate } = useWebSocketEvent('system.status');
  
  // Update system health from WebSocket
  useEffect(() => {
    if (systemUpdate) {
      setSystemHealth(prev => ({
        ...prev,
        ...systemUpdate,
        lastUpdate: new Date().toISOString(),
      }));
    }
  }, [systemUpdate]);
  
  // Fetch system status periodically
  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await fetch('/api/status');
        if (response.ok) {
          const data = await response.json();
          setSystemHealth(prev => ({
            ...prev,
            ...data,
            lastUpdate: new Date().toISOString(),
          }));
        }
      } catch (error) {
        console.error('Failed to fetch system status:', error);
      }
    };
    
    // Initial fetch
    fetchStatus();
    
    // Fetch every 30 seconds
    const interval = setInterval(fetchStatus, 30000);
    
    return () => clearInterval(interval);
  }, []);
  
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'degraded':
        return <AlertCircle className="h-4 w-4 text-yellow-500" />;
      case 'down':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-400" />;
    }
  };
  
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'text-green-600 dark:text-green-400';
      case 'degraded':
        return 'text-yellow-600 dark:text-yellow-400';
      case 'down':
        return 'text-red-600 dark:text-red-400';
      default:
        return 'text-gray-600 dark:text-gray-400';
    }
  };
  
  if (compact) {
    return (
      <div className={`flex items-center space-x-2 ${className}`}>
        <motion.div
          animate={{ 
            scale: isConnected ? 1 : 0.8,
            opacity: isConnected ? 1 : 0.6 
          }}
          transition={{ duration: 0.2 }}
        >
          {isConnected ? (
            <Wifi className="h-4 w-4 text-green-500" />
          ) : (
            <WifiOff className="h-4 w-4 text-red-500" />
          )}
        </motion.div>
        
        <div className="flex items-center space-x-1">
          {getStatusIcon(systemHealth.overall)}
          <span className={`text-xs font-medium ${getStatusColor(systemHealth.overall)}`}>
            {systemHealth.overall}
          </span>
        </div>
      </div>
    );
  }
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 ${className}`}
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
          System Status
        </h3>
        
        <div className="flex items-center space-x-3">
          {/* WebSocket Connection */}
          <div className="flex items-center space-x-1">
            <motion.div
              animate={{ 
                scale: isConnected ? 1 : 0.8,
                opacity: isConnected ? 1 : 0.6 
              }}
              transition={{ duration: 0.2 }}
            >
              {isConnected ? (
                <Wifi className="h-4 w-4 text-green-500" />
              ) : (
                <WifiOff className="h-4 w-4 text-red-500" />
              )}
            </motion.div>
            <span className="text-xs text-gray-600 dark:text-gray-400">
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
          
          {/* Overall Status */}
          <div className="flex items-center space-x-1">
            {getStatusIcon(systemHealth.overall)}
            <span className={`text-sm font-medium ${getStatusColor(systemHealth.overall)}`}>
              {systemHealth.overall.charAt(0).toUpperCase() + systemHealth.overall.slice(1)}
            </span>
          </div>
        </div>
      </div>
      
      {/* Services */}
      <div className="space-y-3">
        {systemHealth.services.map((service, index) => (
          <motion.div
            key={service.name}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className="flex items-center justify-between py-2 px-3 bg-gray-50 dark:bg-gray-700/50 rounded-md"
          >
            <div className="flex items-center space-x-3">
              <div className="flex-shrink-0">
                {service.name.includes('API') && <Server className="h-4 w-4 text-gray-600 dark:text-gray-400" />}
                {service.name.includes('Database') && <Database className="h-4 w-4 text-gray-600 dark:text-gray-400" />}
                {service.name.includes('Queue') && <Activity className="h-4 w-4 text-gray-600 dark:text-gray-400" />}
                {service.name.includes('Vector') && <Database className="h-4 w-4 text-gray-600 dark:text-gray-400" />}
              </div>
              
              <div>
                <div className="text-sm font-medium text-gray-900 dark:text-gray-100">
                  {service.name}
                </div>
                {service.responseTime && (
                  <div className="text-xs text-gray-500 dark:text-gray-400">
                    {service.responseTime}ms response
                  </div>
                )}
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              {getStatusIcon(service.status)}
              <span className={`text-xs font-medium ${getStatusColor(service.status)}`}>
                {service.status}
              </span>
            </div>
          </motion.div>
        ))}
      </div>
      
      {/* Footer */}
      <div className="mt-4 pt-3 border-t border-gray-200 dark:border-gray-600">
        <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
          <span>Uptime: {systemHealth.uptime}</span>
          <span>Last updated: {new Date(systemHealth.lastUpdate).toLocaleTimeString()}</span>
        </div>
      </div>
    </motion.div>
  );
};

export default SystemStatus; 