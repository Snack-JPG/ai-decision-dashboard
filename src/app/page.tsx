'use client'

import { useState, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ThemeToggle } from "@/components/theme-toggle"
import { Upload, BarChart3, Brain, FileText, Loader2 } from "lucide-react"

export default function HomePage() {
  const [isLoadingDemo, setIsLoadingDemo] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const router = useRouter()

  const handleDemoLoad = async () => {
    setIsLoadingDemo(true)
    try {
      const response = await fetch('/api/demo', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        throw new Error('Failed to load demo data')
      }

      const result = await response.json()
      router.push(`/dashboard/${result.dataset_id}`)
    } catch (error) {
      console.error('Error loading demo:', error)
      alert('Failed to load demo data. Please try again.')
    } finally {
      setIsLoadingDemo(false)
    }
  }

  const handleFileUpload = async (files: FileList) => {
    if (!files || files.length === 0) return

    const selectedFile = files[0]
    if (!selectedFile.name.toLowerCase().endsWith('.csv')) {
      alert('Only CSV files are supported right now.')
      return
    }

    setIsUploading(true)
    try {
      const formData = new FormData()
      formData.append('file', selectedFile)

      const response = await fetch('/api/datasets', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error('Failed to upload file')
      }

      const result = await response.json()
      const analysisResponse = await fetch(`/api/datasets/${result.dataset_id}/analyze`, {
        method: 'POST',
      })

      if (!analysisResponse.ok) {
        throw new Error('Failed to analyze dataset')
      }

      router.push(`/dashboard/${result.dataset_id}`)
    } catch (error) {
      console.error('Error uploading file:', error)
      alert('Failed to upload and analyze the file. Please check the CSV format and try again.')
    } finally {
      setIsUploading(false)
    }
  }

  const handleFileSelect = () => {
    fileInputRef.current?.click()
  }

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files
    if (files) {
      handleFileUpload(files)
    }
  }

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault()
    const files = event.dataTransfer.files
    if (files) {
      handleFileUpload(files)
    }
  }

  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault()
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold">AI Decision Support Dashboard</h1>
            <p className="text-muted-foreground">
              AI-powered data intelligence for government and enterprise
            </p>
          </div>
          <ThemeToggle />
        </div>
      </header>

      {/* Hero Section */}
      <main className="container mx-auto px-4 py-12">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold mb-4">
            Transform Your Data Into Actionable Insights
          </h2>
          <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
            Upload structured data and get AI-powered analysis with natural language insights, 
            anomaly detection, and professional briefings.
          </p>
          
          <div className="flex gap-4 justify-center">
            <Button 
              size="lg" 
              className="bg-primary hover:bg-primary/90"
              onClick={handleDemoLoad}
              disabled={isLoadingDemo}
            >
              {isLoadingDemo ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Loading Demo...
                </>
              ) : (
                'Try Demo Dataset'
              )}
            </Button>
            <Button 
              size="lg" 
              variant="outline"
              onClick={handleFileSelect}
              disabled={isUploading}
            >
              {isUploading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Uploading...
                </>
              ) : (
                'Upload Your Data'
              )}
            </Button>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          <Card>
            <CardHeader>
              <Upload className="h-8 w-8 mb-2 text-primary" />
              <CardTitle className="text-lg">Data Ingestion</CardTitle>
              <CardDescription>
                Drag-and-drop CSV upload with automatic schema detection
              </CardDescription>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader>
              <BarChart3 className="h-8 w-8 mb-2 text-primary" />
              <CardTitle className="text-lg">Smart Analytics</CardTitle>
              <CardDescription>
                Trend analysis, anomaly detection, and correlation discovery
              </CardDescription>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader>
              <Brain className="h-8 w-8 mb-2 text-primary" />
              <CardTitle className="text-lg">Natural Language</CardTitle>
              <CardDescription>
                Ask questions in plain English and get intelligent answers
              </CardDescription>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader>
              <FileText className="h-8 w-8 mb-2 text-primary" />
              <CardTitle className="text-lg">Auto Briefings</CardTitle>
              <CardDescription>
                Generate professional reports suitable for stakeholders
              </CardDescription>
            </CardHeader>
          </Card>
        </div>

        {/* Demo Section */}
        <Card className="mb-12">
          <CardHeader>
            <CardTitle>Demo: UK NHS A&E Waiting Times</CardTitle>
            <CardDescription>
              Explore real government data with AI-powered insights and analysis
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="bg-muted rounded-lg p-6 mb-4">
              <p className="text-sm text-muted-foreground mb-2">Sample Dataset</p>
              <p className="font-medium">NHS A&E Monthly Performance Data</p>
              <p className="text-sm text-muted-foreground">
                Monthly attendances, 4-hour target performance, admissions, and breaches by trust/region
              </p>
            </div>
            <Button 
              onClick={handleDemoLoad} 
              disabled={isLoadingDemo}
            >
              {isLoadingDemo ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Loading...
                </>
              ) : (
                'Load Demo Data'
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Upload Section */}
        <Card>
          <CardHeader>
            <CardTitle>Upload Your Data</CardTitle>
              <CardDescription>
                Drag and drop your CSV files to get started
              </CardDescription>
          </CardHeader>
          <CardContent>
            <div 
              className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-8 text-center hover:border-muted-foreground/50 transition-colors cursor-pointer"
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onClick={handleFileSelect}
            >
              {isUploading ? (
                <>
                  <Loader2 className="h-12 w-12 mx-auto mb-4 animate-spin text-primary" />
                  <p className="text-lg font-medium mb-2">Uploading and analyzing...</p>
                  <p className="text-sm text-muted-foreground">
                    Please wait while we process your data
                  </p>
                </>
              ) : (
                <>
                  <Upload className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                  <p className="text-lg font-medium mb-2">Drop files here or click to browse</p>
                  <p className="text-sm text-muted-foreground">
                    Supports CSV files up to 10MB
                  </p>
                </>
              )}
            </div>
            
            <input
              ref={fileInputRef}
              type="file"
              accept=".csv,text/csv"
              onChange={handleFileChange}
              className="hidden"
            />
          </CardContent>
        </Card>
      </main>

      {/* Footer */}
      <footer className="border-t bg-muted/50">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center">
            <p className="text-sm text-muted-foreground">
              Built with Next.js 15, TypeScript, and shadcn/ui
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}
