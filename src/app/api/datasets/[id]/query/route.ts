import { NextRequest, NextResponse } from 'next/server'
import { getBackendUrl, withBackendAuth } from '@/lib/backend-url'

const FASTAPI_BASE_URL = getBackendUrl()

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id: datasetId } = await params
    const body = await request.json()
    
    // Validate request body
    if (!body.question || !String(body.question).trim()) {
      return NextResponse.json(
        { error: 'Question is required' },
        { status: 400 }
      )
    }

    // Forward the request to FastAPI
    const response = await fetch(`${FASTAPI_BASE_URL}/query`, {
      method: 'POST',
      headers: withBackendAuth({
        'Content-Type': 'application/json',
      }),
      body: JSON.stringify({
        dataset_id: datasetId,
        question: String(body.question).trim().slice(0, 1000),
        conversation_history: body.conversation_history || []
      })
    })

    if (!response.ok) {
      const status = response.status >= 400 && response.status < 600 ? response.status : 502
      return NextResponse.json(
        {
          error:
            status === 400
              ? 'Question could not be processed'
              : status === 404
                ? 'Dataset not found'
                : 'Failed to process query',
        },
        { status }
      )
    }

    const data = await response.json()
    return NextResponse.json(data)

  } catch (error) {
    console.error('Query API route error:', error)
    
    return NextResponse.json(
      {
        error: 'Internal server error',
      },
      { status: 502 }
    )
  }
}
