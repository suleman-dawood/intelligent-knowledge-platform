'use client'
import { useRef, useEffect } from 'react'
import ForceGraph2D from 'react-force-graph-2d'

interface Node {
  id: string
  label: string
  type: string
  properties: {
    [key: string]: any
  }
  // Add optional position properties that get set by the force graph
  x?: number
  y?: number
  vx?: number
  vy?: number
  fx?: number
  fy?: number
}

interface Edge {
  source: string
  target: string
  label: string
  weight: number
  properties: {
    [key: string]: any
  }
}

interface GraphData {
  nodes: Node[]
  edges: Edge[]
}

interface ForceGraphProps {
  data: GraphData
  onNodeClick: (node: Node) => void
  selectedNode: Node | null
}

// Extended node type for the force graph (includes color and other properties)
interface ForceGraphNode extends Node {
  color: string
  borderWidth?: number
}

// Link type for the force graph
interface ForceGraphLink {
  source: string
  target: string
  label: string
  weight: number
}

const NODE_COLORS: { [key: string]: string } = {
  concept: '#3388cc',
  person: '#ff7700',
  technology: '#33cc77',
  organization: '#cc3388',
  topic: '#ffbb33',
}

export default function ForceGraph({ data, onNodeClick, selectedNode }: ForceGraphProps) {
  const graphRef = useRef<any>(null)

  // Convert the data to the format expected by react-force-graph
  const graphData = {
    nodes: data.nodes.map((node): ForceGraphNode => ({
      ...node,
      color: NODE_COLORS[node.type] || '#999999',
      // Highlight the selected node
      ...(selectedNode && node.id === selectedNode.id && {
        color: '#ff0000',
        borderWidth: 2,
      })
    })),
    links: data.edges.map((edge): ForceGraphLink => ({
      source: edge.source,
      target: edge.target,
      label: edge.label,
      weight: edge.weight
    }))
  }

  // Focus on the selected node
  useEffect(() => {
    if (selectedNode && graphRef.current) {
      const nodeObject = graphData.nodes.find(node => node.id === selectedNode.id)
      if (nodeObject && nodeObject.x !== undefined && nodeObject.y !== undefined) {
        graphRef.current.centerAt(
          nodeObject.x,
          nodeObject.y,
          1000
        )
        graphRef.current.zoom(2, 1000)
      }
    }
  }, [selectedNode]) // Removed graphData.nodes dependency to prevent unnecessary re-runs

  return (
    <ForceGraph2D
      ref={graphRef}
      graphData={graphData}
      nodeLabel={(node: ForceGraphNode) => `${node.label} (${node.type})`}
      linkLabel={(link: ForceGraphLink) => link.label}
      nodeColor={(node: ForceGraphNode) => node.color}
      linkWidth={(link: ForceGraphLink) => link.weight ? link.weight * 2 : 1}
      nodeRelSize={6}
      linkDirectionalArrowLength={3}
      linkDirectionalArrowRelPos={1}
      linkDirectionalParticles={2}
      linkDirectionalParticleSpeed={(d: ForceGraphLink) => d.weight * 0.01}
      onNodeClick={onNodeClick}
      cooldownTicks={100}
      onEngineStop={() => console.log('Graph rendering complete')}
      nodeCanvasObjectMode={() => 'after'}
      nodeCanvasObject={(node: ForceGraphNode, ctx: CanvasRenderingContext2D, globalScale: number) => {
        const label = node.label
        const fontSize = 12/globalScale
        ctx.font = `${fontSize}px Sans-Serif`
        ctx.textAlign = 'center'
        ctx.textBaseline = 'middle'
        ctx.fillStyle = 'rgba(255, 255, 255, 0.8)'
        
        // Draw a background for the text
        const textWidth = ctx.measureText(label).width
        const bckgDimensions = [textWidth + 6, fontSize + 4].map(n => n) as [number, number]
        ctx.fillRect(
          (node.x || 0) - bckgDimensions[0] / 2,
          (node.y || 0) - bckgDimensions[1] / 2,
          ...bckgDimensions
        )
        
        // Draw the text
        ctx.fillStyle = '#333333'
        ctx.fillText(label, node.x || 0, node.y || 0)
      }}
    />
  )
}