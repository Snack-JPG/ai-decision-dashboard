'use client'

import { useState, useEffect, useCallback } from 'react'
import { useParams } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { ThemeToggle } from "@/components/theme-toggle"
import { AlertTriangle, TrendingUp, TrendingDown, Activity, Download, ArrowLeft, FileText, Calendar } from "lucide-react"
import Link from 'next/link'

interface BriefingData {
  dataset_id: string
  executive_summary: string
  key_findings: Array<{
    title: string
    description: string
    confidence_score: number
    impact_level: 'high' | 'medium' | 'low'
  }>
  anomalies_risks: Array<{
    date?: string
    period?: string
    description: string
    severity: 'high' | 'medium' | 'low'
    confidence_score: number
  }>
  trend_analysis: Array<{
    metric: string
    direction: 'increasing' | 'decreasing' | 'stable'
    description: string
    confidence_score: number
    time_period?: string
  }>
  recommendations: Array<{
    title: string
    description: string
    priority: 'high' | 'medium' | 'low'
    confidence_score: number
  }>
  confidence_score: number
  generated_at: string
}

const getConfidenceColor = (score: number) => {
  if (score >= 0.8) return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300"
  if (score >= 0.6) return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300"
  return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300"
}

const getImpactColor = (level: string) => {
  switch (level) {
    case 'high': return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300"
    case 'medium': return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300"
    case 'low': return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300"
    default: return "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300"
  }
}

const getTrendIcon = (direction: string) => {
  switch (direction) {
    case 'increasing': return <TrendingUp className="h-4 w-4 text-green-500" />
    case 'decreasing': return <TrendingDown className="h-4 w-4 text-red-500" />
    default: return <Activity className="h-4 w-4 text-blue-500" />
  }
}

export default function BriefingPage() {
  const params = useParams()
  const datasetId = params.id as string
  
  const [briefing, setBriefing] = useState<BriefingData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)

  const fetchBriefing = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await fetch(`/api/datasets/${datasetId}/briefing`, {
        method: 'POST'
      })
      
      if (!response.ok) {
        throw new Error('Failed to generate briefing')
      }
      
      const data = await response.json()
      setBriefing(data)
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
      setIsGenerating(false)
    }
  }, [datasetId])

  useEffect(() => {
    if (!datasetId) return
    fetchBriefing()
  }, [datasetId, fetchBriefing])

  const regenerateBriefing = async () => {
    setIsGenerating(true)
    await fetchBriefing()
  }

  const exportToMarkdown = () => {
    if (!briefing) return

    const markdown = `# Executive Briefing
Generated: ${new Date(briefing.generated_at).toLocaleString()}
Overall Confidence: ${Math.round(briefing.confidence_score * 100)}%

## Executive Summary

${briefing.executive_summary}

## Key Findings

${briefing.key_findings.map((finding, index) => 
  `### ${index + 1}. ${finding.title}
${finding.description}
**Impact:** ${finding.impact_level.toUpperCase()} | **Confidence:** ${Math.round(finding.confidence_score * 100)}%`
).join('\n\n')}

## Anomalies & Risks

${briefing.anomalies_risks.map((anomaly, index) => 
  `### Risk ${index + 1}${anomaly.date ? ` - ${anomaly.date}` : ''}
${anomaly.description}
**Severity:** ${anomaly.severity.toUpperCase()} | **Confidence:** ${Math.round(anomaly.confidence_score * 100)}%`
).join('\n\n')}

## Trend Analysis

${briefing.trend_analysis.map((trend, index) => 
  `### ${trend.metric}
**Direction:** ${trend.direction.toUpperCase()}
${trend.description}
**Confidence:** ${Math.round(trend.confidence_score * 100)}%`
).join('\n\n')}

## Recommendations

${briefing.recommendations.map((rec, index) => 
  `### ${index + 1}. ${rec.title}
${rec.description}
**Priority:** ${rec.priority.toUpperCase()} | **Confidence:** ${Math.round(rec.confidence_score * 100)}%`
).join('\n\n')}

---
*This briefing was automatically generated using AI analysis. Please review findings and confidence scores before making decisions.*`

    const blob = new Blob([markdown], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `briefing-${datasetId}-${new Date().toISOString().split('T')[0]}.md`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  if (loading || isGenerating) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <Activity className="h-8 w-8 animate-spin mx-auto mb-4 text-primary" />
          <p className="text-muted-foreground">
            {isGenerating ? 'Regenerating briefing...' : 'Generating briefing...'}
          </p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center max-w-md">
          <AlertTriangle className="h-8 w-8 mx-auto mb-4 text-destructive" />
          <p className="text-destructive mb-4">{error}</p>
          <div className="space-x-2">
            <Button onClick={regenerateBriefing}>
              Try Again
            </Button>
            <Button variant="outline" asChild>
              <Link href={`/dashboard/${datasetId}`}>Back to Dashboard</Link>
            </Button>
          </div>
        </div>
      </div>
    )
  }

  if (!briefing) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <FileText className="h-8 w-8 mx-auto mb-4 text-muted-foreground" />
          <p className="text-muted-foreground">No briefing data available</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="sm" asChild>
                <Link href={`/dashboard/${datasetId}`}>
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back to Dashboard
                </Link>
              </Button>
              <div>
                <h1 className="text-2xl font-bold">Executive Briefing</h1>
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Calendar className="h-4 w-4" />
                  Generated {new Date(briefing.generated_at).toLocaleString()}
                  <Badge className={getConfidenceColor(briefing.confidence_score)}>
                    {Math.round(briefing.confidence_score * 100)}% Overall Confidence
                  </Badge>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm" onClick={regenerateBriefing}>
                <FileText className="h-4 w-4 mr-2" />
                Regenerate
              </Button>
              <Button size="sm" onClick={exportToMarkdown}>
                <Download className="h-4 w-4 mr-2" />
                Export Markdown
              </Button>
              <ThemeToggle />
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6 max-w-4xl">
        {/* Executive Summary */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Executive Summary
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-lg leading-relaxed">{briefing.executive_summary}</p>
          </CardContent>
        </Card>

        {/* Key Findings */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Key Findings</CardTitle>
            <CardDescription>
              Top insights ranked by importance and impact
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {briefing.key_findings.map((finding, index) => (
              <div key={index} className="border rounded-lg p-4">
                <div className="flex items-start justify-between mb-2">
                  <h3 className="font-semibold text-lg">
                    {index + 1}. {finding.title}
                  </h3>
                  <div className="flex gap-2">
                    <Badge className={getImpactColor(finding.impact_level)}>
                      {finding.impact_level} impact
                    </Badge>
                    <Badge className={getConfidenceColor(finding.confidence_score)}>
                      {Math.round(finding.confidence_score * 100)}%
                    </Badge>
                  </div>
                </div>
                <p className="text-muted-foreground">{finding.description}</p>
              </div>
            ))}
          </CardContent>
        </Card>

        <div className="grid md:grid-cols-2 gap-6 mb-6">
          {/* Anomalies & Risks */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5" />
                Anomalies & Risks
              </CardTitle>
              <CardDescription>
                Significant outliers and areas of concern
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {briefing.anomalies_risks.map((anomaly, index) => (
                <div key={index} className="border rounded-lg p-3">
                  <div className="flex items-start justify-between mb-1">
                    {anomaly.date && (
                      <span className="text-sm font-medium text-muted-foreground">
                        {anomaly.date}
                      </span>
                    )}
                    <div className="flex gap-1">
                      <Badge 
                        variant="outline" 
                        className={getImpactColor(anomaly.severity)}
                      >
                        {anomaly.severity}
                      </Badge>
                      <Badge className={getConfidenceColor(anomaly.confidence_score)}>
                        {Math.round(anomaly.confidence_score * 100)}%
                      </Badge>
                    </div>
                  </div>
                  <p className="text-sm">{anomaly.description}</p>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Trend Analysis */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                Trend Analysis
              </CardTitle>
              <CardDescription>
                Statistical patterns and directions
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {briefing.trend_analysis.map((trend, index) => (
                <div key={index} className="border rounded-lg p-3">
                  <div className="flex items-center justify-between mb-1">
                    <div className="flex items-center gap-2">
                      {getTrendIcon(trend.direction)}
                      <span className="font-medium">{trend.metric}</span>
                    </div>
                    <Badge className={getConfidenceColor(trend.confidence_score)}>
                      {Math.round(trend.confidence_score * 100)}%
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground">{trend.description}</p>
                  {trend.time_period && (
                    <p className="text-xs text-muted-foreground mt-1">
                      Period: {trend.time_period}
                    </p>
                  )}
                </div>
              ))}
            </CardContent>
          </Card>
        </div>

        {/* Recommendations */}
        <Card>
          <CardHeader>
            <CardTitle>Recommendations</CardTitle>
            <CardDescription>
              Actionable next steps based on the analysis
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {briefing.recommendations.map((rec, index) => (
              <div key={index} className="border rounded-lg p-4">
                <div className="flex items-start justify-between mb-2">
                  <h3 className="font-semibold">
                    {index + 1}. {rec.title}
                  </h3>
                  <div className="flex gap-2">
                    <Badge className={getImpactColor(rec.priority)}>
                      {rec.priority} priority
                    </Badge>
                    <Badge className={getConfidenceColor(rec.confidence_score)}>
                      {Math.round(rec.confidence_score * 100)}%
                    </Badge>
                  </div>
                </div>
                <p className="text-muted-foreground">{rec.description}</p>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Footer Note */}
        <div className="mt-8 text-center text-sm text-muted-foreground">
          <p>
            This briefing was automatically generated using AI analysis. 
            Please review findings and confidence scores before making decisions.
          </p>
        </div>
      </main>
    </div>
  )
}
