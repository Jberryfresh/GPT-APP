"""
Model Management Routes
======================

API endpoints for managing AI models and their configurations.
"""

from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

models_bp = Blueprint('models', __name__)

@models_bp.route('/models', methods=['GET'])
def list_models():
    """List all available models."""
    try:
        model_manager = current_app.model_manager
        models = model_manager.list_models()

        return jsonify({
            'success': True,
            'models': models,
            'count': len(models)
        })

    except Exception as e:
        logger.error(f"Error listing models: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@models_bp.route('/models/<model_id>', methods=['GET'])
def get_model_info(model_id):
    """Get detailed information about a specific model."""
    try:
        model_manager = current_app.model_manager
        models = model_manager.list_models()

        model = next((m for m in models if m['model_id'] == model_id), None)
        if not model:
            return jsonify({
                'success': False,
                'error': f'Model {model_id} not found'
            }), 404

        return jsonify({
            'success': True,
            'model': model
        })

    except Exception as e:
        logger.error(f"Error getting model info: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@models_bp.route('/models/load', methods=['POST'])
@jwt_required()
def load_model():
    """Load a model from a file path."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400

        model_path = data.get('model_path')
        model_id = data.get('model_id')

        if not model_path:
            return jsonify({
                'success': False,
                'error': 'model_path is required'
            }), 400

        if not os.path.exists(model_path):
            return jsonify({
                'success': False,
                'error': f'Model path does not exist: {model_path}'
            }), 400

        model_manager = current_app.model_manager
        loaded_model_id = model_manager.load_model(model_path, model_id)

        return jsonify({
            'success': True,
            'model_id': loaded_model_id,
            'message': f'Model {loaded_model_id} loaded successfully'
        })

    except Exception as e:
        logger.error(f"Error loading model: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@models_bp.route('/models/<model_id>/unload', methods=['POST'])
@jwt_required()
def unload_model(model_id):
    """Unload a model to free memory."""
    try:
        model_manager = current_app.model_manager
        model_manager.unload_model(model_id)

        return jsonify({
            'success': True,
            'message': f'Model {model_id} unloaded successfully'
        })

    except Exception as e:
        logger.error(f"Error unloading model: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@models_bp.route('/models/<model_id>/default', methods=['POST'])
@jwt_required()
def set_default_model(model_id):
    """Set a model as the default for inference."""
    try:
        model_manager = current_app.model_manager
        model_manager.set_default_model(model_id)

        return jsonify({
            'success': True,
            'message': f'Model {model_id} set as default'
        })

    except Exception as e:
        logger.error(f"Error setting default model: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@models_bp.route('/models/discover', methods=['GET'])
def discover_models():
    """Discover available models in the models directory."""
    try:
        models_dir = Path('./models')
        discovered_models = []

        if models_dir.exists():
            for model_path in models_dir.iterdir():
                if model_path.is_dir():
                    # Check if it's a valid model directory
                    if (model_path / 'config.json').exists() or (model_path / 'adapter_config.json').exists():
                        discovered_models.append({
                            'model_id': model_path.name,
                            'model_path': str(model_path),
                            'type': 'fine_tuned' if (model_path / 'adapter_config.json').exists() else 'base'
                        })

        return jsonify({
            'success': True,
            'discovered_models': discovered_models,
            'count': len(discovered_models)
        })

    except Exception as e:
        logger.error(f"Error discovering models: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500