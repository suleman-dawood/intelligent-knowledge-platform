import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    
    const contentType = formData.get('type') as string;
    const title = formData.get('title') as string;
    const content = formData.get('content') as string;
    const url = formData.get('url') as string;
    const file = formData.get('file') as File | null;

    // Prepare the payload for the backend API
    const payload: any = {
      type: contentType,
      title,
    };

    // Handle different content types
    switch (contentType) {
      case 'text':
      case 'academic':
        payload.content = content;
        break;
      case 'url':
        payload.url = url;
        break;
      case 'pdf':
        // For PDF files, we would typically upload to a file storage service
        // and then pass the URL to the backend
        if (file) {
          // For now, we'll simulate file processing
          payload.filename = file.name;
          payload.size = file.size;
          // In a real implementation, you would:
          // 1. Upload file to storage (AWS S3, etc.)
          // 2. Get the file URL
          // 3. Pass URL to backend for processing
        }
        break;
    }

    // Send to backend API for processing
    const backendResponse = await fetch('http://localhost:3100/api/process-content', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!backendResponse.ok) {
      throw new Error(`Backend API error: ${backendResponse.status}`);
    }

    const result = await backendResponse.json();

    return NextResponse.json({
      success: true,
      message: 'Content submitted successfully',
      taskId: result.task_id,
    });

  } catch (error) {
    console.error('Content submission error:', error);
    
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred',
      },
      { status: 500 }
    );
  }
} 