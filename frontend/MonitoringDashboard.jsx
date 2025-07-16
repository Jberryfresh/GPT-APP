import React, { useState, useEffect } from 'react';

const MonitoringDashboard = () => {
  const [systemHealth, setSystemHealth] = useState(null);
  const [performanceMetrics, setPerformanceMetrics] = useState(null);
  const [modelStats, setModelStats] = useState({});
  const [alerts, setAlerts] = useState([]);
  const [refreshInterval, setRefreshInterval] = useState(30); // seconds
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    fetchSystemHealth();
    fetchPerformanceMetrics();
    fetchAlerts();

    let interval;
    if (autoRefresh) {
      interval = setInterval(() => {
        fetchSystemHealth();
        fetchPerformanceMetrics();
      }, refreshInterval * 1000);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh, refreshInterval]);

  const fetchSystemHealth = async () => {
    try {
      const response = await fetch('/api/monitoring/system-health');
      if (response.ok) {
        const data = await response.json();
        setSystemHealth(data);
      }
    } catch (error) {
      console.error('Error fetching system health:', error);
    }
  };

  const fetchPerformanceMetrics = async () => {
    try {
      const response = await fetch('/api/monitoring/performance');
      if (response.ok) {
        const data = await response.json();
        setPerformanceMetrics(data);
        setModelStats(data.model_stats || {});
      }
    } catch (error) {
      console.error('Error fetching performance metrics:', error);
    }
  };

  const fetchAlerts = async () => {
    try {
      // Simulate alerts - replace with actual API call
      const mockAlerts = [
        {
          id: 1,
          type: 'warning',
          message: 'High memory usage detected (85%)',
          timestamp: new Date().toISOString(),
          severity: 'medium'
        },
        {
          id: 2,
          type: 'info',
          message: 'Model training completed successfully',
          timestamp: new Date(Date.now() - 300000).toISOString(),
          severity: 'low'
        }
      ];
      setAlerts(mockAlerts);
    } catch (error) {
      console.error('Error fetching alerts:', error);
    }
  };

  const StatusIndicator = ({ status, label }) => {
    const colors = {
      healthy: 'bg-green-500',
      warning: 'bg-yellow-500',
      critical: 'bg-red-500',
      unknown: 'bg-gray-500'
    };

    return (
      <div className="flex items-center space-x-2">
        <div className={`w-3 h-3 rounded-full ${colors[status] || colors.unknown}`}></div>
        <span className="text-sm text-gray-600">{label}</span>
      </div>
    );
  };

  const MetricCard = ({ title, value, unit, status, description }) => (
    <div className="bg-white p-6 rounded-lg border shadow-sm">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-medium text-gray-600">{title}</h3>
        {status && <StatusIndicator status={status} label="" />}
      </div>
      <div className="flex items-baseline">
        <p className="text-3xl font-bold text-gray-900">{value}</p>
        {unit && <span className="ml-1 text-sm text-gray-500">{unit}</span>}
      </div>
      {description && (
        <p className="mt-1 text-sm text-gray-600">{description}</p>
      )}
    </div>
  );

  const AlertCard = ({ alert }) => {
    const icons = {
      error: '🚨',
      warning: '⚠️',
      info: 'ℹ️',
      success: '✅'
    };

    const colors = {
      error: 'border-red-300 bg-red-50',
      warning: 'border-yellow-300 bg-yellow-50',
      info: 'border-blue-300 bg-blue-50',
      success: 'border-green-300 bg-green-50'
    };

    return (
      <div className={`p-4 rounded-lg border ${colors[alert.type] || colors.info}`}>
        <div className="flex items-start space-x-3">
          <span className="text-xl">{icons[alert.type] || icons.info}</span>
          <div className="flex-1">
            <p className="font-medium text-gray-900">{alert.message}</p>
            <p className="text-sm text-gray-600 mt-1">
              {new Date(alert.timestamp).toLocaleString()}
            </p>
          </div>
        </div>
      </div>
    );
  };

  if (!systemHealth || !performanceMetrics) {
    return (
      <div className="max-w-7xl mx-auto p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">System Monitoring</h1>
          <p className="text-gray-600 mt-1">Real-time system health and performance metrics</p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <label className="text-sm text-gray-600">Auto-refresh:</label>
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
          </div>
          <select
            value={refreshInterval}
            onChange={(e) => setRefreshInterval(parseInt(e.target.value))}
            className="text-sm border border-gray-300 rounded px-2 py-1"
            disabled={!autoRefresh}
          >
            <option value={10}>10s</option>
            <option value={30}>30s</option>
            <option value={60}>1m</option>
            <option value={300}>5m</option>
          </select>
        </div>
      </div>

      {/* System Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <MetricCard
          title="System Status"
          value={systemHealth.overall_status}
          status={systemHealth.overall_status}
          description="Overall system health"
        />
        <MetricCard
          title="Uptime"
          value={Math.round(performanceMetrics.uptime_seconds / 3600)}
          unit="hours"
          description="System uptime"
        />
        <MetricCard
          title="Total Requests"
          value={performanceMetrics.total_requests?.toLocaleString()}
          description="API requests processed"
        />
        <MetricCard
          title="Error Rate"
          value={performanceMetrics.error_rate?.toFixed(2)}
          unit="%"
          status={performanceMetrics.error_rate > 5 ? 'warning' : performanceMetrics.error_rate > 10 ? 'critical' : 'healthy'}
          description="Request error percentage"
        />
      </div>

      {/* Performance Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Response Times */}
        <div className="bg-white p-6 rounded-lg border shadow-sm">
          <h2 className="text-lg font-semibold mb-4">Response Times</h2>
          <div className="space-y-4">
            <div className="flex justify-between">
              <span className="text-gray-600">Average:</span>
              <span className="font-medium">{performanceMetrics.avg_response_time?.toFixed(2)}ms</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">P50:</span>
              <span className="font-medium">{performanceMetrics.p50_response_time?.toFixed(2)}ms</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">P95:</span>
              <span className="font-medium">{performanceMetrics.p95_response_time?.toFixed(2)}ms</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">P99:</span>
              <span className="font-medium">{performanceMetrics.p99_response_time?.toFixed(2)}ms</span>
            </div>
          </div>
        </div>

        {/* Memory Usage */}
        <div className="bg-white p-6 rounded-lg border shadow-sm">
          <h2 className="text-lg font-semibold mb-4">Memory Usage</h2>
          {systemHealth.memory && (
            <div className="space-y-4">
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-gray-600">Process Memory</span>
                  <span className="font-medium">
                    {systemHealth.memory.memory_usage.process_memory_gb?.toFixed(2)} GB
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full"
                    style={{ 
                      width: `${Math.min(
                        (systemHealth.memory.memory_usage.process_memory_gb / 8) * 100, 
                        100
                      )}%` 
                    }}
                  ></div>
                </div>
              </div>

              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-gray-600">Available Memory</span>
                  <span className="font-medium">
                    {systemHealth.memory.memory_usage.available_memory_gb?.toFixed(2)} GB
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-green-600 h-2 rounded-full"
                    style={{ 
                      width: `${Math.min(
                        (systemHealth.memory.memory_usage.available_memory_gb / 
                         systemHealth.memory.memory_usage.system_memory_gb) * 100, 
                        100
                      )}%` 
                    }}
                  ></div>
                </div>
              </div>

              {systemHealth.memory.warnings.length > 0 && (
                <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded">
                  <h4 className="text-sm font-medium text-yellow-800 mb-1">Memory Warnings:</h4>
                  {systemHealth.memory.warnings.map((warning, index) => (
                    <p key={index} className="text-sm text-yellow-700">• {warning}</p>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Model Statistics */}
      {Object.keys(modelStats).length > 0 && (
        <div className="bg-white p-6 rounded-lg border shadow-sm mb-8">
          <h2 className="text-lg font-semibold mb-4">Model Performance</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {Object.entries(modelStats).map(([modelId, stats]) => (
              <div key={modelId} className="p-4 bg-gray-50 rounded-lg">
                <h3 className="font-medium text-gray-900 mb-2">Model {modelId}</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Requests:</span>
                    <span className="font-medium">{stats.requests?.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Errors:</span>
                    <span className="font-medium">{stats.errors}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Avg Response:</span>
                    <span className="font-medium">{stats.avg_response_time?.toFixed(2)}ms</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Error Rate:</span>
                    <span className={`font-medium ${
                      (stats.errors / Math.max(stats.requests, 1)) > 0.1 ? 'text-red-600' : 'text-green-600'
                    }`}>
                      {((stats.errors / Math.max(stats.requests, 1)) * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Dependencies Status */}
      <div className="bg-white p-6 rounded-lg border shadow-sm mb-8">
        <h2 className="text-lg font-semibold mb-4">System Dependencies</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {systemHealth.dependencies && Object.entries(systemHealth.dependencies).map(([dep, available]) => (
            <StatusIndicator
              key={dep}
              status={available ? 'healthy' : 'critical'}
              label={dep.replace('_available', '').toUpperCase()}
            />
          ))}
        </div>
      </div>

      {/* Recent Alerts */}
      <div className="bg-white p-6 rounded-lg border shadow-sm">
        <h2 className="text-lg font-semibold mb-4">Recent Alerts</h2>
        {alerts.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <span className="text-4xl">✅</span>
            <p className="mt-2">No recent alerts. System is running smoothly!</p>
          </div>
        ) : (
          <div className="space-y-3">
            {alerts.map(alert => (
              <AlertCard key={alert.id} alert={alert} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default MonitoringDashboard;