import { NextRequest, NextResponse } from 'next/server'
import { writeFile, mkdir } from 'fs/promises'
import { existsSync } from 'fs'
import path from 'path'
import { setFileMetadata, type FileMetadata } from '@/lib/fileStorage'

const UPLOAD_DIR = path.join(process.cwd(), 'uploads')
const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB

const ALLOWED_TYPES = [
  'application/pdf',
  'text/plain',
  'text/markdown',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
]

function generateFileId(): string {
  return Math.random().toString(36).substring(2) + Date.now().toString(36)
}

function sanitizeFilename(filename: string): string {
  return filename.replace(/[^a-zA-Z0-9.-]/g, '_')
}

export async function POST(request: NextRequest) {
  try {
    // Ensure upload directory exists
    if (!existsSync(UPLOAD_DIR)) {
      await mkdir(UPLOAD_DIR, { recursive: true })
    }

    const formData = await request.formData()
    const file = formData.get('file') as File
    const originalFilename = formData.get('filename') as string
    const mimeType = formData.get('mimeType') as string

    if (!file) {
      return NextResponse.json(
        { message: 'No file provided' },
        { status: 400 }
      )
    }

    // Validate file size
    if (file.size > MAX_FILE_SIZE) {
      return NextResponse.json(
        { message: `File size must be less than ${MAX_FILE_SIZE / 1024 / 1024}MB` },
        { status: 400 }
      )
    }

    // Validate file type
    if (!ALLOWED_TYPES.includes(file.type)) {
      return NextResponse.json(
        { message: `File type ${file.type} is not supported` },
        { status: 400 }
      )
    }

    // Generate unique file ID and sanitize filename
    const fileId = generateFileId()
    const sanitizedFilename = sanitizeFilename(originalFilename || file.name)
    const fileExtension = path.extname(sanitizedFilename)
    const storedFilename = `${fileId}${fileExtension}`
    const filePath = path.join(UPLOAD_DIR, storedFilename)

    // Convert file to buffer and save
    const bytes = await file.arrayBuffer()
    const buffer = Buffer.from(bytes)
    await writeFile(filePath, buffer)

    // Store metadata using the fileStorage module
    const metadata: FileMetadata = {
      id: fileId,
      filename: originalFilename || file.name,
      storedFilename,
      size: file.size,
      mimeType: file.type,
      uploadedAt: new Date().toISOString(),
      url: `/api/files/${fileId}/download`,
      path: filePath
    }

    setFileMetadata(fileId, metadata)

    // Return success response
    return NextResponse.json({
      success: true,
      fileId,
      url: metadata.url,
      filename: metadata.filename,
      size: metadata.size,
      mimeType: metadata.mimeType
    })

  } catch (error) {
    console.error('File upload error:', error)
    return NextResponse.json(
      { message: 'Internal server error during file upload' },
      { status: 500 }
    )
  }
} 