'use client'

import { useState, useEffect, useRef } from 'react'
import dynamic from 'next/dynamic'
import Header from '@/components/Header'
import Footer from '@/components/Footer'
import SearchBox from '@/components/SearchBox'

// Import force graph with SSR disabled (it requires window access)
const ForceGraph = dynamic(() => import('@/components/ForceGraph'), { ssr: false })

// Sample knowledge graph data
const SAMPLE_GRAPH_DATA = {
  nodes: [
    { id: 'artificial_intelligence', label: 'Artificial Intelligence', type: 'concept', properties: { description: 'The simulation of human intelligence in machines' } },
    { id: 'machine_learning', label: 'Machine Learning', type: 'concept', properties: { description: 'A subset of AI focused on learning from data' } },
    { id: 'deep_learning', label: 'Deep Learning', type: 'concept', properties: { description: 'A subset of machine learning using neural networks' } },
    { id: 'neural_networks', label: 'Neural Networks', type: 'concept', properties: { description: 'Computing systems inspired by biological neural networks' } },
    { id: 'computer_vision', label: 'Computer Vision', type: 'concept', properties: { description: 'Field of AI that enables computers to interpret visual world' } },
    { id: 'nlp', label: 'Natural Language Processing', type: 'concept', properties: { description: 'Branch of AI focused on interactions between computers and human language' } },
    { id: 'reinforcement_learning', label: 'Reinforcement Learning', type: 'concept', properties: { description: 'Training models to make sequences of decisions' } },
    { id: 'supervised_learning', label: 'Supervised Learning', type: 'concept', properties: { description: 'Training with labeled data' } },
    { id: 'unsupervised_learning', label: 'Unsupervised Learning', type: 'concept', properties: { description: 'Finding patterns in unlabeled data' } },
    { id: 'tensorflow', label: 'TensorFlow', type: 'technology', properties: { description: 'Open-source machine learning framework' } },
    { id: 'pytorch', label: 'PyTorch', type: 'technology', properties: { description: 'Open-source machine learning library' } },
    { id: 'turing_alan', label: 'Alan Turing', type: 'person', properties: { description: 'British mathematician and computer scientist' } },
  ],
  edges: [
    { source: 'artificial_intelligence', target: 'machine_learning', label: 'includes', weight: 1.0, properties: {} },
    { source: 'machine_learning', target: 'deep_learning', label: 'includes', weight: 1.0, properties: {} },
    { source: 'machine_learning', target: 'supervised_learning', label: 'includes', weight: 1.0, properties: {} },
    { source: 'machine_learning', target: 'unsupervised_learning', label: 'includes', weight: 1.0, properties: {} },
    { source: 'machine_learning', target: 'reinforcement_learning', label: 'includes', weight: 1.0, properties: {} },
    { source: 'deep_learning', target: 'neural_networks', label: 'uses', weight: 1.0, properties: {} },
    { source: 'artificial_intelligence', target: 'computer_vision', label: 'includes', weight: 1.0, properties: {} },
    { source: 'artificial_intelligence', target: 'nlp', label: 'includes', weight: 1.0, properties: {} },
    { source: 'deep_learning', target: 'computer_vision', label: 'applied_to', weight: 0.8, properties: {} },
    { source: 'deep_learning', target: 'nlp', label: 'applied_to', weight: 0.8, properties: {} },
    { source: 'tensorflow', target: 'machine_learning', label: 'enables', weight: 0.9, properties: {} },
    { source: 'pytorch', target: 'machine_learning', label: 'enables', weight: 0.9, properties: {} },
    { source: 'turing_alan', target: 'artificial_intelligence', label: 'contributed_to', weight: 0.7, properties: {} },
  ]
}

export default function ExplorePage() {
  const [query, setQuery] = useState('')
  const [graphData, setGraphData] = useState(SAMPLE_GRAPH_DATA)
  const [selectedNode, setSelectedNode] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [filters, setFilters] = useState({
    nodeTypes: ['concept', 'person', 'technology'],
    relationTypes: ['all'],
    maxDepth: 2
  })
  
  // Handle search
  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim()) return
    
    setIsLoading(true)
    
    try {
      // In a real app, this would make an API call to get the knowledge graph data
      // For example:
      // const response = await fetch(`/api/knowledge-graph?query=${encodeURIComponent(query)}&depth=${filters.maxDepth}`)
      // const data = await response.json()
      // setGraphData(data)
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 800))
      
      // For demo purposes, just change the selected node based on the query
      const matchedNode = graphData.nodes.find(node => 
        node.label.toLowerCase().includes(query.toLowerCase())
      )
      
      if (matchedNode) {
        setSelectedNode(matchedNode)
      } else {
        alert('No matching nodes found. Try a different search term.')
      }
      
    } catch (error) {
      console.error('Error searching knowledge graph:', error)
    } finally {
      setIsLoading(false)
    }
  }
  
  // Handle filter changes
  const handleFilterChange = (filter: string, value: any) => {
    setFilters(prev => ({
      ...prev,
      [filter]: value
    }))
  }
  
  // Handle node click
  const handleNodeClick = (node: any) => {
    setSelectedNode(node)
  }
  
  // Filter the graph data based on selected filters
  const filteredGraphData = {
    nodes: graphData.nodes.filter(node => filters.nodeTypes.includes(node.type)),
    edges: graphData.edges.filter(edge => {
      const sourceNode = graphData.nodes.find(n => n.id === edge.source)
      const targetNode = graphData.nodes.find(n => n.id === edge.target)
      return (
        sourceNode && targetNode && 
        filters.nodeTypes.includes(sourceNode.type) && 
        filters.nodeTypes.includes(targetNode.type) &&
        (filters.relationTypes.includes('all') || filters.relationTypes.includes(edge.label))
      )
    })
  }
  
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      
      <main className="flex-grow bg-gray-50">
        <div className="bg-white shadow-sm">
          <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
            <h1 className="text-2xl font-bold leading-7 text-gray-900 sm:truncate sm:leading-9">
              Knowledge Graph Explorer
            </h1>
            <p className="mt-1 text-sm text-gray-500">
              Discover connections between concepts, entities, and ideas.
            </p>
            
            <div className="mt-4 flex flex-col md:flex-row gap-4">
              <div className="w-full md:w-2/3">
                <SearchBox 
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onSubmit={handleSearch}
                  placeholder="Search for a concept or entity (e.g., 'machine learning')"
                  fullWidth
                />
              </div>
              <div className="w-full md:w-1/3">
                <select 
                  className="input h-full"
                  value={filters.maxDepth}
                  onChange={(e) => handleFilterChange('maxDepth', parseInt(e.target.value))}
                >
                  <option value={1}>Depth: 1</option>
                  <option value={2}>Depth: 2</option>
                  <option value={3}>Depth: 3</option>
                </select>
              </div>
            </div>
            
            <div className="mt-4 flex flex-wrap gap-2">
              <span className="text-xs font-medium text-gray-500">Node Types:</span>
              {['concept', 'person', 'technology', 'organization', 'topic'].map(type => (
                <label key={type} className="inline-flex items-center">
                  <input
                    type="checkbox"
                    className="rounded border-gray-300 text-primary-600 focus:ring-primary-500 h-4 w-4"
                    checked={filters.nodeTypes.includes(type)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        handleFilterChange('nodeTypes', [...filters.nodeTypes, type])
                      } else {
                        handleFilterChange('nodeTypes', filters.nodeTypes.filter(t => t !== type))
                      }
                    }}
                  />
                  <span className="ml-1 text-xs text-gray-700 capitalize">{type}</span>
                </label>
              ))}
            </div>
          </div>
        </div>
        
        <div className="graph-container relative h-[calc(100vh-280px)] min-h-[500px] border-b border-gray-200">
          {isLoading ? (
            <div className="absolute inset-0 flex items-center justify-center bg-gray-50 bg-opacity-75">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
                <p className="mt-2 text-sm text-gray-600">Loading knowledge graph...</p>
              </div>
            </div>
          ) : (
            <ForceGraph 
              data={filteredGraphData} 
              onNodeClick={handleNodeClick} 
              selectedNode={selectedNode}
            />
          )}
        </div>
        
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
          <div className="bg-white shadow rounded-lg">
            <div className="px-6 py-5 border-b border-gray-200">
              <h3 className="text-lg font-medium leading-6 text-gray-900">
                {selectedNode ? selectedNode.label : 'Select a node to see details'}
              </h3>
            </div>
            
            {selectedNode ? (
              <div className="px-6 py-5">
                <dl className="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Type</dt>
                    <dd className="mt-1 text-sm text-gray-900 capitalize">{selectedNode.type}</dd>
                  </div>
                  
                  <div>
                    <dt className="text-sm font-medium text-gray-500">ID</dt>
                    <dd className="mt-1 text-sm text-gray-900">{selectedNode.id}</dd>
                  </div>
                  
                  <div className="sm:col-span-2">
                    <dt className="text-sm font-medium text-gray-500">Description</dt>
                    <dd className="mt-1 text-sm text-gray-900">
                      {selectedNode.properties?.description || 'No description available.'}
                    </dd>
                  </div>
                  
                  <div className="sm:col-span-2">
                    <dt className="text-sm font-medium text-gray-500">Connections</dt>
                    <dd className="mt-1 text-sm text-gray-900">
                      <ul className="divide-y divide-gray-200">
                        {graphData.edges
                          .filter(edge => edge.source === selectedNode.id || edge.target === selectedNode.id)
                          .map((edge, idx) => {
                            const isSource = edge.source === selectedNode.id
                            const connectedNodeId = isSource ? edge.target : edge.source
                            const connectedNode = graphData.nodes.find(n => n.id === connectedNodeId)
                            
                            return (
                              <li key={idx} className="py-2">
                                <div className="flex items-center">
                                  <span className="text-xs text-gray-500">
                                    {isSource ? 'Outgoing:' : 'Incoming:'}
                                  </span>
                                  <span className="mx-1 text-xs text-primary-600 capitalize">
                                    {edge.label}
                                  </span>
                                  <button
                                    type="button"
                                    className="ml-1 text-sm font-medium text-primary-600 hover:text-primary-800"
                                    onClick={() => connectedNode && setSelectedNode(connectedNode)}
                                  >
                                    {connectedNode?.label}
                                  </button>
                                </div>
                              </li>
                            )
                          })}
                      </ul>
                    </dd>
                  </div>
                </dl>
              </div>
            ) : (
              <div className="px-6 py-5 text-center text-gray-500 italic">
                Click on a node in the graph to view its details
              </div>
            )}
          </div>
        </div>
      </main>
      
      <Footer />
    </div>
  )
} 