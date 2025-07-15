
import { useState, useEffect } from 'react'
import { 
  Activity, 
  AlertTriangle, 
  Clock, 
  Database,
  Brain,
  TrendingUp,
  Server,
  Zap,
  RefreshCw,
  Download
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

export default function MonitoringDashboard() {
  const [metrics, setMetrics] = useState(null)
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)
  const [autoRefresh, setAutoRefresh] = useState(true)

  useEffect(() => {
    fetchMetrics()
    
    if (autoRefresh) {
      const interval = setInterval(fetchMetrics, 30000) // Refresh every 30 seconds
      return () => clearInterval(interval)
    }
  }, [autoRefresh])

  const fetchMetrics = async () => {
    try {
      const token = localStorage.getItem('access_token')
      
      const [metricsResponse, alertsResponse] = await Promise.all([
        fetch('/api/v1/metrics', {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch('/api/v1/alerts', {
          headers: { 'Authorization': `Bearer ${token}` }
        })
      ])

      if (metricsResponse.ok) {
        const metricsData = await metricsResponse.json()
        setMetrics(metricsData.data)
      }

      if (alertsResponse.ok) {
        const alertsData = await alertsResponse.json()
        setAlerts(alertsData.data)
      }
    } catch (error) {
      console.error('Failed to fetch monitoring data:', error)
    } finally {
      setLoading(false)
    }
  }

  const exportMetrics = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch('/api/v1/monitoring/export', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `metrics_${Date.now()}.json`
        a.click()
        window.URL.revokeObjectURL(url)
      }
    } catch (error) {
      console.error('Failed to export metrics:', error)
    }
  }

  const getAlertBadgeColor = (type) => {
    const colors = {
      'high_response_time': 'destructive',
      'high_error_rate': 'destructive',
      'high_cpu_usage': 'secondary',
      'high_memory_usage': 'secondary'
    }
    return colors[type] || 'default'
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin text-gray-400" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">System Monitoring</h1>
          <p className="text-gray-600">Real-time performance and health metrics</p>
        </div>
        <div className="flex items-center space-x-3">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setAutoRefresh(!autoRefresh)}
          >
            <Activity className={`h-4 w-4 mr-2 ${autoRefresh ? 'text-green-500' : 'text-gray-400'}`} />
            Auto Refresh
          </Button>
          <Button variant="outline" size="sm" onClick={fetchMetrics}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button variant="outline" size="sm" onClick={exportMetrics}>
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Alerts */}
      {alerts.length > 0 && (
        <Card className="border-red-200 bg-red-50">
          <CardHeader>
            <CardTitle className="text-red-800 flex items-center">
              <AlertTriangle className="h-5 w-5 mr-2" />
              Active Alerts ({alerts.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {alerts.slice(0, 5).map((alert, index) => (
                <div key={index} className="flex items-center justify-between p-2 bg-white rounded border">
                  <div className="flex items-center space-x-3">
                    <Badge variant={getAlertBadgeColor(alert.type)}>
                      {alert.type.replace('_', ' ').toUpperCase()}
                    </Badge>
                    <span className="text-sm">
                      {alert.endpoint && `${alert.endpoint}: `}
                      {alert.value?.toFixed(2)} exceeds threshold {alert.threshold}
                    </span>
                  </div>
                  <span className="text-xs text-gray-500">
                    {new Date(alert.timestamp).toLocaleTimeString()}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="api">API Metrics</TabsTrigger>
          <TabsTrigger value="database">Database</TabsTrigger>
          <TabsTrigger value="models">Models</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          {/* System Overview */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">CPU Usage</CardTitle>
                <Server className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {metrics?.api_metrics?.system?.cpu_avg?.toFixed(1) || 0}%
                </div>
                <div className={`text-xs ${
                  (metrics?.api_metrics?.system?.cpu_avg || 0) > 80 ? 'text-red-600' : 'text-gray-600'
                }`}>
                  System CPU usage
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Memory Usage</CardTitle>
                <Database className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {metrics?.api_metrics?.system?.memory_avg?.toFixed(1) || 0}%
                </div>
                <div className={`text-xs ${
                  (metrics?.api_metrics?.system?.memory_avg || 0) > 85 ? 'text-red-600' : 'text-gray-600'
                }`}>
                  System memory usage
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Active Requests</CardTitle>
                <Activity className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {metrics?.api_metrics?.system?.active_requests || 0}
                </div>
                <div className="text-xs text-gray-600">
                  Currently processing
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Error Rate</CardTitle>
                <AlertTriangle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {(() => {
                    const totalRequests = Object.values(metrics?.api_metrics?.requests || {}).reduce((a, b) => a + b, 0)
                    const totalErrors = metrics?.api_metrics?.errors?.total_count || 0
                    const errorRate = totalRequests > 0 ? (totalErrors / totalRequests) * 100 : 0
                    return errorRate.toFixed(2)
                  })()}%
                </div>
                <div className="text-xs text-gray-600">
                  Error percentage
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="api" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Response Times</CardTitle>
                <CardDescription>Average response times by endpoint</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {Object.entries(metrics?.api_metrics?.response_times || {}).map(([endpoint, stats]) => (
                    <div key={endpoint} className="flex justify-between items-center">
                      <div>
                        <div className="font-medium text-sm">{endpoint}</div>
                        <div className="text-xs text-gray-500">{stats.count} requests</div>
                      </div>
                      <div className="text-right">
                        <div className="font-medium">{stats.avg.toFixed(0)}ms</div>
                        <div className="text-xs text-gray-500">P95: {stats.p95.toFixed(0)}ms</div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Status Codes</CardTitle>
                <CardDescription>HTTP response status distribution</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {Object.entries(metrics?.api_metrics?.status_codes || {}).map(([code, count]) => (
                    <div key={code} className="flex justify-between items-center">
                      <Badge variant={code.startsWith('2') ? 'default' : code.startsWith('4') ? 'secondary' : 'destructive'}>
                        {code}
                      </Badge>
                      <span className="font-medium">{count}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="database" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Query Performance</CardTitle>
                <CardDescription>Database query metrics</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between">
                    <span>Total Queries</span>
                    <span className="font-medium">{metrics?.database_metrics?.query_count || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Avg Query Time</span>
                    <span className="font-medium">
                      {metrics?.database_metrics?.avg_query_time?.toFixed(2) || 0}ms
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>P95 Query Time</span>
                    <span className="font-medium">
                      {metrics?.database_metrics?.p95_query_time?.toFixed(2) || 0}ms
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Slow Queries</span>
                    <span className="font-medium text-orange-600">
                      {metrics?.database_metrics?.slow_query_count || 0}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Recent Slow Queries</CardTitle>
                <CardDescription>Queries taking over 1 second</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {(metrics?.database_metrics?.recent_slow_queries || []).map((query, index) => (
                    <div key={index} className="p-2 bg-orange-50 rounded border border-orange-200">
                      <div className="text-sm font-medium">{query.execution_time.toFixed(2)}ms</div>
                      <div className="text-xs text-gray-600 truncate">{query.query}</div>
                    </div>
                  ))}
                  {(!metrics?.database_metrics?.recent_slow_queries?.length) && (
                    <p className="text-sm text-gray-500">No recent slow queries</p>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="models" className="space-y-4">
          <div className="grid grid-cols-1 gap-6">
            {Object.entries(metrics?.model_metrics || {}).map(([modelId, stats]) => (
              <Card key={modelId}>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Brain className="h-5 w-5 mr-2" />
                    {modelId}
                  </CardTitle>
                  <CardDescription>Model performance metrics</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div>
                      <div className="text-2xl font-bold">{stats.total_requests}</div>
                      <div className="text-xs text-gray-600">Total Requests</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-red-600">{stats.error_count}</div>
                      <div className="text-xs text-gray-600">Errors</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold">{stats.avg_tokens_per_second?.toFixed(1)}</div>
                      <div className="text-xs text-gray-600">Avg Tokens/sec</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold">
                        {((1 - stats.error_count / stats.total_requests) * 100).toFixed(1)}%
                      </div>
                      <div className="text-xs text-gray-600">Success Rate</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
            {Object.keys(metrics?.model_metrics || {}).length === 0 && (
              <Card>
                <CardContent className="p-6 text-center">
                  <Brain className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500">No model metrics available yet</p>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
