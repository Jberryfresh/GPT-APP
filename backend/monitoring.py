
"""
Advanced Monitoring and Metrics Collection
==========================================

Comprehensive monitoring system for the Custom GPT API including
performance metrics, error tracking, and system health monitoring.
"""

import time
import psutil
import logging
from datetime import datetime, timedelta
from functools import wraps
from collections import defaultdict, deque
from threading import Lock
import json
from flask import request, g, current_app
from database import db, UsageRecord
import traceback

logger = logging.getLogger(__name__)

class MetricsCollector:
    """Collects and stores application metrics."""
    
    def __init__(self):
        self.metrics = defaultdict(lambda: defaultdict(int))
        self.response_times = defaultdict(deque)
        self.error_counts = defaultdict(int)
        self.active_requests = 0
        self.lock = Lock()
        
        # Performance tracking
        self.cpu_usage = deque(maxlen=100)
        self.memory_usage = deque(maxlen=100)
        self.request_rate = deque(maxlen=60)  # per minute
        
        # Error tracking
        self.recent_errors = deque(maxlen=50)
        self.error_patterns = defaultdict(int)
        
    def record_request(self, endpoint, method, status_code, response_time):
        """Record API request metrics."""
        with self.lock:
            key = f"{method}:{endpoint}"
            self.metrics['requests'][key] += 1
            self.metrics['status_codes'][status_code] += 1
            
            # Store response times (keep last 1000)
            if len(self.response_times[key]) >= 1000:
                self.response_times[key].popleft()
            self.response_times[key].append(response_time)
            
    def record_error(self, error, endpoint=None, user_id=None):
        """Record error occurrence."""
        with self.lock:
            error_info = {
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(error),
                'type': type(error).__name__,
                'endpoint': endpoint,
                'user_id': str(user_id) if user_id else None,
                'traceback': traceback.format_exc()
            }
            
            self.recent_errors.append(error_info)
            self.error_counts[type(error).__name__] += 1
            
            # Track error patterns
            if endpoint:
                self.error_patterns[f"{endpoint}:{type(error).__name__}"] += 1
                
    def record_system_metrics(self):
        """Record system performance metrics."""
        with self.lock:
            self.cpu_usage.append(psutil.cpu_percent())
            self.memory_usage.append(psutil.virtual_memory().percent)
            
    def get_metrics_summary(self):
        """Get comprehensive metrics summary."""
        with self.lock:
            # Calculate averages and percentiles
            response_time_stats = {}
            for endpoint, times in self.response_times.items():
                if times:
                    sorted_times = sorted(times)
                    response_time_stats[endpoint] = {
                        'avg': sum(times) / len(times),
                        'p50': sorted_times[len(times) // 2],
                        'p95': sorted_times[int(len(times) * 0.95)],
                        'p99': sorted_times[int(len(times) * 0.99)],
                        'count': len(times)
                    }
            
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'requests': dict(self.metrics['requests']),
                'status_codes': dict(self.metrics['status_codes']),
                'response_times': response_time_stats,
                'errors': {
                    'total_count': sum(self.error_counts.values()),
                    'by_type': dict(self.error_counts),
                    'patterns': dict(self.error_patterns),
                    'recent': list(self.recent_errors)[-10:]  # Last 10 errors
                },
                'system': {
                    'cpu_avg': sum(self.cpu_usage) / len(self.cpu_usage) if self.cpu_usage else 0,
                    'memory_avg': sum(self.memory_usage) / len(self.memory_usage) if self.memory_usage else 0,
                    'active_requests': self.active_requests
                }
            }

# Global metrics collector
metrics_collector = MetricsCollector()

class PerformanceMonitor:
    """Monitors API performance and generates alerts."""
    
    def __init__(self):
        self.thresholds = {
            'response_time_ms': 2000,
            'error_rate_percent': 5.0,
            'cpu_percent': 80.0,
            'memory_percent': 85.0
        }
        self.alerts = deque(maxlen=100)
        
    def check_performance(self):
        """Check performance metrics against thresholds."""
        alerts = []
        summary = metrics_collector.get_metrics_summary()
        
        # Check response times
        for endpoint, stats in summary['response_times'].items():
            if stats['p95'] > self.thresholds['response_time_ms']:
                alerts.append({
                    'type': 'high_response_time',
                    'endpoint': endpoint,
                    'value': stats['p95'],
                    'threshold': self.thresholds['response_time_ms'],
                    'timestamp': datetime.utcnow().isoformat()
                })
        
        # Check error rates
        total_requests = sum(summary['requests'].values())
        total_errors = summary['errors']['total_count']
        if total_requests > 0:
            error_rate = (total_errors / total_requests) * 100
            if error_rate > self.thresholds['error_rate_percent']:
                alerts.append({
                    'type': 'high_error_rate',
                    'value': error_rate,
                    'threshold': self.thresholds['error_rate_percent'],
                    'timestamp': datetime.utcnow().isoformat()
                })
        
        # Check system resources
        if summary['system']['cpu_avg'] > self.thresholds['cpu_percent']:
            alerts.append({
                'type': 'high_cpu_usage',
                'value': summary['system']['cpu_avg'],
                'threshold': self.thresholds['cpu_percent'],
                'timestamp': datetime.utcnow().isoformat()
            })
            
        if summary['system']['memory_avg'] > self.thresholds['memory_percent']:
            alerts.append({
                'type': 'high_memory_usage',
                'value': summary['system']['memory_avg'],
                'threshold': self.thresholds['memory_percent'],
                'timestamp': datetime.utcnow().isoformat()
            })
        
        # Store alerts
        for alert in alerts:
            self.alerts.append(alert)
            logger.warning(f"Performance alert: {alert}")
            
        return alerts

# Global performance monitor
performance_monitor = PerformanceMonitor()

def monitor_request(f):
    """Decorator to monitor API requests."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        g.start_time = start_time
        
        # Increment active requests
        metrics_collector.active_requests += 1
        
        try:
            response = f(*args, **kwargs)
            status_code = getattr(response, 'status_code', 200)
        except Exception as e:
            # Record error
            metrics_collector.record_error(
                e, 
                endpoint=request.endpoint,
                user_id=getattr(g, 'current_user_id', None)
            )
            raise
        finally:
            # Calculate response time
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            # Record metrics
            metrics_collector.record_request(
                endpoint=request.endpoint or 'unknown',
                method=request.method,
                status_code=getattr(response, 'status_code', 500),
                response_time=response_time
            )
            
            # Decrement active requests
            metrics_collector.active_requests -= 1
            
        return response
    
    return decorated_function

class DatabaseMonitor:
    """Monitors database performance and health."""
    
    def __init__(self):
        self.query_times = deque(maxlen=1000)
        self.slow_queries = deque(maxlen=50)
        self.connection_errors = 0
        
    def record_query(self, query, execution_time):
        """Record database query performance."""
        self.query_times.append(execution_time)
        
        # Flag slow queries (>1 second)
        if execution_time > 1000:
            self.slow_queries.append({
                'query': query,
                'execution_time': execution_time,
                'timestamp': datetime.utcnow().isoformat()
            })
            
    def get_database_stats(self):
        """Get database performance statistics."""
        if not self.query_times:
            return {}
            
        sorted_times = sorted(self.query_times)
        return {
            'query_count': len(self.query_times),
            'avg_query_time': sum(self.query_times) / len(self.query_times),
            'p50_query_time': sorted_times[len(sorted_times) // 2],
            'p95_query_time': sorted_times[int(len(sorted_times) * 0.95)],
            'slow_query_count': len(self.slow_queries),
            'connection_errors': self.connection_errors,
            'recent_slow_queries': list(self.slow_queries)[-5:]
        }

# Global database monitor
db_monitor = DatabaseMonitor()

class ModelPerformanceMonitor:
    """Monitors AI model performance and usage."""
    
    def __init__(self):
        self.inference_times = defaultdict(deque)
        self.model_usage = defaultdict(int)
        self.model_errors = defaultdict(int)
        
    def record_inference(self, model_id, tokens_generated, inference_time):
        """Record model inference performance."""
        self.model_usage[model_id] += 1
        
        # Keep last 100 inference times per model
        if len(self.inference_times[model_id]) >= 100:
            self.inference_times[model_id].popleft()
        self.inference_times[model_id].append({
            'tokens': tokens_generated,
            'time_ms': inference_time,
            'tokens_per_second': tokens_generated / (inference_time / 1000) if inference_time > 0 else 0,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    def record_model_error(self, model_id, error):
        """Record model error."""
        self.model_errors[model_id] += 1
        logger.error(f"Model {model_id} error: {error}")
        
    def get_model_stats(self):
        """Get model performance statistics."""
        stats = {}
        for model_id in self.model_usage.keys():
            inferences = list(self.inference_times[model_id])
            if inferences:
                tokens_per_sec = [inf['tokens_per_second'] for inf in inferences]
                stats[model_id] = {
                    'total_requests': self.model_usage[model_id],
                    'error_count': self.model_errors[model_id],
                    'avg_tokens_per_second': sum(tokens_per_sec) / len(tokens_per_sec),
                    'recent_inferences': inferences[-10:]
                }
        return stats

# Global model monitor
model_monitor = ModelPerformanceMonitor()

def setup_monitoring_middleware(app):
    """Setup monitoring middleware for Flask app."""
    
    @app.before_request
    def before_request():
        g.start_time = time.time()
        
    @app.after_request
    def after_request(response):
        # Record system metrics periodically
        if hasattr(g, 'start_time'):
            metrics_collector.record_system_metrics()
            
        return response
        
    @app.teardown_request
    def teardown_request(error):
        if error:
            metrics_collector.record_error(
                error,
                endpoint=request.endpoint,
                user_id=getattr(g, 'current_user_id', None)
            )

def get_comprehensive_metrics():
    """Get all monitoring metrics."""
    return {
        'api_metrics': metrics_collector.get_metrics_summary(),
        'database_metrics': db_monitor.get_database_stats(),
        'model_metrics': model_monitor.get_model_stats(),
        'performance_alerts': list(performance_monitor.alerts)[-20:]  # Last 20 alerts
    }
