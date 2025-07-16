
const Reports = () => {
  const [reports, setReports] = React.useState([]);
  const [selectedReport, setSelectedReport] = React.useState(null);
  const [loading, setLoading] = React.useState(false);
  const [generatingReport, setGeneratingReport] = React.useState(false);

  const reportTypes = [
    {
      id: 'user_activity',
      name: 'User Activity Report',
      description: 'Detailed analysis of user engagement and behavior',
      icon: '👥',
      estimatedTime: '2-3 minutes'
    },
    {
      id: 'model_performance',
      name: 'Model Performance Report',
      description: 'Performance metrics and usage statistics for all models',
      icon: '🤖',
      estimatedTime: '3-5 minutes'
    },
    {
      id: 'revenue_analysis',
      name: 'Revenue Analysis',
      description: 'Comprehensive financial performance and subscription metrics',
      icon: '💰',
      estimatedTime: '1-2 minutes'
    },
    {
      id: 'system_health',
      name: 'System Health Report',
      description: 'Technical performance, uptime, and infrastructure metrics',
      icon: '🔧',
      estimatedTime: '2-3 minutes'
    },
    {
      id: 'competitive_analysis',
      name: 'Competitive Analysis',
      description: 'Market positioning and competitive landscape insights',
      icon: '📊',
      estimatedTime: '5-7 minutes'
    }
  ];

  React.useEffect(() => {
    fetchReports();
  }, []);

  const fetchReports = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/reports');
      const data = await response.json();
      setReports(data.reports || []);
    } catch (error) {
      console.error('Error fetching reports:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateReport = async (reportType) => {
    try {
      setGeneratingReport(true);
      const response = await fetch('/api/reports/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: reportType.id })
      });
      const data = await response.json();
      
      if (data.success) {
        // Refresh reports list
        await fetchReports();
        alert(`${reportType.name} generated successfully!`);
      }
    } catch (error) {
      console.error('Error generating report:', error);
      alert('Error generating report. Please try again.');
    } finally {
      setGeneratingReport(false);
    }
  };

  const downloadReport = async (reportId, format = 'pdf') => {
    try {
      const response = await fetch(`/api/reports/${reportId}/download?format=${format}`);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = `report_${reportId}.${format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading report:', error);
    }
  };

  const ReportCard = ({ reportType }) => (
    <div className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex items-center space-x-3">
          <div className="text-3xl">{reportType.icon}</div>
          <div>
            <h3 className="text-lg font-semibold">{reportType.name}</h3>
            <p className="text-gray-600 text-sm">{reportType.description}</p>
            <p className="text-blue-600 text-xs mt-1">⏱ {reportType.estimatedTime}</p>
          </div>
        </div>
        <button
          onClick={() => generateReport(reportType)}
          disabled={generatingReport}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {generatingReport ? 'Generating...' : 'Generate'}
        </button>
      </div>
    </div>
  );

  const ReportHistoryItem = ({ report }) => (
    <div className="bg-white rounded-lg shadow p-4 flex items-center justify-between">
      <div className="flex items-center space-x-3">
        <div className="text-2xl">📄</div>
        <div>
          <h4 className="font-medium">{report.name}</h4>
          <p className="text-sm text-gray-600">Generated: {report.generated_at}</p>
          <p className="text-xs text-gray-500">Size: {report.size}</p>
        </div>
      </div>
      <div className="flex space-x-2">
        <button
          onClick={() => setSelectedReport(report)}
          className="px-3 py-1 text-blue-600 border border-blue-600 rounded hover:bg-blue-50"
        >
          View
        </button>
        <button
          onClick={() => downloadReport(report.id, 'pdf')}
          className="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700"
        >
          PDF
        </button>
        <button
          onClick={() => downloadReport(report.id, 'csv')}
          className="px-3 py-1 bg-gray-600 text-white rounded hover:bg-gray-700"
        >
          CSV
        </button>
      </div>
    </div>
  );

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
        <h1 className="text-3xl font-bold text-gray-900">Reports & Analytics</h1>
        <button
          onClick={fetchReports}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Refresh
        </button>
      </div>

      {/* Report Generation */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Generate New Report</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {reportTypes.map(reportType => (
            <ReportCard key={reportType.id} reportType={reportType} />
          ))}
        </div>
      </div>

      {/* Recent Reports */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Recent Reports</h2>
        {reports.length > 0 ? (
          <div className="space-y-3">
            {reports.map(report => (
              <ReportHistoryItem key={report.id} report={report} />
            ))}
          </div>
        ) : (
          <div className="bg-gray-50 rounded-lg p-8 text-center">
            <p className="text-gray-600">No reports generated yet. Create your first report above!</p>
          </div>
        )}
      </div>

      {/* Scheduled Reports */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Scheduled Reports</h2>
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded">
            <div>
              <h4 className="font-medium">Weekly Performance Summary</h4>
              <p className="text-sm text-gray-600">Every Monday at 9:00 AM</p>
            </div>
            <div className="flex space-x-2">
              <button className="px-3 py-1 text-blue-600 border border-blue-600 rounded hover:bg-blue-50">
                Edit
              </button>
              <button className="px-3 py-1 text-red-600 border border-red-600 rounded hover:bg-red-50">
                Disable
              </button>
            </div>
          </div>
          <button className="w-full p-4 border-2 border-dashed border-gray-300 rounded-lg text-gray-600 hover:border-blue-300 hover:text-blue-600">
            + Add Scheduled Report
          </button>
        </div>
      </div>

      {/* Report Modal */}
      {selectedReport && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-4xl max-h-[80vh] overflow-auto">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-semibold">{selectedReport.name}</h3>
              <button
                onClick={() => setSelectedReport(null)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>
            <div className="prose max-w-none">
              <p>Report content would be displayed here...</p>
              <p>Generated: {selectedReport.generated_at}</p>
              <p>This would show the actual report content with charts, tables, and insights.</p>
            </div>
            <div className="flex justify-end space-x-2 mt-6">
              <button
                onClick={() => downloadReport(selectedReport.id, 'pdf')}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Download PDF
              </button>
              <button
                onClick={() => setSelectedReport(null)}
                className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )</div>
      </div>
    </div>
  );
};

export default Reports;dow.Reports = Reports;
