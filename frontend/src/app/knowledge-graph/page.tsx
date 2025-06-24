'use client';

import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import {
  MagnifyingGlassIcon,
  AdjustmentsHorizontalIcon,
  PlayIcon,
  PauseIcon,
  ArrowsPointingOutIcon,
  ArrowsPointingInIcon,
  InformationCircleIcon,
} from '@heroicons/react/24/outline';

interface Node {
  id: string;
  label: string;
  type: 'concept' | 'document' | 'keyword' | 'topic';
  size: number;
  color: string;
  x?: number;
  y?: number;
}

interface Edge {
  id: string;
  source: string;
  target: string;
  weight: number;
  label?: string;
}

interface GraphData {
  nodes: Node[];
  edges: Edge[];
}

const KnowledgeGraphPage = () => {
  const svgRef = useRef<SVGSVGElement>(null);
  const [graphData, setGraphData] = useState<GraphData>({ nodes: [], edges: [] });
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [showControls, setShowControls] = useState(false);
  const [isSimulating, setIsSimulating] = useState(false);
  const [zoomLevel, setZoomLevel] = useState(1);
  const [viewBox, setViewBox] = useState('0 0 800 600');

  // Mock data generation
  useEffect(() => {
    const generateMockData = (): GraphData => {
      const nodes: Node[] = [
        { id: '1', label: 'Machine Learning', type: 'concept', size: 30, color: '#3b82f6' },
        { id: '2', label: 'Neural Networks', type: 'concept', size: 25, color: '#3b82f6' },
        { id: '3', label: 'Deep Learning', type: 'concept', size: 28, color: '#3b82f6' },
        { id: '4', label: 'AI Ethics', type: 'topic', size: 20, color: '#10b981' },
        { id: '5', label: 'Data Science', type: 'concept', size: 32, color: '#3b82f6' },
        { id: '6', label: 'Python', type: 'keyword', size: 22, color: '#f59e0b' },
        { id: '7', label: 'TensorFlow', type: 'keyword', size: 18, color: '#f59e0b' },
        { id: '8', label: 'Research Paper 1', type: 'document', size: 15, color: '#ef4444' },
        { id: '9', label: 'Research Paper 2', type: 'document', size: 15, color: '#ef4444' },
        { id: '10', label: 'Statistics', type: 'concept', size: 24, color: '#3b82f6' },
        { id: '11', label: 'Algorithms', type: 'concept', size: 26, color: '#3b82f6' },
        { id: '12', label: 'Computer Vision', type: 'topic', size: 20, color: '#10b981' },
        { id: '13', label: 'NLP', type: 'topic', size: 22, color: '#10b981' },
        { id: '14', label: 'Supervised Learning', type: 'concept', size: 18, color: '#3b82f6' },
        { id: '15', label: 'Unsupervised Learning', type: 'concept', size: 16, color: '#3b82f6' },
      ];

      const edges: Edge[] = [
        { id: 'e1', source: '1', target: '2', weight: 0.8, label: 'includes' },
        { id: 'e2', source: '1', target: '3', weight: 0.9, label: 'related to' },
        { id: 'e3', source: '2', target: '3', weight: 0.7, label: 'subset of' },
        { id: 'e4', source: '1', target: '5', weight: 0.6, label: 'overlaps with' },
        { id: 'e5', source: '5', target: '10', weight: 0.8, label: 'uses' },
        { id: 'e6', source: '1', target: '6', weight: 0.7, label: 'implemented in' },
        { id: 'e7', source: '3', target: '7', weight: 0.6, label: 'uses framework' },
        { id: 'e8', source: '1', target: '8', weight: 0.5, label: 'referenced in' },
        { id: 'e9', source: '3', target: '9', weight: 0.5, label: 'referenced in' },
        { id: 'e10', source: '1', target: '11', weight: 0.9, label: 'based on' },
        { id: 'e11', source: '3', target: '12', weight: 0.7, label: 'applied to' },
        { id: 'e12', source: '3', target: '13', weight: 0.7, label: 'applied to' },
        { id: 'e13', source: '1', target: '14', weight: 0.8, label: 'includes' },
        { id: 'e14', source: '1', target: '15', weight: 0.8, label: 'includes' },
        { id: 'e15', source: '1', target: '4', weight: 0.4, label: 'considers' },
      ];

      // Position nodes in a circular layout
      nodes.forEach((node, index) => {
        const angle = (index / nodes.length) * 2 * Math.PI;
        const radius = 200;
        node.x = 400 + radius * Math.cos(angle);
        node.y = 300 + radius * Math.sin(angle);
      });

      return { nodes, edges };
    };

    setIsLoading(true);
    setTimeout(() => {
      setGraphData(generateMockData());
      setIsLoading(false);
    }, 1000);
  }, []);

  const getNodeColor = (type: string) => {
    switch (type) {
      case 'concept': return '#3b82f6';
      case 'document': return '#ef4444';
      case 'keyword': return '#f59e0b';
      case 'topic': return '#10b981';
      default: return '#6b7280';
    }
  };

  const handleNodeClick = (node: Node) => {
    setSelectedNode(node);
  };

  const handleZoomIn = () => {
    setZoomLevel(prev => Math.min(prev * 1.2, 3));
  };

  const handleZoomOut = () => {
    setZoomLevel(prev => Math.max(prev / 1.2, 0.3));
  };

  const filteredNodes = graphData.nodes.filter(node =>
    node.label.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const filteredEdges = graphData.edges.filter(edge =>
    filteredNodes.some(node => node.id === edge.source) &&
    filteredNodes.some(node => node.id === edge.target)
  );

  return (
    <div className="min-h-screen bg-secondary-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-secondary-900 mb-2">Knowledge Graph</h1>
          <p className="text-secondary-600">Explore connections between concepts, documents, and topics</p>
        </div>

        {/* Controls */}
        <div className="bg-white rounded-2xl shadow-sm border border-secondary-200 p-6 mb-6">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
            {/* Search */}
            <div className="relative flex-1 max-w-md">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-secondary-400" />
              <input
                type="text"
                placeholder="Search nodes..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent text-gray-900 placeholder-gray-500"
              />
            </div>

            {/* Graph Controls */}
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setShowControls(!showControls)}
                className="flex items-center space-x-2 px-4 py-2 bg-secondary-100 text-secondary-700 rounded-lg hover:bg-secondary-200 transition-colors"
              >
                <AdjustmentsHorizontalIcon className="h-4 w-4" />
                <span>Controls</span>
              </button>
              
              <button
                onClick={() => setIsSimulating(!isSimulating)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                  isSimulating 
                    ? 'bg-error-100 text-error-700 hover:bg-error-200' 
                    : 'bg-success-100 text-success-700 hover:bg-success-200'
                }`}
              >
                {isSimulating ? <PauseIcon className="h-4 w-4" /> : <PlayIcon className="h-4 w-4" />}
                <span>{isSimulating ? 'Pause' : 'Simulate'}</span>
              </button>

              <div className="flex items-center space-x-1">
                <button
                  onClick={handleZoomOut}
                  className="p-2 bg-secondary-100 text-secondary-700 rounded-lg hover:bg-secondary-200 transition-colors"
                  title="Zoom Out"
                >
                  <ArrowsPointingInIcon className="h-4 w-4" />
                </button>
                <span className="text-sm text-secondary-600 min-w-[3rem] text-center">
                  {Math.round(zoomLevel * 100)}%
                </span>
                <button
                  onClick={handleZoomIn}
                  className="p-2 bg-secondary-100 text-secondary-700 rounded-lg hover:bg-secondary-200 transition-colors"
                  title="Zoom In"
                >
                  <ArrowsPointingOutIcon className="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>

          {/* Extended Controls */}
          {showControls && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mt-4 pt-4 border-t border-secondary-200"
            >
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    Node Size
                  </label>
                  <input
                    type="range"
                    min="0.5"
                    max="2"
                    step="0.1"
                    defaultValue="1"
                    className="w-full"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    Edge Thickness
                  </label>
                  <input
                    type="range"
                    min="0.5"
                    max="3"
                    step="0.1"
                    defaultValue="1"
                    className="w-full"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    Force Strength
                  </label>
                  <input
                    type="range"
                    min="0.1"
                    max="2"
                    step="0.1"
                    defaultValue="1"
                    className="w-full"
                  />
                </div>
              </div>
            </motion.div>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Graph Visualization */}
          <div className="lg:col-span-3">
            <div className="bg-white rounded-2xl shadow-sm border border-secondary-200 p-6">
              {isLoading ? (
                <div className="flex items-center justify-center h-96">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
                </div>
              ) : (
                <div className="relative">
                  <svg
                    ref={svgRef}
                    width="100%"
                    height="600"
                    viewBox={viewBox}
                    className="border border-secondary-200 rounded-lg bg-secondary-50"
                    style={{ transform: `scale(${zoomLevel})` }}
                  >
                    {/* Edges */}
                    {filteredEdges.map((edge) => {
                      const sourceNode = filteredNodes.find(n => n.id === edge.source);
                      const targetNode = filteredNodes.find(n => n.id === edge.target);
                      if (!sourceNode || !targetNode) return null;

                      return (
                        <g key={edge.id}>
                          <line
                            x1={sourceNode.x}
                            y1={sourceNode.y}
                            x2={targetNode.x}
                            y2={targetNode.y}
                            stroke="#cbd5e1"
                            strokeWidth={edge.weight * 2}
                            opacity={0.6}
                          />
                          {edge.label && (
                            <text
                              x={(sourceNode.x! + targetNode.x!) / 2}
                              y={(sourceNode.y! + targetNode.y!) / 2}
                              textAnchor="middle"
                              fontSize="10"
                              fill="#64748b"
                              className="pointer-events-none"
                            >
                              {edge.label}
                            </text>
                          )}
                        </g>
                      );
                    })}

                    {/* Nodes */}
                    {filteredNodes.map((node) => (
                      <g key={node.id}>
                        <circle
                          cx={node.x}
                          cy={node.y}
                          r={node.size}
                          fill={getNodeColor(node.type)}
                          stroke={selectedNode?.id === node.id ? '#f59e0b' : '#ffffff'}
                          strokeWidth={selectedNode?.id === node.id ? 3 : 2}
                          className="cursor-pointer hover:opacity-80 transition-opacity"
                          onClick={() => handleNodeClick(node)}
                        />
                        <text
                          x={node.x}
                          y={node.y! + node.size + 15}
                          textAnchor="middle"
                          fontSize="12"
                          fill="#1f2937"
                          className="pointer-events-none font-medium"
                        >
                          {node.label}
                        </text>
                      </g>
                    ))}
                  </svg>

                  {/* Legend */}
                  <div className="absolute top-4 right-4 bg-white rounded-lg shadow-sm border border-secondary-200 p-4">
                    <h4 className="font-medium text-secondary-900 mb-3">Legend</h4>
                    <div className="space-y-2">
                      <div className="flex items-center space-x-2">
                        <div className="w-4 h-4 rounded-full bg-blue-500"></div>
                        <span className="text-sm text-secondary-700">Concepts</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <div className="w-4 h-4 rounded-full bg-red-500"></div>
                        <span className="text-sm text-secondary-700">Documents</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <div className="w-4 h-4 rounded-full bg-amber-500"></div>
                        <span className="text-sm text-secondary-700">Keywords</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <div className="w-4 h-4 rounded-full bg-emerald-500"></div>
                        <span className="text-sm text-secondary-700">Topics</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Node Details Panel */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-2xl shadow-sm border border-secondary-200 p-6">
              <h3 className="font-semibold text-secondary-900 mb-4">Node Details</h3>
              
              {selectedNode ? (
                <div className="space-y-4">
                  <div>
                    <div className="flex items-center space-x-2 mb-2">
                      <div 
                        className="w-4 h-4 rounded-full"
                        style={{ backgroundColor: getNodeColor(selectedNode.type) }}
                      ></div>
                      <h4 className="font-medium text-secondary-900">{selectedNode.label}</h4>
                    </div>
                    <p className="text-sm text-secondary-600 capitalize">
                      Type: {selectedNode.type}
                    </p>
                    <p className="text-sm text-secondary-600">
                      Size: {selectedNode.size}
                    </p>
                  </div>

                  <div>
                    <h5 className="font-medium text-secondary-900 mb-2">Connections</h5>
                    <div className="space-y-1">
                      {filteredEdges
                        .filter(edge => edge.source === selectedNode.id || edge.target === selectedNode.id)
                        .map(edge => {
                          const connectedNodeId = edge.source === selectedNode.id ? edge.target : edge.source;
                          const connectedNode = filteredNodes.find(n => n.id === connectedNodeId);
                          return (
                            <div key={edge.id} className="text-sm text-secondary-600">
                              → {connectedNode?.label} ({edge.label})
                            </div>
                          );
                        })}
                    </div>
                  </div>

                  <div>
                    <h5 className="font-medium text-secondary-900 mb-2">Actions</h5>
                    <div className="space-y-2">
                      <button className="w-full px-3 py-2 text-sm bg-primary-100 text-primary-700 rounded-lg hover:bg-primary-200 transition-colors">
                        View Related Documents
                      </button>
                      <button className="w-full px-3 py-2 text-sm bg-secondary-100 text-secondary-700 rounded-lg hover:bg-secondary-200 transition-colors">
                        Expand Connections
                      </button>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <InformationCircleIcon className="h-12 w-12 text-secondary-400 mx-auto mb-4" />
                  <p className="text-secondary-600">Click on a node to view details</p>
                </div>
              )}
            </div>

            {/* Statistics */}
            <div className="bg-white rounded-2xl shadow-sm border border-secondary-200 p-6 mt-6">
              <h3 className="font-semibold text-secondary-900 mb-4">Graph Statistics</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-secondary-600">Total Nodes:</span>
                  <span className="font-medium text-secondary-900">{filteredNodes.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-secondary-600">Total Edges:</span>
                  <span className="font-medium text-secondary-900">{filteredEdges.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-secondary-600">Concepts:</span>
                  <span className="font-medium text-secondary-900">
                    {filteredNodes.filter(n => n.type === 'concept').length}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-secondary-600">Documents:</span>
                  <span className="font-medium text-secondary-900">
                    {filteredNodes.filter(n => n.type === 'document').length}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-secondary-600">Topics:</span>
                  <span className="font-medium text-secondary-900">
                    {filteredNodes.filter(n => n.type === 'topic').length}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default KnowledgeGraphPage; 