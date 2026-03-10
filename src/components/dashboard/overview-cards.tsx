'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { TrendingUp, TrendingDown, Activity, AlertTriangle, Brain } from "lucide-react"

interface Metric {
  name: string
  value: number
  change_percent: number
  trend: 'up' | 'down' | 'stable'
  confidence: number
}

interface Insight {
  type: 'trend' | 'anomaly' | 'correlation' | 'seasonal'
  title: string
  description: string
  confidence: number
  impact: 'low' | 'medium' | 'high'
}

interface OverviewCardsProps {
  metrics: Metric[]
  insights: Insight[]
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

function getTrendIcon(trend: string, changePercent: number) {
  if (trend === 'up') {
    return <TrendingUp className="h-4 w-4 text-green-500" />
  } else if (trend === 'down') {
    return <TrendingDown className="h-4 w-4 text-red-500" />
  } else {
    return <Activity className="h-4 w-4 text-blue-500" />
  }
}

function getTrendColor(trend: string, changePercent: number): string {
  if (trend === 'up') {
    return changePercent > 0 ? 'text-green-500' : 'text-red-500'
  } else if (trend === 'down') {
    return changePercent < 0 ? 'text-green-500' : 'text-red-500'
  } else {
    return 'text-muted-foreground'
  }
}

export function OverviewCards({ metrics, insights }: OverviewCardsProps) {
  // Get high-impact insights for the overview
  const highImpactInsights = insights.filter(i => i.impact === 'high').slice(0, 2)
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {/* Metric Cards */}
      {metrics.slice(0, 3).map((metric, index) => (
        <Card key={index}>
          <CardHeader className="pb-2">
            <CardDescription className="text-xs font-medium">
              {metric.name}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold">
                  {formatValue(metric.value)}
                </div>
                <div className={`text-sm flex items-center gap-1 ${getTrendColor(metric.trend, metric.change_percent)}`}>
                  {getTrendIcon(metric.trend, metric.change_percent)}
                  {metric.change_percent > 0 ? '+' : ''}{metric.change_percent.toFixed(1)}%
                </div>
              </div>
              <Badge variant="outline" className="text-xs">
                {Math.round(metric.confidence * 100)}%
              </Badge>
            </div>
          </CardContent>
        </Card>
      ))}

      {/* Insights Card */}
      <Card>
        <CardHeader className="pb-2">
          <CardDescription className="text-xs font-medium flex items-center gap-1">
            <Brain className="h-3 w-3" />
            Key Insights
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {highImpactInsights.length > 0 ? (
              highImpactInsights.map((insight, index) => (
                <div key={index} className="text-sm">
                  <div className="flex items-center gap-1 mb-1">
                    {insight.type === 'anomaly' && <AlertTriangle className="h-3 w-3 text-orange-500" />}
                    {insight.type === 'trend' && <TrendingUp className="h-3 w-3 text-blue-500" />}
                    <span className="font-medium text-xs">{insight.title}</span>
                  </div>
                  <p className="text-xs text-muted-foreground line-clamp-2">
                    {insight.description}
                  </p>
                </div>
              ))
            ) : (
              <div className="text-center py-2">
                <Activity className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
                <p className="text-xs text-muted-foreground">
                  AI analysis in progress
                </p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}