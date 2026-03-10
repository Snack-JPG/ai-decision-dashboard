import { NextResponse } from 'next/server'
import { getBackendUrl, withBackendAuth } from '@/lib/backend-url'

const BACKEND_URL = getBackendUrl()

export async function POST() {
  try {
    // Read the realistic NHS A&E demo dataset
    const fs = require('fs')
    const path = require('path')
    
    const csvPath = path.join(process.cwd(), 'backend', 'data', 'nhs_ae_demo.csv')
    
    if (!fs.existsSync(csvPath)) {
      throw new Error('Demo dataset not found. Please ensure the NHS demo data has been generated.')
    }
    
    const demoData = fs.readFileSync(csvPath, 'utf-8')

    // Create FormData with Web API
    const formData = new FormData()
    
    // Create a blob from the CSV data
    const csvBlob = new Blob([demoData], { type: 'text/csv' })
    formData.append('file', csvBlob, 'nhs_ae_demo.csv')
    formData.append('name', 'NHS A&E Performance Data (2021-2023)')
    formData.append('description', 'NHS A&E monthly performance data across 15 trusts with attendances, 4-hour target compliance, emergency admissions, 12-hour waits, and ambulance handover delays. Includes seasonal patterns, COVID impact, and regional variation.')

    // Upload to backend
    const response = await fetch(`${BACKEND_URL}/ingest`, {
      method: 'POST',
      headers: withBackendAuth(),
      body: formData,
    })

    if (!response.ok) {
      throw new Error(`Backend responded with status: ${response.status}`)
    }

    const dataset = await response.json()
    
    // Run analysis on the demo dataset
    try {
      const analysisResponse = await fetch(`${BACKEND_URL}/analyze/${dataset.dataset_id}`, {
        method: 'POST',
        headers: withBackendAuth({
          'Content-Type': 'application/json',
        }),
      })

      if (!analysisResponse.ok) {
        console.warn('Analysis failed, but dataset was created:', analysisResponse.status)
      } else {
        console.log('Analysis completed successfully')
      }
    } catch (analysisError) {
      console.warn('Analysis failed but continuing:', analysisError)
    }

    return NextResponse.json({ 
      dataset_id: dataset.dataset_id,
      message: 'Demo data loaded successfully'
    })
  } catch (error) {
    console.error('Error loading demo data:', error)
    return NextResponse.json(
      { error: 'Failed to load demo data' },
      { status: 502 }
    )
  }
}
