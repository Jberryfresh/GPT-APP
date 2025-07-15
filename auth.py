
"""
Authentication Routes
====================

API endpoints for user authentication and management.
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from database import db, User, Subscription
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/auth/login', methods=['POST'])
def login():
    """User login endpoint."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({
                'success': False,
                'error': 'Email and password are required'
            }), 400
        
        # Find user
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            return jsonify({
                'success': False,
                'error': 'Invalid email or password'
            }), 401
        
        # Check if account is locked
        if user.is_locked():
            return jsonify({
                'success': False,
                'error': 'Account is temporarily locked'
            }), 423
        
        # Update login info
        user.last_login_at = datetime.utcnow()
        user.failed_login_attempts = 0
        db.session.commit()
        
        # Create access token
        access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            'success': True,
            'access_token': access_token,
            'user': user.to_dict()
        })
    
    except Exception as e:
        logger.error(f"Error during login: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_bp.route('/auth/register', methods=['POST'])
def register():
    """User registration endpoint."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')
        
        if not all([email, username, password]):
            return jsonify({
                'success': False,
                'error': 'Email, username, and password are required'
            }), 400
        
        # Check if user exists
        existing_user = User.query.filter(
            (User.email == email) | (User.username == username)
        ).first()
        
        if existing_user:
            return jsonify({
                'success': False,
                'error': 'Email or username already exists'
            }), 409
        
        # Create user
        user = User(
            email=email,
            username=username,
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            is_active=True
        )
        user.set_password(password)
        user.generate_api_key()
        
        db.session.add(user)
        db.session.flush()  # Get user ID
        
        # Create default subscription
        subscription = Subscription(
            user_id=user.id,
            tier='free',
            status='active',
            monthly_token_limit=10000,
            monthly_tokens_used=0,
            monthly_training_hours_limit=1.0,
            monthly_training_hours_used=0.0,
            can_train_models=True,
            can_use_api=True,
            max_models=3,
            current_period_start=datetime.utcnow(),
            current_period_end=datetime.utcnow() + timedelta(days=30)
        )
        
        db.session.add(subscription)
        db.session.commit()
        
        # Create access token
        access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            'success': True,
            'access_token': access_token,
            'user': user.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error during registration: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_bp.route('/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user information."""
    try:
        user_id = get_jwt_identity()
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        # Get user's subscription
        subscription = Subscription.query.filter_by(user_id=user_id).first()
        
        return jsonify({
            'success': True,
            'user': user.to_dict(),
            'subscription': subscription.to_dict() if subscription else None
        })
    
    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
