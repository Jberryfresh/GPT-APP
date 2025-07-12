"""
Health Check Routes
==================

Health check and system status endpoints.
"""

from flask import Blueprint, jsonify, current_app
from datetime import datetime
import psutil
import torch

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """Basic health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@health_bp.route('/health/detailed', methods=['GET'])
def detailed_health_check():
    """Detailed health check with system information."""
    try:
        # System information
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # GPU information
        gpu_info = {}
        if torch.cuda.is_available():
            gpu_info = {
                'available': True,
                'device_count': torch.cuda.device_count(),
                'current_device': torch.cuda.current_device(),
                'device_name': torch.cuda.get_device_name(0) if torch.cuda.device_count() > 0 else None,
                'memory_allocated': torch.cuda.memory_allocated(0) if torch.cuda.device_count() > 0 else 0,
                'memory_reserved': torch.cuda.memory_reserved(0) if torch.cuda.device_count() > 0 else 0
            }
        else:
            gpu_info = {'available': False}
        
        # Model manager status
        model_manager = getattr(current_app, 'model_manager', None)
        models_info = []
        if model_manager:
            models_info = model_manager.list_models()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'system': {
                'cpu_percent': cpu_percent,
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'used': memory.used
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': (disk.used / disk.total) * 100
                },
                'gpu': gpu_info
            },
            'models': {
                'loaded_count': len(models_info),
                'models': models_info
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
    """Readiness check for Kubernetes deployments."""
    try:
        # Check if model manager is available
        model_manager = getattr(current_app, 'model_manager', None)
        if model_manager is None:
            return jsonify({
                'status': 'not_ready',
                'reason': 'Model manager not initialized'
            }), 503
        
        return jsonify({
            'status': 'ready',
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'status': 'not_ready',
            'reason': str(e)
        }), 503

@health_bp.route('/health/live', methods=['GET'])
def liveness_check():
    """Liveness check for Kubernetes deployments."""
    return jsonify({
        'status': 'alive',
        'timestamp': datetime.now().isoformat()
    })

