import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    // In a production app, you might want to:
    // 1. Blacklist the token
    // 2. Remove the refresh token from the database
    // 3. Log the logout event
    
    // For now, we'll just return a success response
    // The client will handle clearing the tokens from localStorage
    
    return NextResponse.json({
      message: 'Logged out successfully'
    })
    
  } catch (error) {
    console.error('Logout error:', error)
    return NextResponse.json(
      { message: 'Internal server error' },
      { status: 500 }
    )
  }
} 