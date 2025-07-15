
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
