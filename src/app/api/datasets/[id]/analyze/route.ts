import { NextRequest, NextResponse } from 'next/server'
import { getBackendUrl, withBackendAuth } from '@/lib/backend-url'

const BACKEND_URL = getBackendUrl()

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params
    
    const response = await fetch(`${BACKEND_URL}/analyze/${id}/results`, {
      method: 'GET',
      cache: 'no-store',
      headers: withBackendAuth({
        'Content-Type': 'application/json',
      }),
    })

    if (!response.ok) {
      const status = response.status >= 400 && response.status < 600 ? response.status : 502
      return NextResponse.json(
        { error: status === 404 ? 'Dataset not found' : 'Failed to fetch analysis results' },
        { status }
      )
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error fetching analysis results:', error)
    return NextResponse.json(
      { error: 'Failed to fetch analysis results' },
      { status: 502 }
    )
  }
}

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params
    
    const response = await fetch(`${BACKEND_URL}/analyze/${id}`, {
      method: 'POST',
      headers: withBackendAuth({
        'Content-Type': 'application/json',
      }),
    })

    if (!response.ok) {
      const status = response.status >= 400 && response.status < 600 ? response.status : 502
      const message =
        status === 404
          ? 'Dataset not found'
          : status === 429
            ? 'Analysis quota exceeded'
            : 'Failed to run analysis'
      return NextResponse.json(
        { error: message },
        { status }
      )
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error running analysis:', error)
    return NextResponse.json(
      { error: 'Failed to run analysis' },
      { status: 502 }
    )
  }
}
