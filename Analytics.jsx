
const Analytics = () => {
  const [analyticsData, setAnalyticsData] = React.useState({
    overview: {
      totalUsers: 0,
      activeUsers: 0,
      totalModels: 0,
      totalConversations: 0,
      revenue: 0,
      growth: 0
    },
    userMetrics: {
      newUsers: [],
      activeUsers: [],
      retention: []
    },
    modelMetrics: {
      modelUsage: [],
      performanceStats: [],
      trainingMetrics: []
    },
    revenueMetrics: {
      revenue: [],
      subscriptions: [],
      churn: []
    },
    systemMetrics: {
      apiCalls: [],
      responseTime: [],
      errorRate: []
    }
  });
  
  const [timeRange, setTimeRange] = React.useState('7d');
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    fetchAnalyticsData();
  }, [timeRange]);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/analytics?range=${timeRange}`);
      const data = await response.json();
      setAnalyticsData(data);
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const MetricCard = ({ title, value, change, icon, color = "blue" }) => (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          {change && (
            <p className={`text-sm ${change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {change >= 0 ? '↗' : '↘'} {Math.abs(change)}%
            </p>
          )}
        </div>
        <div className={`p-3 rounded-full bg-${color}-100`}>
          <span className={`text-${color}-600 text-xl`}>{icon}</span>
        </div>
      </div>
    </div>
  );

  const ChartContainer = ({ title, children }) => (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold mb-4">{title}</h3>
      {children}
    </div>
  );

  const SimpleChart = ({ data, color = "#3b82f6" }) => {
    if (!data || data.length === 0) {
      return <div className="text-gray-500 text-center py-4">No data available</div>;
    }

    const max = Math.max(...data);
    const min = Math.min(...data);
    const range = max - min;

    return (
      <div className="h-32 flex items-end space-x-1">
        {data.map((value, index) => (
          <div
            key={index}
            className="flex-1 bg-blue-500 rounded-t opacity-80"
            style={{
              height: `${range === 0 ? 50 : ((value - min) / range) * 100}%`,
              backgroundColor: color
            }}
            title={`Value: ${value}`}
          />
        ))}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
        <div className="flex space-x-2">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="1d">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
            <option value="90d">Last 90 Days</option>
          </select>
          <button
            onClick={fetchAnalyticsData}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Refresh
          </button>
        </div>
      </div>

      {/* Overview Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-6">
        <MetricCard
          title="Total Users"
          value={analyticsData.overview.totalUsers.toLocaleString()}
          change={analyticsData.overview.growth}
          icon="👥"
          color="blue"
        />
        <MetricCard
          title="Active Users"
          value={analyticsData.overview.activeUsers.toLocaleString()}
          icon="🟢"
          color="green"
        />
        <MetricCard
          title="Custom Models"
          value={analyticsData.overview.totalModels.toLocaleString()}
          icon="🤖"
          color="purple"
        />
        <MetricCard
          title="Conversations"
          value={analyticsData.overview.totalConversations.toLocaleString()}
          icon="💬"
          color="indigo"
        />
        <MetricCard
          title="Revenue"
          value={`$${analyticsData.overview.revenue.toLocaleString()}`}
          icon="💰"
          color="yellow"
        />
        <MetricCard
          title="Growth Rate"
          value={`${analyticsData.overview.growth}%`}
          icon="📈"
          color="green"
        />
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* User Metrics */}
        <ChartContainer title="New Users Over Time">
          <SimpleChart data={analyticsData.userMetrics.newUsers} color="#3b82f6" />
        </ChartContainer>

        <ChartContainer title="Active Users">
          <SimpleChart data={analyticsData.userMetrics.activeUsers} color="#10b981" />
        </ChartContainer>

        <ChartContainer title="Model Usage">
          <SimpleChart data={analyticsData.modelMetrics.modelUsage} color="#8b5cf6" />
        </ChartContainer>

        <ChartContainer title="Revenue Trend">
          <SimpleChart data={analyticsData.revenueMetrics.revenue} color="#f59e0b" />
        </ChartContainer>

        <ChartContainer title="API Response Time (ms)">
          <SimpleChart data={analyticsData.systemMetrics.responseTime} color="#ef4444" />
        </ChartContainer>

        <ChartContainer title="System Performance">
          <SimpleChart data={analyticsData.systemMetrics.apiCalls} color="#06b6d4" />
        </ChartContainer>
      </div>

      {/* Detailed Tables */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Models */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Top Performing Models</h3>
          <div className="space-y-3">
            {analyticsData.modelMetrics.performanceStats.slice(0, 5).map((model, index) => (
              <div key={index} className="flex justify-between items-center p-3 bg-gray-50 rounded">
                <div>
                  <p className="font-medium">{model.name || `Model ${index + 1}`}</p>
                  <p className="text-sm text-gray-600">{model.type || 'Custom GPT'}</p>
                </div>
                <div className="text-right">
                  <p className="font-bold">{model.usage || Math.floor(Math.random() * 1000)} uses</p>
                  <p className="text-sm text-gray-600">{model.rating || '4.8'} ⭐</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* User Engagement */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">User Engagement</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Average Session Duration</span>
              <span className="font-bold">24 minutes</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Messages per Session</span>
              <span className="font-bold">12.3</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">User Retention (30d)</span>
              <span className="font-bold">68%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Daily Active Users</span>
              <span className="font-bold">{analyticsData.overview.activeUsers}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Conversion Rate</span>
              <span className="font-bold">3.2%</span>
            </div>
          </div>
        </div>
      </div>

      {/* Export Options */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Export Analytics</h3>
        <div className="flex space-x-4">
          <button className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700">
            📊 Export to CSV
          </button>
          <button className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700">
            📄 Generate PDF Report
          </button>
          <button className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700">
            📈 Export Charts
          </button>
        </div>
      </div>
    </div>
  );
};

window.Analytics = Analytics;
