'use client'

import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ThemeToggle } from "@/components/theme-toggle"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { AlertTriangle, TrendingUp, TrendingDown, Activity, Brain, FileText, ArrowLeft } from "lucide-react"
import Link from 'next/link'

import { OverviewCards } from '@/components/dashboard/overview-cards'
import { TimeSeriesChart } from '@/components/dashboard/time-series-chart'
import { AnomalyTable } from '@/components/dashboard/anomaly-table'
import { BreakdownTable } from '@/components/dashboard/breakdown-table'
import { QueryInterface } from '@/components/query-interface'

interface Dataset {
  id: string
  name: string
  description?: string | null
  rows_count: number
  columns_count: number
  created_at: string
  columns: Array<{
    name: string
    data_type: string
    role: string
  }>
}

interface AnalysisResults {
  dataset_id: string
  status: 'completed' | 'no_analysis' | 'processing'
  requires_refresh?: boolean
  summary: {
    total_rows: number
    date_range: {
      start: string
      end: string
    } | null
    key_metrics: Array<{
      name: string
      value: number
      change_percent: number
      trend: 'up' | 'down' | 'stable'
      confidence: number
    }>
  }
  trends: Array<{
    metric: string
    direction: 'increasing' | 'decreasing' | 'stable'
    slope: number
    r_squared: number
    confidence: number
    explanation: string
  }>
  anomalies: Array<{
    date: string
    metric: string
    value: number
    expected: number
    severity: 'low' | 'medium' | 'high'
    explanation: string
    confidence: number
  }>
  insights: Array<{
    type: 'trend' | 'anomaly' | 'correlation' | 'seasonal'
    title: string
    description: string
    confidence: number
    impact: 'low' | 'medium' | 'high'
  }>
  time_series_data: Array<{
    date: string
    [key: string]: string | number
  }>
}

export default function DashboardPage() {
  const params = useParams()
  const datasetId = params.id as string
  
  const [dataset, setDataset] = useState<Dataset | null>(null)
  const [analysis, setAnalysis] = useState<AnalysisResults | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isQueryOpen, setIsQueryOpen] = useState(false)

  useEffect(() => {
    if (!datasetId) return

    const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

    const fetchData = async () => {
      try {
        setLoading(true)
        
        // Fetch dataset metadata
        const datasetResponse = await fetch(`/api/datasets/${datasetId}`, {
          cache: 'no-store'
        })
        if (!datasetResponse.ok) {
          throw new Error('Failed to fetch dataset')
        }
        const datasetData = await datasetResponse.json()
        setDataset(datasetData)

        let analysisData: AnalysisResults | null = null
        let shouldTriggerAnalysis = false

        for (let attempt = 0; attempt < 50; attempt++) {
          const analysisResponse = await fetch(`/api/datasets/${datasetId}/analyze`, {
            cache: 'no-store'
          })

          if (!analysisResponse.ok) {
            throw new Error('Failed to fetch analysis results')
          }

          const payload = await analysisResponse.json()
          analysisData = payload

          if (payload.status === 'completed' && !payload.requires_refresh) {
            break
          }

          if (!shouldTriggerAnalysis && (payload.status === 'no_analysis' || payload.requires_refresh)) {
            shouldTriggerAnalysis = true
            const runAnalysisResponse = await fetch(`/api/datasets/${datasetId}/analyze`, {
              method: 'POST',
            })

            if (!runAnalysisResponse.ok) {
              throw new Error('Failed to analyze dataset')
            }
          }

          await sleep(1500)
        }

        if (!analysisData || analysisData.status !== 'completed') {
          throw new Error('Analysis is still processing. Please refresh in a moment.')
        }

        setAnalysis(analysisData)
        
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [datasetId])

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <Activity className="h-8 w-8 animate-spin mx-auto mb-4 text-primary" />
          <p className="text-muted-foreground">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <AlertTriangle className="h-8 w-8 mx-auto mb-4 text-destructive" />
          <p className="text-destructive mb-4">{error}</p>
          <Button asChild>
            <Link href="/">Return Home</Link>
          </Button>
        </div>
      </div>
    )
  }

  if (!dataset || !analysis) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <AlertTriangle className="h-8 w-8 mx-auto mb-4 text-muted-foreground" />
          <p className="text-muted-foreground">No data available</p>
        </div>
      </div>
    )
  }

  const dateRangeLabel = analysis.summary.date_range
    ? `${analysis.summary.date_range.start} to ${analysis.summary.date_range.end}`
    : 'No detected time range'

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="sm" asChild>
                <Link href="/">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back
                </Link>
              </Button>
              <div>
                <h1 className="text-2xl font-bold">{dataset.name}</h1>
                <p className="text-muted-foreground">
                  {analysis.summary.total_rows.toLocaleString()} rows • 
                  {' '}{dateRangeLabel}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <Button variant="outline" size="sm" onClick={() => setIsQueryOpen(true)}>
                <Brain className="h-4 w-4 mr-2" />
                Ask Question
              </Button>
              <Button size="sm" asChild>
                <Link href={`/dashboard/${datasetId}/briefing`}>
                  <FileText className="h-4 w-4 mr-2" />
                  Generate Briefing
                </Link>
              </Button>
              <ThemeToggle />
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6">
        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList>
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="trends">Trends</TabsTrigger>
            <TabsTrigger value="anomalies">Anomalies</TabsTrigger>
            <TabsTrigger value="insights">Insights</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            {/* Overview Cards */}
            <OverviewCards 
              metrics={analysis.summary.key_metrics} 
              insights={analysis.insights}
            />

            {/* Main Chart */}
            <Card>
              <CardHeader>
                <CardTitle>Time Series Analysis</CardTitle>
                <CardDescription>
                  Key metrics over time with anomaly detection
                </CardDescription>
              </CardHeader>
              <CardContent>
                <TimeSeriesChart 
                  data={analysis.time_series_data}
                  anomalies={analysis.anomalies}
                />
              </CardContent>
            </Card>

            {/* Breakdown Table */}
            <BreakdownTable 
              data={analysis.time_series_data}
              metrics={analysis.summary.key_metrics}
            />
          </TabsContent>

          <TabsContent value="trends" className="space-y-6">
            <div className="grid gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Trend Analysis</CardTitle>
                  <CardDescription>
                    Statistical trend detection with confidence scores
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {analysis.trends.length > 0 ? (
                    <div className="space-y-4">
                      {analysis.trends.map((trend, index) => (
                        <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                          <div className="flex items-center gap-3">
                            {trend.direction === 'increasing' ? (
                              <TrendingUp className="h-5 w-5 text-green-500" />
                            ) : trend.direction === 'decreasing' ? (
                              <TrendingDown className="h-5 w-5 text-red-500" />
                            ) : (
                              <Activity className="h-5 w-5 text-blue-500" />
                            )}
                            <div>
                              <p className="font-medium">{trend.metric}</p>
                              <p className="text-sm text-muted-foreground">{trend.explanation}</p>
                            </div>
                          </div>
                          <div className="text-right">
                            <Badge variant={trend.confidence > 0.8 ? "default" : "secondary"}>
                              {Math.round(trend.confidence * 100)}% confidence
                            </Badge>
                            <p className="text-sm text-muted-foreground mt-1">
                              R² = {trend.r_squared.toFixed(3)}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-muted-foreground">No statistically significant trends were detected.</p>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="anomalies" className="space-y-6">
            <AnomalyTable anomalies={analysis.anomalies} />
          </TabsContent>

          <TabsContent value="insights" className="space-y-6">
            <div className="grid gap-4">
              {analysis.insights.length > 0 ? (
                analysis.insights.map((insight, index) => (
                  <Card key={index}>
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <CardTitle className="text-lg">{insight.title}</CardTitle>
                        <div className="flex items-center gap-2">
                          <Badge variant={insight.impact === 'high' ? "destructive" : insight.impact === 'medium' ? "default" : "secondary"}>
                            {insight.impact} impact
                          </Badge>
                          <Badge variant="outline">
                            {Math.round(insight.confidence * 100)}% confidence
                          </Badge>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <p className="text-muted-foreground">{insight.description}</p>
                    </CardContent>
                  </Card>
                ))
              ) : (
                <Card>
                  <CardContent className="pt-6">
                    <p className="text-sm text-muted-foreground">No high-confidence insights are available yet.</p>
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>
        </Tabs>
      </main>

      {/* Query Interface */}
      <QueryInterface 
        datasetId={datasetId}
        datasetName={dataset?.name}
        isOpen={isQueryOpen}
        onClose={() => setIsQueryOpen(false)}
      />
    </div>
  )
}
