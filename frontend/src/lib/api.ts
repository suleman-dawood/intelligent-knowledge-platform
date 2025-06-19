/**
 * API client for communicating with the Knowledge Platform API.
 * Provides methods for data fetching, search, and task management.
 */

import { useState, useEffect } from 'react';

// API base URL from environment or default
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3100';

// Define common types
export interface Task {
  id: string;
  type: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  result?: any;
  error?: string;
  created_at: string;
  completed_at?: string;
}

export interface SearchResult {
  id: string;
  title: string;
  content: string;
  summary?: string;
  source: string;
  score: number;
  type: string;
  entities: Array<{
    name: string;
    type: string;
    confidence: number;
  }>;
  metadata?: Record<string, any>;
  timestamp?: string;
  tags?: string[];
  url?: string;
}

export interface Entity {
  id: string;
  name: string;
  type: string;
  properties: Record<string, any>;
}

export interface GraphData {
  nodes: Array<{
    id: string;
    label: string;
    type: string;
    properties: Record<string, any>;
  }>;
  edges: Array<{
    source: string;
    target: string;
    label: string;
    properties: Record<string, any>;
  }>;
}

export interface KnowledgeGraphNode {
  id: string;
  label: string;
  type: string;
  properties: Record<string, any>;
}

export interface KnowledgeGraphEdge {
  source: string;
  target: string;
  label: string;
  properties: Record<string, any>;
}

export interface KnowledgeGraph {
  nodes: KnowledgeGraphNode[];
  edges: KnowledgeGraphEdge[];
}

// Generic fetch wrapper with error handling
async function fetchApi<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }

    return await response.json() as T;
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
}

// Task-related API methods
export async function submitTask(type: string, data: Record<string, any>): Promise<string> {
  const response = await fetchApi<{ task_id: string }>('/tasks', {
    method: 'POST',
    body: JSON.stringify({ task_type: type, task_data: data }),
  });
  
  return response.task_id;
}

export async function getTaskStatus(taskId: string): Promise<Task> {
  return fetchApi<Task>(`/tasks/${taskId}`);
}

// Legacy API methods - replaced by ApiService class

export async function getEntityDetails(entityId: string): Promise<Entity> {
  return fetchApi<Entity>(`/entities/${entityId}`);
}

// Hook for managing task submission and status tracking
export function useTaskSubmission() {
  const [taskId, setTaskId] = useState<string | null>(null);
  const [status, setStatus] = useState<Task['status'] | null>(null);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // Submit a new task
  const submit = async (type: string, data: Record<string, any>) => {
    setLoading(true);
    setError(null);
    
    try {
      const id = await submitTask(type, data);
      setTaskId(id);
      setStatus('pending');
      return id;
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Poll task status if we have a task ID
  useEffect(() => {
    if (!taskId || status === 'completed' || status === 'failed') {
      return;
    }

    const interval = setInterval(async () => {
      try {
        const taskInfo = await getTaskStatus(taskId);
        setStatus(taskInfo.status);
        
        if (taskInfo.status === 'completed') {
          setResult(taskInfo.result);
        } else if (taskInfo.status === 'failed') {
          setError(taskInfo.error || 'Task failed with no error message');
        }
        
        if (taskInfo.status === 'completed' || taskInfo.status === 'failed') {
          clearInterval(interval);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : String(err));
        clearInterval(interval);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [taskId, status]);

  return { submit, taskId, status, result, error, loading };
}

class ApiService {
  private baseUrl: string;
  
  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3100';
  }

  async searchKnowledge(query: string, options: {
    limit?: number;
    offset?: number;
    filters?: Record<string, any>;
  } = {}): Promise<SearchResult[]> {
    try {
      const params = new URLSearchParams({
        q: query,
        limit: (options.limit || 10).toString(),
        offset: (options.offset || 0).toString()
      });

      // Add filters if provided
      if (options.filters) {
        Object.entries(options.filters).forEach(([key, value]) => {
          params.append(`filter_${key}`, value.toString());
        });
      }

      const response = await fetch(`${this.baseUrl}/search?${params}`);
      
      if (!response.ok) {
        throw new Error(`Search failed: ${response.status} ${response.statusText}`);
      }

      const results = await response.json();
      return Array.isArray(results) ? results : [];
    } catch (error) {
      console.error('Search error:', error);
      
      // Return fallback mock results for development
      return this.getMockSearchResults(query);
    }
  }

  async getKnowledgeGraph(options: {
    nodeId?: string;
    depth?: number;
    maxNodes?: number;
  } = {}): Promise<KnowledgeGraph> {
    try {
      const params = new URLSearchParams();
      
      if (options.nodeId) params.append('nodeId', options.nodeId);
      if (options.depth) params.append('depth', options.depth.toString());
      if (options.maxNodes) params.append('maxNodes', options.maxNodes.toString());

      const endpoint = options.nodeId 
        ? `/graph/node/${options.nodeId}?${params}`
        : `/graph/overview?${params}`;

      const response = await fetch(`${this.baseUrl}${endpoint}`);
      
      if (!response.ok) {
        throw new Error(`Graph fetch failed: ${response.status} ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Knowledge graph error:', error);
      return { nodes: [], edges: [] };
    }
  }

  async submitContent(data: {
    type: string;
    title: string;
    content?: string;
    url?: string;
    fileId?: string;
    tags?: string[];
  }): Promise<{ taskId: string; status: string }> {
    try {
      const response = await fetch(`${this.baseUrl}/api/process-content`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Content submission failed');
      }

      return await response.json();
    } catch (error) {
      console.error('Content submission error:', error);
      throw error;
    }
  }

  async getTaskStatus(taskId: string): Promise<{
    id: string;
    status: string;
    result?: any;
    error?: string;
  }> {
    try {
      const response = await fetch(`${this.baseUrl}/tasks/${taskId}`);
      
      if (!response.ok) {
        throw new Error(`Task status fetch failed: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Task status error:', error);
      throw error;
    }
  }

  async getSystemStatus(): Promise<{
    status: string;
    agents: Record<string, Record<string, number>>;
    tasks: Record<string, number>;
  }> {
    try {
      const response = await fetch(`${this.baseUrl}/status`);
      
      if (!response.ok) {
        throw new Error(`System status fetch failed: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('System status error:', error);
      return {
        status: 'unknown',
        agents: {},
        tasks: {}
      };
    }
  }

  private getMockSearchResults(query: string): SearchResult[] {
    const mockResults = [
      {
        id: '1',
        title: 'Understanding Knowledge Integration',
        content: 'Knowledge integration is the process of combining information from multiple sources to create comprehensive understanding...',
        source: 'research_paper',
        score: 0.95,
        type: 'academic',
        entities: [
          { name: 'Knowledge Integration', type: 'concept', confidence: 0.98 },
          { name: 'Information Systems', type: 'field', confidence: 0.85 }
        ]
      },
      {
        id: '2',
        title: 'Quantum Computing Fundamentals',
        content: 'Quantum computing leverages quantum mechanical phenomena to process information in ways classical computers cannot...',
        source: 'textbook',
        score: 0.88,
        type: 'educational',
        entities: [
          { name: 'Quantum Computing', type: 'technology', confidence: 0.99 },
          { name: 'Quantum Mechanics', type: 'science', confidence: 0.92 }
        ]
      },
      {
        id: '3',
        title: 'Artificial Intelligence in Modern Applications',
        content: 'AI technologies are transforming industries through machine learning, natural language processing, and computer vision...',
        source: 'article',
        score: 0.82,
        type: 'article',
        entities: [
          { name: 'Artificial Intelligence', type: 'technology', confidence: 0.97 },
          { name: 'Machine Learning', type: 'method', confidence: 0.89 }
        ]
      }
    ];

    // Filter results based on query relevance
    return mockResults.filter(result => 
      result.title.toLowerCase().includes(query.toLowerCase()) ||
      result.content.toLowerCase().includes(query.toLowerCase())
    ).slice(0, 10);
  }
}

export const apiService = new ApiService();

// Legacy exports for backward compatibility
export const searchKnowledge = (query: string) => apiService.searchKnowledge(query);
export const getKnowledgeGraph = (options?: any) => apiService.getKnowledgeGraph(options); 