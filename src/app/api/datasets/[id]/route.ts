import { NextRequest, NextResponse } from 'next/server'
import { getBackendUrl, withBackendAuth } from '@/lib/backend-url'

const BACKEND_URL = getBackendUrl()

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params
    
    const response = await fetch(`${BACKEND_URL}/datasets/${id}`, {
      method: 'GET',
      cache: 'no-store',
      headers: withBackendAuth({
        'Content-Type': 'application/json',
      }),
    })

    if (!response.ok) {
      const status = response.status >= 400 && response.status < 600 ? response.status : 502
      return NextResponse.json(
        { error: status === 404 ? 'Dataset not found' : 'Failed to fetch dataset' },
        { status }
      )
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error fetching dataset:', error)
    return NextResponse.json(
      { error: 'Failed to fetch dataset' },
      { status: 502 }
    )
  }
}
