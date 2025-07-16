
# Analytics System Documentation

## Overview

The analytics system provides comprehensive insights into your Custom GPT application's performance, user behavior, and business metrics. It's built with a modular architecture that supports real-time data collection, processing, and visualization.

## Architecture

### Components

1. **Backend Analytics API** (`simple_app.py`)
   - Data collection endpoints
   - Metrics calculation
   - Export functionality

2. **Frontend Analytics Dashboard** (`Analytics.jsx`)
   - Interactive visualizations
   - Real-time updates
   - Filtering and time range selection

3. **Reports System** (`Reports.jsx`)
   - Automated report generation
   - Export capabilities
   - Historical data analysis

## API Endpoints

### Core Analytics Endpoint
```
GET /api/analytics?range={timeRange}
```

**Parameters:**
- `range`: Time range for data (1d, 7d, 30d, 90d)

**Response Structure:**
```json
{
  "overview": {
    "totalUsers": 1234,
    "activeUsers": 567,
    "totalModels": 45,
    "totalConversations": 8901,
    "revenue": 12500,
    "growth": 8.5
  },
  "userMetrics": {
    "newUsers": [/* time series data */],
    "activeUsers": [/* time series data */],
    "retention": [/* retention data */]
  },
  "modelMetrics": {
    "modelUsage": [/* usage statistics */],
    "performanceStats": [/* performance data */],
    "trainingMetrics": [/* training statistics */]
  },
  "revenueMetrics": {
    "revenue": [/* revenue over time */],
    "subscriptions": [/* subscription data */],
    "churn": [/* churn analysis */]
  },
  "systemMetrics": {
    "apiCalls": [/* API usage */],
    "responseTime": [/* performance metrics */],
    "errorRate": [/* error statistics */]
  }
}
```

### Revenue Analytics
```
GET /api/analytics/revenue
```

Returns detailed revenue and subscription analytics including MRR, ARR, churn rates, and tier-based breakdowns.

### Export Analytics
```
GET /api/analytics/export/{format}?range={timeRange}
```

**Formats:** `csv`, `json`, `pdf`

Exports analytics data in the specified format for external analysis.

## Dashboard Features

### Overview Metrics
- **Total Users**: Cumulative user count
- **Active Users**: Users active in the selected time period
- **Custom Models**: Number of trained custom models
- **Conversations**: Total conversation count
- **Revenue**: Total revenue generated
- **Growth Rate**: Percentage growth rate

### Charts and Visualizations

#### User Metrics
- **New Users Over Time**: Track user acquisition trends
- **Active Users**: Monitor user engagement patterns
- **User Retention**: Analyze user retention rates

#### Model Metrics
- **Model Usage**: Track which models are most popular
- **Performance Stats**: Monitor model performance metrics
- **Training Metrics**: Analyze training success rates

#### Revenue Metrics
- **Revenue Trend**: Track revenue over time
- **Subscription Analysis**: Monitor subscription patterns
- **Churn Analysis**: Identify churn patterns

#### System Metrics
- **API Calls**: Monitor API usage patterns
- **Response Time**: Track system performance
- **Error Rate**: Monitor system reliability

### Interactive Features

#### Time Range Selection
- Last 24 Hours
- Last 7 Days
- Last 30 Days
- Last 90 Days

#### Real-time Updates
- Automatic data refresh
- Manual refresh capability
- Live performance monitoring

#### Data Export
- CSV format for spreadsheet analysis
- JSON format for programmatic access
- PDF format for reporting

## Reports System

### Report Types

1. **User Analytics Report**
   - User acquisition trends
   - Engagement metrics
   - Demographic analysis

2. **Model Performance Report**
   - Model usage statistics
   - Performance benchmarks
   - Training success rates

3. **Revenue Report**
   - Financial performance
   - Subscription analysis
   - Revenue forecasting

4. **System Performance Report**
   - Technical metrics
   - Uptime statistics
   - Performance optimization recommendations

### Report Generation

Reports can be generated on-demand or scheduled for automatic generation. Each report includes:

- Executive summary
- Detailed metrics
- Trend analysis
- Recommendations
- Data visualizations

### Report Formats

- **PDF**: Professional formatted reports
- **CSV**: Raw data for analysis
- **JSON**: Structured data for integration

## Data Collection

### Automatic Data Collection

The system automatically collects data on:

- User registrations and logins
- Model training events
- Chat interactions
- API usage
- System performance metrics
- Revenue transactions

### Data Sources

1. **Database Events**: User actions, model operations
2. **API Logs**: Request/response metrics
3. **System Monitoring**: Performance data
4. **Billing System**: Revenue and subscription data

## Metrics Definitions

### User Metrics

- **Total Users**: All registered users
- **Active Users**: Users with activity in the time period
- **New Users**: Users registered in the time period
- **Retention Rate**: Percentage of users who return

### Model Metrics

- **Model Usage**: Number of interactions per model
- **Training Success Rate**: Percentage of successful training jobs
- **Model Performance**: Quality metrics for model outputs

### Revenue Metrics

- **MRR (Monthly Recurring Revenue)**: Predictable monthly revenue
- **ARR (Annual Recurring Revenue)**: Projected annual revenue
- **Churn Rate**: Percentage of customers who cancel subscriptions
- **LTV (Lifetime Value)**: Average customer lifetime value

### System Metrics

- **API Response Time**: Average response time for API calls
- **Error Rate**: Percentage of failed requests
- **Uptime**: System availability percentage

## Implementation Details

### Data Processing Pipeline

1. **Collection**: Raw events captured from various sources
2. **Processing**: Data cleaned, normalized, and aggregated
3. **Storage**: Processed data stored in optimized format
4. **Retrieval**: Data retrieved and formatted for presentation

### Performance Optimization

- **Caching**: Frequently accessed data cached for fast retrieval
- **Aggregation**: Pre-calculated metrics for common queries
- **Indexing**: Database indexes optimized for analytics queries

### Security and Privacy

- **Data Anonymization**: Personal data anonymized in analytics
- **Access Control**: Role-based access to analytics data
- **Audit Logging**: All analytics access logged for compliance

## Usage Examples

### Viewing Analytics Dashboard

1. Navigate to Analytics tab in the application
2. Select desired time range
3. Review overview metrics
4. Explore detailed charts
5. Export data if needed

### Generating Reports

1. Go to Reports section
2. Select report type
3. Choose time range and parameters
4. Generate report
5. Download in preferred format

### API Integration

```javascript
// Fetch analytics data
const response = await fetch('/api/analytics?range=7d');
const analytics = await response.json();

// Display user metrics
console.log('Active Users:', analytics.overview.activeUsers);
console.log('Revenue:', analytics.overview.revenue);
```

## Troubleshooting

### Common Issues

1. **Slow Loading**: Check network connection and server performance
2. **Missing Data**: Verify data collection is properly configured
3. **Export Failures**: Ensure sufficient permissions and disk space

### Performance Tips

- Use appropriate time ranges for better performance
- Export large datasets during off-peak hours
- Cache frequently accessed reports

## Future Enhancements

### Planned Features

1. **Custom Dashboards**: User-configurable dashboard layouts
2. **Advanced Filtering**: More granular data filtering options
3. **Predictive Analytics**: ML-powered forecasting
4. **Real-time Alerts**: Automated alerts for important metrics
5. **Mobile Optimization**: Better mobile dashboard experience

### Integration Opportunities

1. **Third-party Analytics**: Google Analytics, Mixpanel integration
2. **Business Intelligence**: Tableau, Power BI connectors
3. **Slack/Teams**: Automated report delivery
4. **Email Reports**: Scheduled email reports

## API Reference

### Authentication

All analytics endpoints require authentication:

```
Authorization: Bearer <your_api_token>
```

### Rate Limits

- Analytics API: 100 requests per minute
- Export API: 10 requests per minute

### Error Handling

Standard HTTP status codes:
- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 429: Rate Limited
- 500: Server Error

## Contributing

To extend the analytics system:

1. Add new metrics in `simple_app.py`
2. Update frontend components in `Analytics.jsx`
3. Add new report types in `Reports.jsx`
4. Update this documentation

## Support

For questions about the analytics system:
- Check this documentation first
- Review the code in `simple_app.py` and `Analytics.jsx`
- Test API endpoints using the provided examples
