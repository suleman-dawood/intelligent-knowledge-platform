import { NextRequest, NextResponse } from 'next/server'

interface KnowledgeStats {
  totalEntities: number
  totalRelations: number
  recentEntities: number
  recentSources: number
  weeklyGrowth: {
    entities: number
    relations: number
    sources: number
    queries: number
  }
}

export async function GET(request: NextRequest) {
  try {
    // In production, this would query a real database
    // For now, return realistic mock data with some randomization
    
    const baseStats = {
      totalEntities: 12580,
      totalRelations: 35624,
      recentEntities: 156,
      recentSources: 42
    }

    // Add some realistic variation
    const stats: KnowledgeStats = {
      totalEntities: baseStats.totalEntities + Math.floor(Math.random() * 1000),
      totalRelations: baseStats.totalRelations + Math.floor(Math.random() * 2000),
      recentEntities: baseStats.recentEntities + Math.floor(Math.random() * 50 - 25),
      recentSources: baseStats.recentSources + Math.floor(Math.random() * 20 - 10),
      weeklyGrowth: {
        entities: Math.random() * 20 - 5, // -5 to 15
        relations: Math.random() * 15 - 2, // -2 to 13
        sources: Math.random() * 25 - 3, // -3 to 22
        queries: Math.random() * 30 + 5 // 5 to 35
      }
    }

    return NextResponse.json(stats)

  } catch (error) {
    console.error('Error fetching knowledge stats:', error)
    return NextResponse.json(
      { message: 'Internal server error' },
      { status: 500 }
    )
  }
} 