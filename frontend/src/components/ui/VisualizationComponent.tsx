'use client'

import React, { useEffect, useRef, useState } from 'react'
import { motion } from 'framer-motion'
import * as d3 from 'd3'

interface VisualizationProps {
  type: 'concept_map' | 'timeline' | 'hierarchy' | 'comparison' | 'statistics'
  data: any
  settings?: {
    width?: number
    height?: number
    interactive?: boolean
    theme?: 'light' | 'dark'
    layout?: string
  }
  onNodeClick?: (node: any) => void
  onEdgeClick?: (edge: any) => void
}

interface ConceptMapData {
  concepts: Array<{
    id: string
    label: string
    level: number
    importance: number
    position: { x: number; y: number }
    isRoot?: boolean
    x?: number
    y?: number
    fx?: number | null
    fy?: number | null
  }>
  relationships: Array<{
    source: string
    target: string
    label: string
    strength: number
  }>
}

interface TimelineData {
  events: Array<{
    id: string
    title: string
    date: string
    description: string
    category: string
  }>
}

interface HierarchyData {
  root: {
    id: string
    name: string
    children?: HierarchyData['root'][]
    value?: number
  }
}

interface ComparisonData {
  items: Array<{
    id: string
    name: string
    values: Record<string, number>
  }>
  metrics: string[]
}

interface StatisticsData {
  charts: Array<{
    type: 'bar' | 'line' | 'pie' | 'scatter'
    title: string
    data: Array<{ label: string; value: number }>
  }>
}

export default function VisualizationComponent({
  type,
  data,
  settings = {},
  onNodeClick,
  onEdgeClick
}: VisualizationProps) {
  const svgRef = useRef<SVGSVGElement>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const {
    width = 800,
    height = 600,
    interactive = true,
    theme = 'light',
    layout = 'force'
  } = settings

  useEffect(() => {
    if (!svgRef.current || !data) return

    setIsLoading(true)
    setError(null)

    try {
      const svg = d3.select(svgRef.current)
      svg.selectAll('*').remove() // Clear previous visualization

      switch (type) {
        case 'concept_map':
          renderConceptMap(svg, data as ConceptMapData)
          break
        case 'timeline':
          renderTimeline(svg, data as TimelineData)
          break
        case 'hierarchy':
          renderHierarchy(svg, data as HierarchyData)
          break
        case 'comparison':
          renderComparison(svg, data as ComparisonData)
          break
        case 'statistics':
          renderStatistics(svg, data as StatisticsData)
          break
        default:
          throw new Error(`Unsupported visualization type: ${type}`)
      }

      setIsLoading(false)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Visualization error')
      setIsLoading(false)
    }
  }, [type, data, width, height, theme, layout])

  const renderConceptMap = (svg: d3.Selection<SVGSVGElement, unknown, null, undefined>, data: ConceptMapData) => {
    // Type the nodes for d3 simulation
    const nodes = data.concepts.map(concept => ({
      ...concept,
      x: concept.position.x,
      y: concept.position.y
    }))

    const simulation = d3.forceSimulation(nodes as any)
      .force('link', d3.forceLink(data.relationships).id((d: any) => d.id).distance(100))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))

    // Create links
    const link = svg.append('g')
      .selectAll('line')
      .data(data.relationships)
      .enter().append('line')
      .attr('stroke', theme === 'dark' ? '#64748b' : '#94a3b8')
      .attr('stroke-width', (d: any) => Math.sqrt(d.strength * 5))
      .attr('stroke-opacity', 0.6)

    // Create nodes
    const node = svg.append('g')
      .selectAll('circle')
      .data(nodes)
      .enter().append('circle')
      .attr('r', (d: any) => 5 + d.importance * 15)
      .attr('fill', (d: any) => d.isRoot ? '#3b82f6' : '#10b981')
      .attr('stroke', theme === 'dark' ? '#1f2937' : '#ffffff')
      .attr('stroke-width', 2)
      .style('cursor', interactive ? 'pointer' : 'default')

    // Add labels
    const label = svg.append('g')
      .selectAll('text')
      .data(nodes)
      .enter().append('text')
      .text((d: any) => d.label)
      .attr('font-size', 12)
      .attr('font-family', 'system-ui, sans-serif')
      .attr('fill', theme === 'dark' ? '#f1f5f9' : '#1f2937')
      .attr('text-anchor', 'middle')
      .attr('dy', -20)

    // Add interactivity
    if (interactive) {
      node.on('click', (event, d) => onNodeClick?.(d))
      link.on('click', (event, d) => onEdgeClick?.(d))

      node.call(d3.drag<SVGCircleElement, any>()
        .on('start', (event, d) => {
          if (!event.active) simulation.alphaTarget(0.3).restart()
          d.fx = d.x
          d.fy = d.y
        })
        .on('drag', (event, d) => {
          d.fx = event.x
          d.fy = event.y
        })
        .on('end', (event, d) => {
          if (!event.active) simulation.alphaTarget(0)
          d.fx = null
          d.fy = null
        }))
    }

    // Update positions on simulation tick
    simulation.on('tick', () => {
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y)

      node
        .attr('cx', (d: any) => d.x)
        .attr('cy', (d: any) => d.y)

      label
        .attr('x', (d: any) => d.x)
        .attr('y', (d: any) => d.y)
    })
  }

  const renderTimeline = (svg: d3.Selection<SVGSVGElement, unknown, null, undefined>, data: TimelineData) => {
    const margin = { top: 20, right: 20, bottom: 40, left: 60 }
    const innerWidth = width - margin.left - margin.right
    const innerHeight = height - margin.top - margin.bottom

    const parseDate = d3.timeParse('%Y-%m-%d')
    const events = data.events.map(d => ({
      ...d,
      date: parseDate(d.date) || new Date()
    })).sort((a, b) => a.date.getTime() - b.date.getTime())

    const xScale = d3.scaleTime()
      .domain(d3.extent(events, d => d.date) as [Date, Date])
      .range([0, innerWidth])

    const yScale = d3.scaleBand()
      .domain(events.map(d => d.category))
      .range([0, innerHeight])
      .padding(0.1)

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`)

    // Add timeline line
    g.append('line')
      .attr('x1', 0)
      .attr('x2', innerWidth)
      .attr('y1', innerHeight / 2)
      .attr('y2', innerHeight / 2)
      .attr('stroke', theme === 'dark' ? '#64748b' : '#94a3b8')
      .attr('stroke-width', 2)

    // Add events
    const eventGroups = g.selectAll('.event')
      .data(events)
      .enter().append('g')
      .attr('class', 'event')
      .attr('transform', d => `translate(${xScale(d.date)}, ${yScale(d.category) || 0})`)

    eventGroups.append('circle')
      .attr('r', 6)
      .attr('fill', '#3b82f6')
      .attr('stroke', theme === 'dark' ? '#1f2937' : '#ffffff')
      .attr('stroke-width', 2)

    eventGroups.append('text')
      .text(d => d.title)
      .attr('dy', -10)
      .attr('text-anchor', 'middle')
      .attr('font-size', 10)
      .attr('fill', theme === 'dark' ? '#f1f5f9' : '#1f2937')

    // Add axes
    g.append('g')
      .attr('transform', `translate(0, ${innerHeight})`)
      .call(d3.axisBottom(xScale))

    g.append('g')
      .call(d3.axisLeft(yScale))
  }

  const renderHierarchy = (svg: d3.Selection<SVGSVGElement, unknown, null, undefined>, data: HierarchyData) => {
    const root = d3.hierarchy(data.root)
      .sum((d: any) => d.value || 1)
      .sort((a, b) => (b.value || 0) - (a.value || 0))

    const treeLayout = d3.tree<any>().size([width - 100, height - 100])
    treeLayout(root)

    const g = svg.append('g')
      .attr('transform', 'translate(50, 50)')

    // Add links
    const linkGenerator = d3.linkHorizontal<any, any>()
      .x((d: any) => d.y)
      .y((d: any) => d.x)

    g.selectAll('.link')
      .data(root.links())
      .enter().append('path')
      .attr('class', 'link')
      .attr('d', linkGenerator as any)
      .attr('fill', 'none')
      .attr('stroke', theme === 'dark' ? '#64748b' : '#94a3b8')
      .attr('stroke-width', 2)

    // Add nodes
    const nodeGroups = g.selectAll('.node')
      .data(root.descendants())
      .enter().append('g')
      .attr('class', 'node')
      .attr('transform', d => `translate(${d.y}, ${d.x})`)

    nodeGroups.append('circle')
      .attr('r', 8)
      .attr('fill', '#3b82f6')
      .attr('stroke', theme === 'dark' ? '#1f2937' : '#ffffff')
      .attr('stroke-width', 2)

    nodeGroups.append('text')
      .text(d => d.data.name)
      .attr('dy', 3)
      .attr('x', d => d.children ? -12 : 12)
      .attr('text-anchor', d => d.children ? 'end' : 'start')
      .attr('font-size', 12)
      .attr('fill', theme === 'dark' ? '#f1f5f9' : '#1f2937')
  }

  const renderComparison = (svg: d3.Selection<SVGSVGElement, unknown, null, undefined>, data: ComparisonData) => {
    const margin = { top: 20, right: 20, bottom: 40, left: 60 }
    const innerWidth = width - margin.left - margin.right
    const innerHeight = height - margin.top - margin.bottom

    const xScale = d3.scaleBand()
      .domain(data.items.map(d => d.name))
      .range([0, innerWidth])
      .padding(0.1)

    const yScale = d3.scaleLinear()
      .domain([0, d3.max(data.items, d => d3.max(Object.values(d.values))) || 0])
      .range([innerHeight, 0])

    const colorScale = d3.scaleOrdinal(d3.schemeCategory10)
      .domain(data.metrics)

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`)

    // Add bars for each metric
    data.metrics.forEach((metric, i) => {
      g.selectAll(`.bar-${i}`)
        .data(data.items)
        .enter().append('rect')
        .attr('class', `bar-${i}`)
        .attr('x', d => (xScale(d.name) || 0) + (xScale.bandwidth() / data.metrics.length) * i)
        .attr('y', d => yScale(d.values[metric] || 0))
        .attr('width', xScale.bandwidth() / data.metrics.length)
        .attr('height', d => innerHeight - yScale(d.values[metric] || 0))
        .attr('fill', colorScale(metric))
    })

    // Add axes
    g.append('g')
      .attr('transform', `translate(0, ${innerHeight})`)
      .call(d3.axisBottom(xScale))

    g.append('g')
      .call(d3.axisLeft(yScale))
  }

  const renderStatistics = (svg: d3.Selection<SVGSVGElement, unknown, null, undefined>, data: StatisticsData) => {
    // For simplicity, render the first chart as a bar chart
    if (data.charts.length === 0) return

    const chartData = data.charts[0]
    const margin = { top: 20, right: 20, bottom: 40, left: 60 }
    const innerWidth = width - margin.left - margin.right
    const innerHeight = height - margin.top - margin.bottom

    const xScale = d3.scaleBand()
      .domain(chartData.data.map(d => d.label))
      .range([0, innerWidth])
      .padding(0.1)

    const yScale = d3.scaleLinear()
      .domain([0, d3.max(chartData.data, d => d.value) || 0])
      .range([innerHeight, 0])

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`)

    // Add bars
    g.selectAll('.bar')
      .data(chartData.data)
      .enter().append('rect')
      .attr('class', 'bar')
      .attr('x', d => xScale(d.label) || 0)
      .attr('y', d => yScale(d.value))
      .attr('width', xScale.bandwidth())
      .attr('height', d => innerHeight - yScale(d.value))
      .attr('fill', '#3b82f6')

    // Add axes
    g.append('g')
      .attr('transform', `translate(0, ${innerHeight})`)
      .call(d3.axisBottom(xScale))

    g.append('g')
      .call(d3.axisLeft(yScale))

    // Add title
    svg.append('text')
      .attr('x', width / 2)
      .attr('y', 20)
      .attr('text-anchor', 'middle')
      .attr('font-size', 16)
      .attr('font-weight', 'bold')
      .attr('fill', theme === 'dark' ? '#f1f5f9' : '#1f2937')
      .text(chartData.title)
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64 bg-red-50 border border-red-200 rounded-lg">
        <div className="text-center">
          <div className="text-red-600 text-lg font-semibold mb-2">Visualization Error</div>
          <div className="text-red-500 text-sm">{error}</div>
        </div>
      </div>
    )
  }

  return (
    <div className="relative">
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-white bg-opacity-75 z-10">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
            className="w-8 h-8 border-2 border-primary-600 border-t-transparent rounded-full"
          />
        </div>
      )}
      <svg
        ref={svgRef}
        width={width}
        height={height}
        className={`border rounded-lg ${theme === 'dark' ? 'bg-gray-900' : 'bg-white'}`}
      />
    </div>
  )
} 