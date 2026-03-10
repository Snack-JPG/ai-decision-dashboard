import { NextRequest, NextResponse } from 'next/server'
import { getBackendUrl, withBackendAuth } from '@/lib/backend-url'

const BACKEND_URL = getBackendUrl()

export async function GET() {
  try {
    const response = await fetch(`${BACKEND_URL}/datasets`, {
      method: 'GET',
      cache: 'no-store',
      headers: withBackendAuth({
        'Content-Type': 'application/json',
      }),
    })

    if (!response.ok) {
      return NextResponse.json(
        { error: 'Failed to fetch datasets' },
        { status: response.status >= 400 && response.status < 600 ? response.status : 502 }
      )
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error fetching datasets:', error)
    return NextResponse.json(
      { error: 'Failed to fetch datasets' },
      { status: 502 }
    )
  }
}

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData()
    
    const response = await fetch(`${BACKEND_URL}/ingest`, {
      method: 'POST',
      headers: withBackendAuth(),
      body: formData,
    })

    if (!response.ok) {
      const status = response.status >= 400 && response.status < 600 ? response.status : 502
      const message =
        status === 400
          ? 'Invalid CSV upload'
          : status === 413
            ? 'Uploaded file is too large'
            : status === 429
              ? 'Upload quota exceeded'
            : 'Failed to upload dataset'

      return NextResponse.json({ error: message }, { status })
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error uploading dataset:', error)
    return NextResponse.json(
      { error: 'Failed to upload dataset' },
      { status: 502 }
    )
  }
}
