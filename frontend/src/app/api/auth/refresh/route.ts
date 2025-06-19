import { NextRequest, NextResponse } from 'next/server'
import jwt from 'jsonwebtoken'
import { z } from 'zod'

const refreshSchema = z.object({
  refreshToken: z.string().min(1, 'Refresh token is required')
})

const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key-change-in-production'
const REFRESH_SECRET = process.env.REFRESH_SECRET || 'your-refresh-secret-change-in-production'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    
    // Validate input
    const validationResult = refreshSchema.safeParse(body)
    if (!validationResult.success) {
      return NextResponse.json(
        { message: 'Invalid input', errors: validationResult.error.issues },
        { status: 400 }
      )
    }
    
    const { refreshToken } = validationResult.data
    
    // Verify refresh token
    try {
      const decoded = jwt.verify(refreshToken, REFRESH_SECRET) as any
      
      if (decoded.type !== 'refresh') {
        return NextResponse.json(
          { message: 'Invalid token type' },
          { status: 401 }
        )
      }
      
      // Generate new access token
      const newToken = jwt.sign(
        { userId: decoded.userId, type: 'access' },
        JWT_SECRET,
        { expiresIn: '15m' }
      )
      
      return NextResponse.json({
        token: newToken
      })
      
    } catch (error) {
      return NextResponse.json(
        { message: 'Invalid or expired refresh token' },
        { status: 401 }
      )
    }
    
  } catch (error) {
    console.error('Refresh token error:', error)
    return NextResponse.json(
      { message: 'Internal server error' },
      { status: 500 }
    )
  }
} 