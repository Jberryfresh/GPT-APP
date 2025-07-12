"""
Billing and Subscription Routes
==============================

API endpoints for managing subscriptions, billing, and payments.
"""

from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import json
import logging
from datetime import datetime, timedelta
from decimal import Decimal

logger = logging.getLogger(__name__)

billing_bp = Blueprint('billing', __name__)

# Mock subscription plans
SUBSCRIPTION_PLANS = {
    'free': {
        'name': 'Free',
        'price': 0,
        'monthly_tokens': 1000,
        'features': ['Basic models', 'Community support'],
        'max_models': 1,
        'max_training_jobs': 1
    },
    'individual': {
        'name': 'Individual',
        'price': 999,  # $9.99 in cents
        'monthly_tokens': 50000,
        'features': ['All models', 'Email support', 'API access'],
        'max_models': 5,
        'max_training_jobs': 10
    },
    'professional': {
        'name': 'Professional',
        'price': 4999,  # $49.99 in cents
        'monthly_tokens': 500000,
        'features': ['Custom model training', 'Priority support', 'Advanced analytics'],
        'max_models': 20,
        'max_training_jobs': 50
    },
    'enterprise': {
        'name': 'Enterprise',
        'price': 19999,  # $199.99 in cents
        'monthly_tokens': -1,  # Unlimited
        'features': ['Unlimited tokens', 'Dedicated infrastructure', 'Phone support', 'Custom SLA'],
        'max_models': -1,  # Unlimited
        'max_training_jobs': -1  # Unlimited
    }
}

# Mock user subscriptions (in production, this would be in a database)
user_subscriptions = {
    'demo_user': {
        'plan': 'professional',
        'status': 'active',
        'current_period_start': datetime.now().isoformat(),
        'current_period_end': (datetime.now() + timedelta(days=30)).isoformat(),
        'tokens_used': 45000,
        'auto_renew': True,
        'payment_method': {
            'type': 'card',
            'last4': '4242',
            'brand': 'visa'
        }
    }
}

@billing_bp.route('/billing/plans', methods=['GET'])
def get_subscription_plans():
    """Get all available subscription plans."""
    try:
        return jsonify({
            'success': True,
            'plans': SUBSCRIPTION_PLANS
        })
    except Exception as e:
        logger.error(f"Error getting subscription plans: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@billing_bp.route('/billing/subscription', methods=['GET'])
@jwt_required()
def get_user_subscription():
    """Get current user's subscription details."""
    try:
        user_id = get_jwt_identity()
        subscription = user_subscriptions.get(user_id)
        
        if not subscription:
            # Return default free plan
            subscription = {
                'plan': 'free',
                'status': 'active',
                'current_period_start': datetime.now().isoformat(),
                'current_period_end': (datetime.now() + timedelta(days=30)).isoformat(),
                'tokens_used': 0,
                'auto_renew': False,
                'payment_method': None
            }
        
        # Add plan details
        plan_details = SUBSCRIPTION_PLANS.get(subscription['plan'], SUBSCRIPTION_PLANS['free'])
        subscription['plan_details'] = plan_details
        
        return jsonify({
            'success': True,
            'subscription': subscription
        })
    
    except Exception as e:
        logger.error(f"Error getting user subscription: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@billing_bp.route('/billing/subscription/upgrade', methods=['POST'])
@jwt_required()
def upgrade_subscription():
    """Upgrade user's subscription plan."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        new_plan = data.get('plan')
        if new_plan not in SUBSCRIPTION_PLANS:
            return jsonify({
                'success': False,
                'error': 'Invalid subscription plan'
            }), 400
        
        # In a real implementation, this would:
        # 1. Create a Stripe subscription
        # 2. Process payment
        # 3. Update database
        
        # Mock upgrade
        user_subscriptions[user_id] = {
            'plan': new_plan,
            'status': 'active',
            'current_period_start': datetime.now().isoformat(),
            'current_period_end': (datetime.now() + timedelta(days=30)).isoformat(),
            'tokens_used': user_subscriptions.get(user_id, {}).get('tokens_used', 0),
            'auto_renew': True,
            'payment_method': {
                'type': 'card',
                'last4': '4242',
                'brand': 'visa'
            }
        }
        
        return jsonify({
            'success': True,
            'message': f'Successfully upgraded to {SUBSCRIPTION_PLANS[new_plan]["name"]} plan',
            'subscription': user_subscriptions[user_id]
        })
    
    except Exception as e:
        logger.error(f"Error upgrading subscription: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@billing_bp.route('/billing/subscription/cancel', methods=['POST'])
@jwt_required()
def cancel_subscription():
    """Cancel user's subscription."""
    try:
        user_id = get_jwt_identity()
        
        if user_id not in user_subscriptions:
            return jsonify({
                'success': False,
                'error': 'No active subscription found'
            }), 404
        
        # In a real implementation, this would cancel the Stripe subscription
        user_subscriptions[user_id]['status'] = 'cancelled'
        user_subscriptions[user_id]['auto_renew'] = False
        
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

@billing_bp.route('/billing/usage', methods=['GET'])
@jwt_required()
def get_usage_stats():
    """Get user's usage statistics."""
    try:
        user_id = get_jwt_identity()
        subscription = user_subscriptions.get(user_id, {})
        plan = subscription.get('plan', 'free')
        plan_details = SUBSCRIPTION_PLANS.get(plan, SUBSCRIPTION_PLANS['free'])
        
        # Mock usage data
        usage_data = {
            'current_period': {
                'tokens_used': subscription.get('tokens_used', 0),
                'tokens_limit': plan_details['monthly_tokens'],
                'api_calls': 1547,
                'models_created': 3,
                'training_jobs': 12
            },
            'daily_usage': [
                {'date': '2024-06-10', 'tokens': 1200, 'api_calls': 45},
                {'date': '2024-06-11', 'tokens': 1800, 'api_calls': 67},
                {'date': '2024-06-12', 'tokens': 2100, 'api_calls': 78},
                {'date': '2024-06-13', 'tokens': 1900, 'api_calls': 56},
                {'date': '2024-06-14', 'tokens': 2300, 'api_calls': 89},
                {'date': '2024-06-15', 'tokens': 2800, 'api_calls': 102},
                {'date': '2024-06-16', 'tokens': 1500, 'api_calls': 67}
            ],
            'top_models': [
                {'name': 'Legal Expert', 'tokens': 15000, 'percentage': 33.3},
                {'name': 'Medical Assistant', 'tokens': 12000, 'percentage': 26.7},
                {'name': 'Default Model', 'tokens': 18000, 'percentage': 40.0}
            ]
        }
        
        return jsonify({
            'success': True,
            'usage': usage_data
        })
    
    except Exception as e:
        logger.error(f"Error getting usage stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@billing_bp.route('/billing/invoices', methods=['GET'])
@jwt_required()
def get_invoices():
    """Get user's billing invoices."""
    try:
        user_id = get_jwt_identity()
        
        # Mock invoice data
        invoices = [
            {
                'id': 'inv_001',
                'date': '2024-06-01',
                'amount': 4999,
                'status': 'paid',
                'plan': 'Professional',
                'period': 'June 2024',
                'download_url': '/api/v1/billing/invoices/inv_001/download'
            },
            {
                'id': 'inv_002',
                'date': '2024-05-01',
                'amount': 4999,
                'status': 'paid',
                'plan': 'Professional',
                'period': 'May 2024',
                'download_url': '/api/v1/billing/invoices/inv_002/download'
            },
            {
                'id': 'inv_003',
                'date': '2024-04-01',
                'amount': 999,
                'status': 'paid',
                'plan': 'Individual',
                'period': 'April 2024',
                'download_url': '/api/v1/billing/invoices/inv_003/download'
            }
        ]
        
        return jsonify({
            'success': True,
            'invoices': invoices
        })
    
    except Exception as e:
        logger.error(f"Error getting invoices: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@billing_bp.route('/billing/payment-methods', methods=['GET'])
@jwt_required()
def get_payment_methods():
    """Get user's payment methods."""
    try:
        user_id = get_jwt_identity()
        subscription = user_subscriptions.get(user_id, {})
        
        payment_methods = []
        if subscription.get('payment_method'):
            payment_methods.append({
                'id': 'pm_demo',
                'type': subscription['payment_method']['type'],
                'last4': subscription['payment_method']['last4'],
                'brand': subscription['payment_method']['brand'],
                'is_default': True
            })
        
        return jsonify({
            'success': True,
            'payment_methods': payment_methods
        })
    
    except Exception as e:
        logger.error(f"Error getting payment methods: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@billing_bp.route('/billing/payment-methods', methods=['POST'])
@jwt_required()
def add_payment_method():
    """Add a new payment method."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        # In a real implementation, this would:
        # 1. Create a Stripe payment method
        # 2. Attach it to the customer
        # 3. Store in database
        
        # Mock payment method creation
        payment_method = {
            'id': f"pm_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'type': 'card',
            'last4': data.get('last4', '4242'),
            'brand': data.get('brand', 'visa'),
            'is_default': True
        }
        
        # Update user subscription
        if user_id in user_subscriptions:
            user_subscriptions[user_id]['payment_method'] = {
                'type': payment_method['type'],
                'last4': payment_method['last4'],
                'brand': payment_method['brand']
            }
        
        return jsonify({
            'success': True,
            'payment_method': payment_method
        })
    
    except Exception as e:
        logger.error(f"Error adding payment method: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@billing_bp.route('/billing/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events."""
    try:
        # In a real implementation, this would:
        # 1. Verify the webhook signature
        # 2. Handle various Stripe events
        # 3. Update subscription status in database
        
        payload = request.get_data()
        event = json.loads(payload)
        
        logger.info(f"Received Stripe webhook: {event.get('type')}")
        
        # Handle different event types
        if event['type'] == 'invoice.payment_succeeded':
            # Update subscription status
            pass
        elif event['type'] == 'invoice.payment_failed':
            # Handle failed payment
            pass
        elif event['type'] == 'customer.subscription.deleted':
            # Handle subscription cancellation
            pass
        
        return jsonify({'success': True})
    
    except Exception as e:
        logger.error(f"Error handling webhook: {e}")
        return jsonify({'error': str(e)}), 400

