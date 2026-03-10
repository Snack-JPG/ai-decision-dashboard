'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { ChevronDown, ArrowUpDown, TrendingUp, TrendingDown } from "lucide-react"

interface TimeSeriesData {
  date: string
  [key: string]: any
}

interface Metric {
  name: string
  value: number
  change_percent: number
  trend: 'up' | 'down' | 'stable'
  confidence: number
}

interface BreakdownTableProps {
  data: TimeSeriesData[]
  metrics: Metric[]
}

type SortDirection = 'asc' | 'desc'

function formatDate(dateStr: string): string {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  if (Number.isNaN(date.getTime())) return dateStr
  return date.toLocaleDateString('en-GB', { 
    day: '2-digit', 
    month: 'short', 
    year: 'numeric' 
  })
}

function formatValue(value: number): string {
  if (value == null || isNaN(value)) return '-'
  
  if (value >= 1000000) {
    return `${(value / 1000000).toFixed(1)}M`
  }
  if (value >= 1000) {
    return `${(value / 1000).toFixed(1)}K`
  }
  if (value < 1 && value > 0) {
    return `${(value * 100).toFixed(1)}%`
  }
  return value.toLocaleString()
}

function calculateChange(current: number, previous: number): number {
  if (!previous || previous === 0) return 0
  return ((current - previous) / previous) * 100
}

function getChangeIcon(change: number) {
  if (Math.abs(change) < 0.1) return null
  return change > 0 ? (
    <TrendingUp className="h-3 w-3 text-green-500" />
  ) : (
    <TrendingDown className="h-3 w-3 text-red-500" />
  )
}

function getChangeColor(change: number): string {
  if (Math.abs(change) < 0.1) return 'text-muted-foreground'
  return change > 0 ? 'text-green-600' : 'text-red-600'
}

export function BreakdownTable({ data, metrics }: BreakdownTableProps) {
  const [sortColumn, setSortColumn] = useState<string>('date')
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc')
  const [visibleColumns, setVisibleColumns] = useState<string[]>(() => {
    // Get all numeric columns
    const numericColumns = Object.keys(data[0] || {}).filter(key => {
      if (key === 'date') return false
      const value = data[0]?.[key]
      return typeof value === 'number'
    })
    // Show first 4 columns by default
    return numericColumns.slice(0, 4)
  })

  // Get all available columns
  const allColumns = Object.keys(data[0] || {}).filter(key => key !== 'date')
  const numericColumns = allColumns.filter(key => {
    const value = data[0]?.[key]
    return typeof value === 'number'
  })

  if (data.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Data Breakdown</CardTitle>
          <CardDescription>No time-series rows are available for this dataset.</CardDescription>
        </CardHeader>
      </Card>
    )
  }

  const chronologicalRows = [...data].sort(
    (a, b) => new Date(a.date).getTime() - new Date(b.date).getTime()
  )

  // Sort data
  const sortedData = [...data].sort((a, b) => {
    let aValue = a[sortColumn]
    let bValue = b[sortColumn]
    
    if (sortColumn === 'date') {
      aValue = new Date(aValue).getTime()
      bValue = new Date(bValue).getTime()
    }
    
    if (typeof aValue === 'string') {
      aValue = aValue.toLowerCase()
      bValue = bValue.toLowerCase()
    }
    
    const comparison = aValue < bValue ? -1 : aValue > bValue ? 1 : 0
    return sortDirection === 'asc' ? comparison : -comparison
  })

  const handleSort = (column: string) => {
    if (sortColumn === column) {
      setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc')
    } else {
      setSortColumn(column)
      setSortDirection('desc')
    }
  }

  const toggleColumn = (column: string) => {
    setVisibleColumns(prev => 
      prev.includes(column) 
        ? prev.filter(c => c !== column)
        : [...prev, column]
    )
  }

  // Calculate changes from previous period
  const dataWithChanges: Array<TimeSeriesData & { changes: Record<string, number> }> = sortedData.map((row, index) => {
    const changes: Record<string, number> = {}
    const previousRow = sortDirection === 'desc' ? sortedData[index + 1] : sortedData[index - 1]
    
    visibleColumns.forEach(column => {
      if (previousRow) {
        changes[column] = calculateChange(row[column], previousRow[column])
      }
    })
    
    return { ...row, changes }
  })

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Data Breakdown</CardTitle>
            <CardDescription>
              Detailed view of {data.length} data points with period-over-period changes
            </CardDescription>
          </div>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm">
                Columns ({visibleColumns.length}) <ChevronDown className="ml-2 h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent>
              {numericColumns.map(column => (
                <DropdownMenuItem 
                  key={column}
                  onClick={() => toggleColumn(column)}
                  className="flex items-center justify-between"
                >
                  {column}
                  {visibleColumns.includes(column) && (
                    <span className="text-xs text-muted-foreground">✓</span>
                  )}
                </DropdownMenuItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left p-2">
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    onClick={() => handleSort('date')}
                    className="h-auto p-0 font-medium hover:bg-transparent"
                  >
                    Date
                    <ArrowUpDown className="ml-2 h-3 w-3" />
                  </Button>
                </th>
                {visibleColumns.map(column => (
                  <th key={column} className="text-left p-2">
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      onClick={() => handleSort(column)}
                      className="h-auto p-0 font-medium hover:bg-transparent"
                    >
                      {column}
                      <ArrowUpDown className="ml-2 h-3 w-3" />
                    </Button>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {dataWithChanges.map((row, index) => (
                <tr key={index} className="border-b hover:bg-muted/50 transition-colors">
                  <td className="p-2 font-medium">
                    {formatDate(row.date)}
                  </td>
                  {visibleColumns.map(column => {
                    const value = row[column]
                    const change = row.changes[column]
                    
                    return (
                      <td key={column} className="p-2">
                        <div className="flex items-center justify-between">
                          <span className="font-medium">
                            {formatValue(value)}
                          </span>
                          {change != null && Math.abs(change) > 0.1 && (
                            <div className={`flex items-center gap-1 text-xs ${getChangeColor(change)}`}>
                              {getChangeIcon(change)}
                              <span>
                                {change > 0 ? '+' : ''}{change.toFixed(1)}%
                              </span>
                            </div>
                          )}
                        </div>
                      </td>
                    )
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Summary Row */}
        <div className="mt-4 pt-4 border-t">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-lg font-bold">
                {data.length}
              </div>
              <div className="text-xs text-muted-foreground">Total Records</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-bold">
                {formatDate(chronologicalRows[0]?.date)} - {formatDate(chronologicalRows[chronologicalRows.length - 1]?.date)}
              </div>
              <div className="text-xs text-muted-foreground">Date Range</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-bold">
                {visibleColumns.length}/{numericColumns.length}
              </div>
              <div className="text-xs text-muted-foreground">Columns Shown</div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
