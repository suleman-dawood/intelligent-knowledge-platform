'use client'

import React, { useState, useEffect } from 'react'
import { getKnowledgeGraph, getEntityDetails, GraphData, Entity } from '../../lib/api'
import KnowledgeGraph from '../../components/KnowledgeGraph'
import Link from 'next/link'

export default function ExplorePage() {
  const [graphData, setGraphData] = useState<GraphData | null>(null)
  const [selectedNode, setSelectedNode] = useState<string | null>(null)
  const [entityDetails, setEntityDetails] = useState<Entity | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [graphDepth, setGraphDepth] = useState(2)

  // Load initial graph data
  useEffect(() => {
    async function loadInitialGraph() {
      setLoading(true)
      setError(null)
      
      try {
        const data = await getKnowledgeGraph()
        setGraphData(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load knowledge graph')
        console.error(err)
      } finally {
        setLoading(false)
      }
    }
    
    loadInitialGraph()
  }, [])
  
  // Handle node selection
  const handleNodeClick = async (nodeId: string) => {
    setSelectedNode(nodeId)
    setLoading(true)
    
    try {
      // Get detailed entity information
      const details = await getEntityDetails(nodeId)
      setEntityDetails(details)
      
      // Fetch subgraph centered on this node
      const subgraph = await getKnowledgeGraph(nodeId, graphDepth)
      setGraphData(subgraph)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load entity details')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }
  
  // Update graph depth
  const handleDepthChange = async (newDepth: number) => {
    setGraphDepth(newDepth)
    
    if (selectedNode) {
      setLoading(true)
      try {
        const subgraph = await getKnowledgeGraph(selectedNode, newDepth)
        setGraphData(subgraph)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to update graph depth')
      } finally {
        setLoading(false)
      }
    }
  }
  
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Knowledge Explorer</h1>
        
        <div className="flex items-center space-x-4">
          <Link 
            href="/search" 
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Search Knowledge
          </Link>
          
          <div className="flex items-center">
            <label htmlFor="depth" className="mr-2 text-sm">Graph Depth:</label>
            <select
              id="depth"
              className="border border-gray-300 rounded px-2 py-1"
              value={graphDepth}
              onChange={(e) => handleDepthChange(Number(e.target.value))}
            >
              {[1, 2, 3, 4].map(depth => (
                <option key={depth} value={depth}>{depth}</option>
              ))}
            </select>
          </div>
        </div>
      </div>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}
      
      <div className="flex flex-col lg:flex-row gap-6">
        {/* Main visualization area */}
        <div className="lg:w-3/4 bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <KnowledgeGraph 
            data={graphData || undefined}
            onNodeClick={handleNodeClick}
            loading={loading}
            height="600px"
          />
        </div>
        
        {/* Entity details sidebar */}
        <div className="lg:w-1/4">
          {selectedNode && entityDetails ? (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
              <h2 className="text-xl font-semibold mb-2 text-blue-600">
                {entityDetails.name}
              </h2>
              
              <div className="mb-4 inline-block px-2 py-1 bg-gray-100 text-xs rounded">
                {entityDetails.type}
              </div>
              
              <div className="space-y-3 mt-4">
                {entityDetails.properties && Object.entries(entityDetails.properties)
                  .filter(([key]) => key !== 'id' && key !== 'name' && key !== 'type')
                  .map(([key, value]) => (
                    <div key={key} className="border-b border-gray-100 pb-2">
                      <div className="text-xs font-medium text-gray-500">{key}</div>
                      <div className="text-sm">{String(value)}</div>
                    </div>
                  ))
                }
              </div>
              
              <div className="mt-6 pt-4 border-t border-gray-100">
                <Link 
                  href={`/explore/entity/${entityDetails.id}`}
                  className="text-blue-600 hover:underline text-sm"
                >
                  View detailed profile →
                </Link>
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 text-center py-12">
              <p className="text-gray-500">
                Select a node in the graph to view its details
              </p>
            </div>
          )}
          
          <div className="mt-6 bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <h3 className="font-medium mb-3">Legend</h3>
            
            <div className="space-y-2">
              {Object.entries({
                Person: '#4285F4',
                Organization: '#34A853',
                Location: '#FBBC05',
                Concept: '#EA4335',
                Event: '#8F44AD',
                Document: '#3498DB'
              }).map(([type, color]) => (
                <div key={type} className="flex items-center">
                  <div 
                    className="w-4 h-4 rounded-full mr-2" 
                    style={{ backgroundColor: color }}
                  ></div>
                  <span className="text-sm">{type}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
} 