"""
Monitoring API Routes
====================

API endpoints for accessing monitoring data and metrics.
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from monitoring import get_comprehensive_metrics, performance_monitor, metrics_collector
from auth import require_admin
import json

monitoring_bp = Blueprint('monitoring', __name__)

@monitoring_bp.route('/metrics', methods=['GET'])
@jwt_required()
@require_admin
def get_metrics():
    """Get comprehensive system metrics."""
    try:
        metrics = get_comprehensive_metrics()
        return jsonify({
            'success': True,
            'data': metrics
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@monitoring_bp.route('/metrics/api', methods=['GET'])
@jwt_required()
@require_admin
def get_api_metrics():
    """Get API-specific metrics."""
    try:
        metrics = metrics_collector.get_metrics_summary()
        return jsonify({
            'success': True,
            'data': metrics
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@monitoring_bp.route('/alerts', methods=['GET'])
@jwt_required()
@require_admin
def get_alerts():
    """Get performance alerts."""
    try:
        alerts = list(performance_monitor.alerts)
        return jsonify({
            'success': True,
            'data': alerts
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@monitoring_bp.route('/alerts/check', methods=['POST'])
@jwt_required()
@require_admin
def check_performance():
    """Manually trigger performance check."""
    try:
        new_alerts = performance_monitor.check_performance()
        return jsonify({
            'success': True,
            'data': {
                'new_alerts': new_alerts,
                'total_alerts': len(performance_monitor.alerts)
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@monitoring_bp.route('/thresholds', methods=['GET', 'PUT'])
@jwt_required()
@require_admin
def manage_thresholds():
    """Get or update performance thresholds."""
    try:
        if request.method == 'GET':
            return jsonify({
                'success': True,
                'data': performance_monitor.thresholds
            })
        else:
            # Update thresholds
            new_thresholds = request.get_json()
            if not new_thresholds:
                return jsonify({
                    'success': False,
                    'error': 'No threshold data provided'
                }), 400

            performance_monitor.thresholds.update(new_thresholds)
            return jsonify({
                'success': True,
                'data': performance_monitor.thresholds
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@monitoring_bp.route('/export', methods=['GET'])
@jwt_required()
@require_admin
def export_metrics():
    """Export metrics data for analysis."""
    try:
        metrics = get_comprehensive_metrics()

        # Add metadata
        export_data = {
            'export_timestamp': metrics_collector.get_metrics_summary()['timestamp'],
            'export_type': 'full_metrics',
            'version': '1.0',
            'data': metrics
        }

        response = jsonify(export_data)
        response.headers['Content-Disposition'] = 'attachment; filename=metrics_export.json'
        return response

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@monitoring_bp.route('/health/detailed', methods=['GET'])
def detailed_health():
    """Get detailed health information."""
    try:
        health_data = monitor.get_health_summary()

        # Add model manager health if available
        from flask import current_app
        model_manager = getattr(current_app, 'model_manager', None)
        if model_manager and hasattr(model_manager, 'get_system_health'):
            health_data['model_manager'] = model_manager.get_system_health()

        return jsonify({
            'success': True,
            'health': health_data
        })

    except Exception as e:
        logger.error(f"Error getting detailed health: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@monitoring_bp.route('/models/stats', methods=['GET'])
def model_stats():
    """Get model performance statistics."""
    try:
        from flask import current_app
        model_manager = getattr(current_app, 'model_manager', None)

        if not model_manager:
            return jsonify({
                'success': False,
                'error': 'Model manager not available'
            }), 503

        if hasattr(model_manager, 'get_performance_stats'):
            stats = model_manager.get_performance_stats()
            return jsonify({
                'success': True,
                'stats': stats
            })
        else:
            return jsonify({
                'success': True,
                'stats': {
                    'loaded_models': len(getattr(model_manager, 'models', {})),
                    'message': 'Limited stats available'
                }
            })

    except Exception as e:
        logger.error(f"Error getting model stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@monitoring_bp.route('/models/memory', methods=['GET'])
def model_memory():
    """Get model memory usage."""
    try:
        from flask import current_app
        model_manager = getattr(current_app, 'model_manager', None)

        if not model_manager:
            return jsonify({
                'success': False,
                'error': 'Model manager not available'
            }), 503

        if hasattr(model_manager, 'get_memory_usage'):
            memory_usage = model_manager.get_memory_usage()
            return jsonify({
                'success': True,
                'memory': memory_usage
            })
        else:
            return jsonify({
                'success': True,
                'memory': {'message': 'Memory monitoring not available'}
            })

    except Exception as e:
        logger.error(f"Error getting model memory: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@monitoring_bp.route('/models/cleanup', methods=['POST'])
def cleanup_memory():
    """Trigger memory cleanup."""
    try:
        from flask import current_app
        model_manager = getattr(current_app, 'model_manager', None)

        if not model_manager:
            return jsonify({
                'success': False,
                'error': 'Model manager not available'
            }), 503

        if hasattr(model_manager, 'cleanup_memory'):
            model_manager.cleanup_memory()
            return jsonify({
                'success': True,
                'message': 'Memory cleanup completed'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Memory cleanup not available'
            }), 501

    except Exception as e:
        logger.error(f"Error during memory cleanup: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Export blueprint
monitoring_bp = Blueprint('monitoring', __name__)
__all__ = ['monitoring_bp']