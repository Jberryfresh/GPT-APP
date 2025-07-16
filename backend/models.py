"""
Models Management Routes
=======================

API endpoints for managing AI models.
"""

from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db, Model, User
import logging
import uuid

logger = logging.getLogger(__name__)

models_bp = Blueprint('models', __name__)

@models_bp.route('/models', methods=['GET'])
@jwt_required(optional=True)
def list_models():
    """List available models."""
    try:
        user_id = get_jwt_identity()

        # Query models based on user
        if user_id:
            # Show user's models plus public models
            models = Model.query.filter(
                (Model.user_id == user_id) | (Model.is_public == True)
            ).all()
        else:
            # Show only public models
            models = Model.query.filter_by(is_public=True).all()

        return jsonify({
            'success': True,
            'models': [model.to_dict() for model in models],
            'count': len(models)
        })

    except Exception as e:
        logger.error(f"Error listing models: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@models_bp.route('/models', methods=['POST'])
@jwt_required()
def create_model():
    """Create a new model."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400

        # Validate required fields
        required_fields = ['name', 'base_model']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'{field} is required'
                }), 400

        # Create model
        model = Model(
            user_id=user_id,
            name=data['name'],
            model_id=data.get('model_id', str(uuid.uuid4())),
            base_model=data['base_model'],
            description=data.get('description', ''),
            model_type=data.get('model_type', 'fine_tuned'),
            is_public=data.get('is_public', False)
        )

        db.session.add(model)
        db.session.commit()

        return jsonify({
            'success': True,
            'model': model.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating model: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@models_bp.route('/models/<model_id>', methods=['GET'])
@jwt_required(optional=True)
def get_model(model_id):
    """Get a specific model."""
    try:
        user_id = get_jwt_identity()

        # Find model
        model = Model.query.filter_by(model_id=model_id).first()
        if not model:
            return jsonify({
                'success': False,
                'error': 'Model not found'
            }), 404

        # Check permissions
        if not model.is_public and (not user_id or model.user_id != user_id):
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403

        return jsonify({
            'success': True,
            'model': model.to_dict()
        })

    except Exception as e:
        logger.error(f"Error getting model: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@models_bp.route('/models/<model_id>', methods=['DELETE'])
@jwt_required()
def delete_model(model_id):
    """Delete a model."""
    try:
        user_id = get_jwt_identity()

        # Find model
        model = Model.query.filter_by(model_id=model_id, user_id=user_id).first()
        if not model:
            return jsonify({
                'success': False,
                'error': 'Model not found or access denied'
            }), 404

        db.session.delete(model)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Model deleted successfully'
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting model: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500