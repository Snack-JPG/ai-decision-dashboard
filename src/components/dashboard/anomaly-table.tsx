'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { AlertTriangle, TrendingUp, TrendingDown } from "lucide-react"

interface Anomaly {
  date: string
  metric: string
  value: number
  expected: number
  severity: 'low' | 'medium' | 'high'
  explanation: string
  confidence: number
}

interface AnomalyTableProps {
  anomalies: Anomaly[]
}

function formatDate(dateStr: string): string {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  if (Number.isNaN(date.getTime())) return dateStr
  return date.toLocaleDateString('en-GB', { 
    day: 'numeric', 
    month: 'short', 
    year: 'numeric' 
  })
}

function formatValue(value: number): string {
  if (value >= 1000000) {
    return `${(value / 1000000).toFixed(1)}M`
  }
  if (value >= 1000) {
    return `${(value / 1000).toFixed(1)}K`
  }
  if (value < 1) {
    return `${(value * 100).toFixed(1)}%`
  }
  return value.toLocaleString()
}

function getSeverityVariant(severity: string): "default" | "secondary" | "destructive" | "outline" {
  switch (severity) {
    case 'high': return 'destructive'
    case 'medium': return 'default'
    case 'low': return 'secondary'
    default: return 'outline'
  }
}

function getDeviationIcon(actual: number, expected: number) {
  if (!expected) return null
  const deviation = ((actual - expected) / expected) * 100
  if (Math.abs(deviation) < 5) {
    return null
  }
  return deviation > 0 ? (
    <TrendingUp className="h-4 w-4 text-red-500" />
  ) : (
    <TrendingDown className="h-4 w-4 text-blue-500" />
  )
}

function getDeviationText(actual: number, expected: number): string {
  if (!expected) return 'n/a'
  const deviation = ((actual - expected) / expected) * 100
  const sign = deviation > 0 ? '+' : ''
  return `${sign}${deviation.toFixed(1)}%`
}

export function AnomalyTable({ anomalies }: AnomalyTableProps) {
  // Sort anomalies by date (most recent first) and severity
  const sortedAnomalies = [...anomalies].sort((a, b) => {
    const dateA = new Date(a.date)
    const dateB = new Date(b.date)
    if (dateA.getTime() !== dateB.getTime()) {
      return dateB.getTime() - dateA.getTime()
    }
    
    // If dates are equal, sort by severity
    const severityOrder = { high: 3, medium: 2, low: 1 }
    return severityOrder[b.severity] - severityOrder[a.severity]
  })

  if (anomalies.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Anomaly Detection</CardTitle>
          <CardDescription>
            No statistical anomalies detected in the current dataset
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <AlertTriangle className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
            <p className="text-muted-foreground">All data points appear normal</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <AlertTriangle className="h-5 w-5 text-orange-500" />
          Anomaly Detection Results
        </CardTitle>
        <CardDescription>
          {anomalies.length} statistical anomal{anomalies.length === 1 ? 'y' : 'ies'} detected with AI analysis and confidence scores
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {sortedAnomalies.map((anomaly, index) => (
            <div 
              key={index}
              className="flex items-start gap-4 p-4 border rounded-lg hover:bg-muted/50 transition-colors"
            >
              {/* Date and Metric */}
              <div className="flex-shrink-0">
                <div className="text-sm font-medium">{formatDate(anomaly.date)}</div>
                <div className="text-xs text-muted-foreground">{anomaly.metric}</div>
              </div>
              
              {/* Values and Deviation */}
              <div className="flex-1">
                <div className="flex items-center gap-4 mb-2">
                  <div className="flex items-center gap-2">
                    {getDeviationIcon(anomaly.value, anomaly.expected)}
                    <div>
                      <span className="text-sm font-medium">
                        {formatValue(anomaly.value)}
                      </span>
                      <span className="text-xs text-muted-foreground ml-2">
                        (expected: {formatValue(anomaly.expected)})
                      </span>
                    </div>
                  </div>
                  <div className="text-sm font-mono">
                    {getDeviationText(anomaly.value, anomaly.expected)}
                  </div>
                </div>
                
                {/* Explanation */}
                <p className="text-sm text-muted-foreground">{anomaly.explanation}</p>
              </div>
              
              {/* Badges */}
              <div className="flex-shrink-0 text-right">
                <Badge 
                  variant={getSeverityVariant(anomaly.severity)}
                  className="mb-2"
                >
                  {anomaly.severity} severity
                </Badge>
                <div className="text-xs text-muted-foreground">
                  {Math.round(anomaly.confidence * 100)}% confidence
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Summary Statistics */}
        <div className="mt-6 pt-4 border-t">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-lg font-bold text-red-500">
                {anomalies.filter(a => a.severity === 'high').length}
              </div>
              <div className="text-xs text-muted-foreground">High Severity</div>
            </div>
            <div>
              <div className="text-lg font-bold text-orange-500">
                {anomalies.filter(a => a.severity === 'medium').length}
              </div>
              <div className="text-xs text-muted-foreground">Medium Severity</div>
            </div>
            <div>
              <div className="text-lg font-bold text-yellow-500">
                {anomalies.filter(a => a.severity === 'low').length}
              </div>
              <div className="text-xs text-muted-foreground">Low Severity</div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
