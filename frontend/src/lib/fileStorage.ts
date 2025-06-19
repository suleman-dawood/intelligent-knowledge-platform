interface UploadProgress {
  loaded: number
  total: number
  percentage: number
}

interface UploadResult {
  success: boolean
  fileId?: string
  url?: string
  error?: string
}

// In-memory file metadata storage (in production, use a database)
export const fileMetadata: Map<string, any> = new Map()

export interface FileMetadata {
  id: string;
  filename: string;
  storedFilename: string;
  size: number;
  mimeType: string;
  uploadedAt: string;
  url: string;
  path: string;
}

export function getFileMetadata(fileId: string): FileMetadata | undefined {
  return fileMetadata.get(fileId);
}

export function setFileMetadata(fileId: string, metadata: FileMetadata): void {
  fileMetadata.set(fileId, metadata);
}

export function deleteFileMetadata(fileId: string): boolean {
  return fileMetadata.delete(fileId);
}

class FileStorageService {
  private readonly maxFileSize = 10 * 1024 * 1024 // 10MB
  private readonly allowedTypes = [
    'application/pdf',
    'text/plain',
    'text/markdown',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
  ]

  async uploadFile(
    file: File,
    onProgress?: (progress: UploadProgress) => void
  ): Promise<UploadResult> {
    try {
      // Validate file
      const validationError = this.validateFile(file)
      if (validationError) {
        return { success: false, error: validationError }
      }

      // Create form data
      const formData = new FormData()
      formData.append('file', file)
      formData.append('filename', file.name)
      formData.append('mimeType', file.type)

      // Upload with progress tracking
      return new Promise((resolve) => {
        const xhr = new XMLHttpRequest()

        // Track upload progress
        xhr.upload.addEventListener('progress', (event) => {
          if (event.lengthComputable && onProgress) {
            const progress: UploadProgress = {
              loaded: event.loaded,
              total: event.total,
              percentage: Math.round((event.loaded / event.total) * 100)
            }
            onProgress(progress)
          }
        })

        // Handle completion
        xhr.addEventListener('load', () => {
          if (xhr.status === 200) {
            try {
              const result = JSON.parse(xhr.responseText)
              resolve({
                success: true,
                fileId: result.fileId,
                url: result.url
              })
            } catch (error) {
              resolve({
                success: false,
                error: 'Invalid response from server'
              })
            }
          } else {
            try {
              const error = JSON.parse(xhr.responseText)
              resolve({
                success: false,
                error: error.message || 'Upload failed'
              })
            } catch {
              resolve({
                success: false,
                error: `Upload failed with status ${xhr.status}`
              })
            }
          }
        })

        // Handle errors
        xhr.addEventListener('error', () => {
          resolve({
            success: false,
            error: 'Network error during upload'
          })
        })

        // Start upload
        xhr.open('POST', '/api/files/upload')
        xhr.send(formData)
      })

    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      }
    }
  }

  async deleteFile(fileId: string): Promise<boolean> {
    try {
      const response = await fetch(`/api/files/${fileId}`, {
        method: 'DELETE'
      })
      return response.ok
    } catch (error) {
      console.error('Error deleting file:', error)
      return false
    }
  }

  async getFileMetadata(fileId: string): Promise<FileMetadata | null> {
    try {
      const response = await fetch(`/api/files/${fileId}/metadata`)
      if (response.ok) {
        return await response.json()
      }
      return null
    } catch (error) {
      console.error('Error getting file metadata:', error)
      return null
    }
  }

  private validateFile(file: File): string | null {
    if (file.size > this.maxFileSize) {
      return `File size must be less than ${this.maxFileSize / 1024 / 1024}MB`
    }

    if (!this.allowedTypes.includes(file.type)) {
      return `File type ${file.type} is not supported. Allowed types: PDF, Word documents, text files`
    }

    return null
  }

  formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes'
    
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  getFileIcon(mimeType: string): string {
    switch (mimeType) {
      case 'application/pdf':
        return '📄'
      case 'application/msword':
      case 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        return '📝'
      case 'text/plain':
      case 'text/markdown':
        return '📋'
      default:
        return '📁'
    }
  }
}

export const fileStorageService = new FileStorageService()
export type { UploadProgress, UploadResult } 