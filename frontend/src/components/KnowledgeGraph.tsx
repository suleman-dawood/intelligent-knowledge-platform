import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { GraphData } from '../lib/api';
import { useWebSocketEvent } from '../lib/websocket';

// Styling for nodes and links
const NODE_COLORS: Record<string, string> = {
  Person: '#4285F4',
  Organization: '#34A853',
  Location: '#FBBC05',
  Concept: '#EA4335',
  Event: '#8F44AD',
  Document: '#3498DB',
  default: '#7F8C8D'
};

const NODE_SIZES: Record<string, number> = {
  Person: 12,
  Organization: 14,
  Location: 10,
  Concept: 8,
  Event: 10,
  Document: 9,
  default: 7
};

// Extended node type with D3 simulation properties
interface SimulationNode {
  id: string;
  label: string; 
  type: string;
  properties: Record<string, any>;
  x?: number;
  y?: number;
  fx?: number | null;
  fy?: number | null;
}

// Extended edge type with D3 simulation properties
interface SimulationLink {
  source: string | SimulationNode;
  target: string | SimulationNode;
  label: string;
  properties: Record<string, any>;
}

interface KnowledgeGraphProps {
  data?: GraphData;
  onNodeClick?: (nodeId: string) => void;
  loading?: boolean;
  height?: number | string;
  width?: number | string;
}

const KnowledgeGraph: React.FC<KnowledgeGraphProps> = ({
  data,
  onNodeClick,
  loading = false,
  height = '600px',
  width = '100%'
}) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);
  
  // Subscribe to real-time graph updates
  const { data: wsData } = useWebSocketEvent<GraphData>('graph.changed');
  
  // Merge WebSocket data with prop data if available
  const graphData = wsData || data;
  
  // Set up the force simulation and visualization
  useEffect(() => {
    if (!graphData || !svgRef.current) return;
    
    // Clear previous graph
    d3.select(svgRef.current).selectAll("*").remove();
    
    const svg = d3.select(svgRef.current);
    const width = +svg.style('width').replace('px', '');
    const height = +svg.style('height').replace('px', '');
    
    // Create the simulation
    const simulation = d3.forceSimulation<SimulationNode>()
      .force("link", d3.forceLink<SimulationNode, SimulationLink>().id(d => d.id).distance(100))
      .force("charge", d3.forceManyBody().strength(-300))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collide", d3.forceCollide().radius(30));
    
    // Create container for zoom/pan
    const g = svg.append("g");
    
    // Add zoom behavior
    const zoom = d3.zoom()
      .scaleExtent([0.1, 4])
      .on("zoom", (event) => {
        g.attr("transform", event.transform);
      });
    
    svg.call(zoom as any);
    
    // Create links
    const link = g.append("g")
      .attr("class", "links")
      .selectAll("line")
      .data(graphData.edges)
      .enter().append("line")
      .attr("stroke", "#999")
      .attr("stroke-opacity", 0.6)
      .attr("stroke-width", 1.5);
    
    // Create link labels
    const linkText = g.append("g")
      .attr("class", "link-labels")
      .selectAll("text")
      .data(graphData.edges)
      .enter().append("text")
      .attr("font-size", "8px")
      .attr("text-anchor", "middle")
      .attr("dy", "-5px")
      .text(d => d.label);
    
    // Create nodes
    const node = g.append("g")
      .attr("class", "nodes")
      .selectAll("circle")
      .data(graphData.nodes)
      .enter().append("circle")
      .attr("r", d => NODE_SIZES[d.type] || NODE_SIZES.default)
      .attr("fill", d => NODE_COLORS[d.type] || NODE_COLORS.default)
      .attr("stroke", "#fff")
      .attr("stroke-width", 1.5)
      .on("click", (event, d) => {
        if (onNodeClick) {
          onNodeClick(d.id);
        }
      })
      .on("mouseover", (event, d) => {
        setHoveredNode(d.id);
      })
      .on("mouseout", () => {
        setHoveredNode(null);
      })
      .call(d3.drag<SVGCircleElement, SimulationNode>()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended) as any);
    
    // Create node labels
    const nodeText = g.append("g")
      .attr("class", "node-labels")
      .selectAll("text")
      .data(graphData.nodes)
      .enter().append("text")
      .attr("font-size", "10px")
      .attr("text-anchor", "middle")
      .attr("dy", "0.35em")
      .attr("dx", d => (NODE_SIZES[d.type] || NODE_SIZES.default) + 7)
      .text(d => d.label);
    
    // Set up simulation
    simulation.nodes(graphData.nodes as unknown as SimulationNode[]);
    (simulation.force("link") as d3.ForceLink<SimulationNode, SimulationLink>)
      .links(graphData.edges.map(edge => ({
        ...edge,
        source: typeof edge.source === 'string' ? edge.source : (edge.source as any).id,
        target: typeof edge.target === 'string' ? edge.target : (edge.target as any).id
      })));
    
    simulation.on("tick", () => {
      link
        .attr("x1", d => {
          const source = typeof d.source === 'string' 
            ? simulation.nodes().find(n => n.id === d.source) 
            : d.source as SimulationNode;
          return source?.x || 0;
        })
        .attr("y1", d => {
          const source = typeof d.source === 'string' 
            ? simulation.nodes().find(n => n.id === d.source) 
            : d.source as SimulationNode;
          return source?.y || 0;
        })
        .attr("x2", d => {
          const target = typeof d.target === 'string' 
            ? simulation.nodes().find(n => n.id === d.target) 
            : d.target as SimulationNode;
          return target?.x || 0;
        })
        .attr("y2", d => {
          const target = typeof d.target === 'string' 
            ? simulation.nodes().find(n => n.id === d.target) 
            : d.target as SimulationNode;
          return target?.y || 0;
        });
      
      node
        .attr("cx", d => (d as unknown as SimulationNode).x || 0)
        .attr("cy", d => (d as unknown as SimulationNode).y || 0);
      
      nodeText
        .attr("x", d => (d as unknown as SimulationNode).x || 0)
        .attr("y", d => (d as unknown as SimulationNode).y || 0);
      
      linkText
        .attr("x", d => {
          const source = typeof d.source === 'string' 
            ? simulation.nodes().find(n => n.id === d.source) 
            : d.source as SimulationNode;
          const target = typeof d.target === 'string' 
            ? simulation.nodes().find(n => n.id === d.target) 
            : d.target as SimulationNode;
          return ((source?.x || 0) + (target?.x || 0)) / 2;
        })
        .attr("y", d => {
          const source = typeof d.source === 'string' 
            ? simulation.nodes().find(n => n.id === d.source) 
            : d.source as SimulationNode;
          const target = typeof d.target === 'string' 
            ? simulation.nodes().find(n => n.id === d.target) 
            : d.target as SimulationNode;
          return ((source?.y || 0) + (target?.y || 0)) / 2;
        });
    });
    
    // Drag functions
    function dragstarted(event: d3.D3DragEvent<SVGCircleElement, SimulationNode, SimulationNode>, d: SimulationNode) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }
    
    function dragged(event: d3.D3DragEvent<SVGCircleElement, SimulationNode, SimulationNode>, d: SimulationNode) {
      d.fx = event.x;
      d.fy = event.y;
    }
    
    function dragended(event: d3.D3DragEvent<SVGCircleElement, SimulationNode, SimulationNode>, d: SimulationNode) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }
    
    // Initial zoom to fit
    const bounds = g.node()?.getBBox();
    if (bounds) {
      const dx = bounds.width;
      const dy = bounds.height;
      const x = bounds.x + bounds.width / 2;
      const y = bounds.y + bounds.height / 2;
      const scale = 0.9 / Math.max(dx / width, dy / height);
      const translate = [width / 2 - scale * x, height / 2 - scale * y];
      
      svg.transition()
        .duration(750)
        .call(zoom.transform as any, d3.zoomIdentity
          .translate(translate[0], translate[1])
          .scale(scale));
    }
    
    return () => {
      simulation.stop();
    };
  }, [graphData, onNodeClick]);
  
  // Find the hovered node details if one is selected
  const hoveredNodeDetails = hoveredNode 
    ? graphData?.nodes.find(n => n.id === hoveredNode)
    : null;
  
  return (
    <div style={{ position: 'relative', width, height }}>
      {loading && (
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: 'rgba(255, 255, 255, 0.7)',
          zIndex: 10
        }}>
          <div>Loading knowledge graph...</div>
        </div>
      )}
      
      <svg 
        ref={svgRef} 
        style={{ width: '100%', height: '100%' }}
      />
      
      {hoveredNodeDetails && (
        <div style={{
          position: 'absolute',
          bottom: '10px',
          right: '10px',
          padding: '10px',
          backgroundColor: 'rgba(255, 255, 255, 0.9)',
          border: '1px solid #ddd',
          borderRadius: '4px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          maxWidth: '300px',
          zIndex: 20
        }}>
          <h4 style={{ margin: '0 0 8px' }}>{hoveredNodeDetails.label}</h4>
          <p style={{ margin: '0 0 4px' }}><strong>Type:</strong> {hoveredNodeDetails.type}</p>
          {hoveredNodeDetails.properties && Object.entries(hoveredNodeDetails.properties)
            .filter(([key]) => key !== 'id' && key !== 'label' && key !== 'type')
            .map(([key, value]) => (
              <p key={key} style={{ margin: '0 0 4px' }}>
                <strong>{key}:</strong> {String(value)}
              </p>
            ))
          }
        </div>
      )}
    </div>
  );
};

export default KnowledgeGraph; 