"""
Billing and Subscription Routes
==============================

API endpoints for managing user subscriptions and billing.
"""

from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

billing_bp = Blueprint('billing', __name__)

# Mock subscription data (in production, use a database)
user_subscriptions = {}

@billing_bp.route('/billing/subscription', methods=['GET'])
@jwt_required()
def get_subscription():
    """Get user's current subscription details."""
    try:
        user_id = get_jwt_identity()

        # Mock subscription data
        subscription = user_subscriptions.get(user_id, {
            'tier': 'free',
            'status': 'active',
            'usage': {
                'tokens_used': 0,
                'tokens_limit': 1000,
                'api_calls': 0
            },
            'billing_cycle': 'monthly',
            'next_billing_date': None,
            'features': ['basic_chat', 'limited_tokens']
        })

        return jsonify({
            'success': True,
            'subscription': subscription
        })

    except Exception as e:
        logger.error(f"Error getting subscription: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@billing_bp.route('/billing/plans', methods=['GET'])
def get_billing_plans():
    """Get available billing plans."""
    try:
        plans = [
            {
                'id': 'free',
                'name': 'Free Tier',
                'price': 0,
                'currency': 'USD',
                'interval': 'monthly',
                'features': [
                    '1,000 tokens per month',
                    'Basic chat interface',
                    'Community support'
                ],
                'limits': {
                    'tokens_per_month': 1000,
                    'models': 1,
                    'api_calls_per_minute': 10
                }
            },
            {
                'id': 'individual',
                'name': 'Individual',
                'price': 9.99,
                'currency': 'USD',
                'interval': 'monthly',
                'features': [
                    '50,000 tokens per month',
                    'Advanced chat features',
                    'Model customization',
                    'Email support'
                ],
                'limits': {
                    'tokens_per_month': 50000,
                    'models': 5,
                    'api_calls_per_minute': 60
                }
            },
            {
                'id': 'professional',
                'name': 'Professional',
                'price': 49.99,
                'currency': 'USD',
                'interval': 'monthly',
                'features': [
                    '500,000 tokens per month',
                    'Advanced model training',
                    'API access',
                    'Priority support',
                    'Analytics dashboard'
                ],
                'limits': {
                    'tokens_per_month': 500000,
                    'models': 25,
                    'api_calls_per_minute': 300
                }
            },
            {
                'id': 'enterprise',
                'name': 'Enterprise',
                'price': 199.99,
                'currency': 'USD',
                'interval': 'monthly',
                'features': [
                    'Unlimited tokens',
                    'Custom model training',
                    'Dedicated support',
                    'SLA guarantees',
                    'On-premise deployment'
                ],
                'limits': {
                    'tokens_per_month': -1,  # Unlimited
                    'models': -1,  # Unlimited
                    'api_calls_per_minute': 1000
                }
            }
        ]

        return jsonify({
            'success': True,
            'plans': plans
        })

    except Exception as e:
        logger.error(f"Error getting billing plans: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@billing_bp.route('/billing/usage', methods=['GET'])
@jwt_required()
def get_usage():
    """Get user's current usage statistics."""
    try:
        user_id = get_jwt_identity()

        # Mock usage data
        usage = {
            'current_period': {
                'start_date': (datetime.now() - timedelta(days=15)).isoformat(),
                'end_date': (datetime.now() + timedelta(days=15)).isoformat(),
                'tokens_used': 2450,
                'api_calls': 123,
                'training_jobs': 2
            },
            'historical': [
                {
                    'period': '2024-05',
                    'tokens_used': 8500,
                    'api_calls': 420,
                    'training_jobs': 5
                },
                {
                    'period': '2024-04',
                    'tokens_used': 6200,
                    'api_calls': 310,
                    'training_jobs': 3
                }
            ]
        }

        return jsonify({
            'success': True,
            'usage': usage
        })

    except Exception as e:
        logger.error(f"Error getting usage: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@billing_bp.route('/billing/upgrade', methods=['POST'])
@jwt_required()
def upgrade_subscription():
    """Upgrade user subscription."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400

        plan_id = data.get('plan_id')
        if not plan_id:
            return jsonify({
                'success': False,
                'error': 'plan_id is required'
            }), 400

        # Mock subscription upgrade
        user_subscriptions[user_id] = {
            'tier': plan_id,
            'status': 'active',
            'upgraded_at': datetime.now().isoformat(),
            'next_billing_date': (datetime.now() + timedelta(days=30)).isoformat()
        }

        return jsonify({
            'success': True,
            'message': f'Successfully upgraded to {plan_id} plan',
            'subscription': user_subscriptions[user_id]
        })

    except Exception as e:
        logger.error(f"Error upgrading subscription: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@billing_bp.route('/billing/cancel', methods=['POST'])
@jwt_required()
def cancel_subscription():
    """Cancel user subscription."""
    try:
        user_id = get_jwt_identity()

        # Mock subscription cancellation
        if user_id in user_subscriptions:
            user_subscriptions[user_id]['status'] = 'cancelled'
            user_subscriptions[user_id]['cancelled_at'] = datetime.now().isoformat()

        return jsonify({
            'success': True,
            'message': 'Subscription cancelled successfully'
        })

    except Exception as e:
        logger.error(f"Error cancelling subscription: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500