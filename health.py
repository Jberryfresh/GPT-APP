"""
Health Check Routes
==================

API endpoints for system health monitoring and status checks.
"""

from flask import Blueprint, jsonify, current_app
import psutil
import time
from datetime import datetime

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """Basic health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Custom GPT API',
        'version': '1.0.0'
    })

@health_bp.route('/health/detailed', methods=['GET'])
def detailed_health():
    """Detailed health check with system metrics."""
    try:
        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        # Get model manager status
        model_manager = current_app.model_manager
        loaded_models = model_manager.list_models()

        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'service': 'Custom GPT API',
            'version': '1.0.0',
            'system': {
                'cpu_percent': cpu_percent,
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent
                },
                'disk': {
                    'total': disk.total,
                    'free': disk.free,
                    'percent': (disk.used / disk.total) * 100
                }
            },
            'models': {
                'loaded_count': len(loaded_models),
                'models': [model['model_id'] for model in loaded_models]
            }
        })

    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }), 500

@health_bp.route('/health/ready', methods=['GET'])
def readiness_check():
    """Readiness check for deployment health checks."""
    try:
        # Check if essential services are ready
        model_manager = current_app.model_manager

        return jsonify({
            'status': 'ready',
            'timestamp': datetime.now().isoformat(),
            'checks': {
                'model_manager': True,
                'api_routes': True
            }
        })

    except Exception as e:
        return jsonify({
            'status': 'not_ready',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }), 503

@health_bp.route('/health/live', methods=['GET'])
def liveness_check():
    """Liveness check for Kubernetes deployments."""
    return jsonify({
        'status': 'alive',
        'timestamp': datetime.now().isoformat()
    })