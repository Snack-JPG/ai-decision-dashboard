'use client'

import { useState } from 'react'
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  ReferenceDot,
  Legend
} from 'recharts'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { ChevronDown, AlertTriangle } from "lucide-react"

interface TimeSeriesData {
  date: string
  [key: string]: any
}

interface Anomaly {
  date: string
  metric: string
  value: number
  expected: number
  severity: 'low' | 'medium' | 'high'
  explanation: string
  confidence: number
}

interface TimeSeriesChartProps {
  data: TimeSeriesData[]
  anomalies: Anomaly[]
}

function formatDate(dateStr: string): string {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  if (Number.isNaN(date.getTime())) return dateStr
  return date.toLocaleDateString('en-GB', { month: 'short', year: 'numeric' })
}

function formatValue(value: number): string {
  if (value >= 1000000) {
    return `${(value / 1000000).toFixed(1)}M`
  }
  if (value >= 1000) {
    return `${(value / 1000).toFixed(1)}K`
  }
  return value.toLocaleString()
}

function getSeverityColor(severity: string): string {
  switch (severity) {
    case 'high': return '#ef4444'
    case 'medium': return '#f97316'
    case 'low': return '#eab308'
    default: return '#6b7280'
  }
}

export function TimeSeriesChart({ data, anomalies }: TimeSeriesChartProps) {
  // Get numeric columns from the data
  const numericColumns = Object.keys(data[0] || {}).filter(key => {
    if (key === 'date') return false
    const value = data[0]?.[key]
    return typeof value === 'number'
  })

  const [selectedMetrics, setSelectedMetrics] = useState<string[]>(
    numericColumns.slice(0, 3) // Show first 3 metrics by default
  )

  const colors = [
    '#3b82f6', // blue
    '#10b981', // green
    '#f59e0b', // amber
    '#ef4444', // red
    '#8b5cf6', // purple
    '#06b6d4', // cyan
  ]

  // Prepare data with formatted dates
  const chartData = data.map(row => ({
    ...row,
    dateFormatted: formatDate(row.date)
  }))

  // Group anomalies by date for easy lookup
  const anomaliesByDate = anomalies.reduce((acc, anomaly) => {
    const dateKey = anomaly.date
    if (!acc[dateKey]) acc[dateKey] = []
    acc[dateKey].push(anomaly)
    return acc
  }, {} as Record<string, Anomaly[]>)

  const toggleMetric = (metric: string) => {
    setSelectedMetrics(prev => 
      prev.includes(metric) 
        ? prev.filter(m => m !== metric)
        : [...prev, metric]
    )
  }

  return (
    <div className="space-y-4">
      {/* Metric Selector */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium">Metrics:</span>
          <div className="flex gap-1">
            {selectedMetrics.map((metric, index) => (
              <Badge 
                key={metric} 
                variant="outline" 
                style={{ borderColor: colors[index % colors.length] }}
              >
                {metric}
              </Badge>
            ))}
          </div>
        </div>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" size="sm">
              Add Metric <ChevronDown className="ml-2 h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent>
            {numericColumns.map(metric => (
              <DropdownMenuItem 
                key={metric}
                onClick={() => toggleMetric(metric)}
                className="flex items-center justify-between"
              >
                {metric}
                {selectedMetrics.includes(metric) && (
                  <span className="text-xs text-muted-foreground">✓</span>
                )}
              </DropdownMenuItem>
            ))}
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      {/* Chart */}
      <div className="h-96">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
            <XAxis 
              dataKey="dateFormatted" 
              tick={{ fontSize: 12 }}
              className="text-muted-foreground"
            />
            <YAxis 
              tick={{ fontSize: 12 }}
              tickFormatter={formatValue}
              className="text-muted-foreground"
            />
            <Tooltip 
              labelFormatter={(value) => `Date: ${value}`}
              formatter={(value: number, name: string) => [formatValue(value), name]}
              contentStyle={{
                backgroundColor: 'hsl(var(--background))',
                border: '1px solid hsl(var(--border))',
                borderRadius: '8px',
                color: 'hsl(var(--foreground))'
              }}
            />
            <Legend />
            
            {selectedMetrics.map((metric, index) => (
              <Line
                key={metric}
                type="monotone"
                dataKey={metric}
                stroke={colors[index % colors.length]}
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 4, stroke: colors[index % colors.length], strokeWidth: 2 }}
                connectNulls
              />
            ))}

            {/* Anomaly markers */}
            {Object.entries(anomaliesByDate).map(([date, dateAnomalies]) => 
              dateAnomalies
                .filter(anomaly => selectedMetrics.includes(anomaly.metric))
                .map((anomaly, index) => (
                  <ReferenceDot
                    key={`${date}-${anomaly.metric}-${index}`}
                    x={formatDate(date)}
                    y={anomaly.value}
                    r={6}
                    fill={getSeverityColor(anomaly.severity)}
                    stroke="#ffffff"
                    strokeWidth={2}
                  />
                ))
            )}
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Anomaly Legend */}
      {anomalies.length > 0 && (
        <Card className="border-orange-200 bg-orange-50 dark:bg-orange-950/30 dark:border-orange-800">
          <CardHeader className="pb-3">
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-orange-600" />
              <CardTitle className="text-sm">Anomalies Detected</CardTitle>
            </div>
            <CardDescription className="text-xs">
              Dots on the chart indicate statistical anomalies with AI analysis
            </CardDescription>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="flex items-center gap-4 text-xs">
              <div className="flex items-center gap-1">
                <div className="w-3 h-3 rounded-full bg-red-500"></div>
                <span>High severity</span>
              </div>
              <div className="flex items-center gap-1">
                <div className="w-3 h-3 rounded-full bg-orange-500"></div>
                <span>Medium severity</span>
              </div>
              <div className="flex items-center gap-1">
                <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                <span>Low severity</span>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
