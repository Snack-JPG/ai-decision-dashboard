import { NextRequest, NextResponse } from 'next/server'
import { getBackendUrl, withBackendAuth } from '@/lib/backend-url'

const BACKEND_URL = getBackendUrl()

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id: datasetId } = await params

  try {
    const response = await fetch(`${BACKEND_URL}/briefing/${datasetId}`, {
      method: 'POST',
      headers: withBackendAuth({
        'Content-Type': 'application/json',
      }),
    })

    if (!response.ok) {
      const status = response.status >= 400 && response.status < 600 ? response.status : 502
      return NextResponse.json(
        {
          error: status === 404 ? 'Dataset not found' : 'Failed to generate briefing',
        },
        { status }
      )
    }

    const briefingData = await response.json()
    return NextResponse.json(briefingData)

  } catch (error) {
    console.error('Error generating briefing:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 502 }
    )
  }
}
