from flask import Flask, jsonify, request, send_from_directory, make_response
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
import logging
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor
import urllib.parse
import random
import time
import csv
from io import StringIO
from io import BytesIO
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Security configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Initialize JWT manager
jwt = JWTManager(app)

# Simple CORS setup for development
CORS(app, origins=['*'], supports_credentials=True)

# PostgreSQL database connection
def get_db_connection():
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        logger.error("DATABASE_URL environment variable not set")
        return None

    try:
        conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return None

# Initialize database tables
def init_database():
    conn = get_db_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()

        # Create users table with enhanced authentication fields
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                email VARCHAR(255) UNIQUE NOT NULL,
                username VARCHAR(80) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                first_name VARCHAR(100),
                last_name VARCHAR(100),
                is_active BOOLEAN DEFAULT TRUE,
                is_verified BOOLEAN DEFAULT FALSE,
                email_verified_at TIMESTAMP,
                last_login_at TIMESTAMP,
                failed_login_attempts INTEGER DEFAULT 0,
                locked_until TIMESTAMP,
                api_key VARCHAR(255) UNIQUE,
                api_key_created_at TIMESTAMP,
                subscription_tier VARCHAR(50) DEFAULT 'free',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create subscriptions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscriptions (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                tier VARCHAR(50) DEFAULT 'free',
                status VARCHAR(50) DEFAULT 'active',
                stripe_customer_id VARCHAR(255),
                stripe_subscription_id VARCHAR(255),
                monthly_token_limit BIGINT DEFAULT 10000,
                monthly_tokens_used BIGINT DEFAULT 0,
                monthly_training_hours_limit REAL DEFAULT 1.0,
                monthly_training_hours_used REAL DEFAULT 0.0,
                can_train_models BOOLEAN DEFAULT TRUE,
                can_use_api BOOLEAN DEFAULT TRUE,
                max_models INTEGER DEFAULT 3,
                priority_support BOOLEAN DEFAULT FALSE,
                current_period_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                current_period_end TIMESTAMP DEFAULT (CURRENT_TIMESTAMP + INTERVAL '30 days'),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create models table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS models (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name VARCHAR(255) NOT NULL,
                description TEXT,
                user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                status VARCHAR(50) DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create conversations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                model_id UUID REFERENCES models(id) ON DELETE CASCADE,
                messages JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create usage_records table for billing
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usage_records (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                model_id UUID REFERENCES models(id) ON DELETE SET NULL,
                operation_type VARCHAR(50) NOT NULL,
                tokens_used INTEGER DEFAULT 0,
                compute_time_seconds REAL DEFAULT 0.0,
                cost_cents INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create billing_invoices table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS billing_invoices (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                stripe_invoice_id VARCHAR(255),
                amount_cents INTEGER NOT NULL,
                currency VARCHAR(3) DEFAULT 'USD',
                status VARCHAR(50) DEFAULT 'pending',
                billing_period_start TIMESTAMP NOT NULL,
                billing_period_end TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                paid_at TIMESTAMP
            )
        ''')

        # Create payment_methods table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payment_methods (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                stripe_payment_method_id VARCHAR(255) UNIQUE NOT NULL,
                type VARCHAR(50) NOT NULL,
                last_four VARCHAR(4),
                brand VARCHAR(50),
                exp_month INTEGER,
                exp_year INTEGER,
                is_default BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        logger.info("Database tables initialized successfully")
        return True

    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

# Database helper functions
def get_users():
    conn = get_db_connection()
    if not conn:
        return {}

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        return {user['email']: dict(user) for user in users}
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        return {}
    finally:
        cursor.close()
        conn.close()

def create_user(email, username, password, first_name='', last_name=''):
    """Create a new user with proper security."""
    conn = get_db_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor()
        
        # Check if user already exists
        cursor.execute(
            "SELECT id FROM users WHERE email = %s OR username = %s",
            (email, username)
        )
        if cursor.fetchone():
            return None  # User already exists
        
        user_id = str(uuid.uuid4())
        password_hash = generate_password_hash(password)
        api_key = str(uuid.uuid4()).replace('-', '')
        
        # Create user
        cursor.execute('''
            INSERT INTO users (id, email, username, password_hash, first_name, last_name, 
                             api_key, api_key_created_at, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (user_id, email, username, password_hash, first_name, last_name, 
              api_key, datetime.utcnow(), True))
        
        # Create default subscription
        cursor.execute('''
            INSERT INTO subscriptions (user_id, tier, status, monthly_token_limit, 
                                     monthly_training_hours_limit, can_train_models, 
                                     can_use_api, max_models)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', (user_id, 'free', 'active', 10000, 1.0, True, True, 3))
        
        conn.commit()
        
        # Return user data
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        return dict(user) if user else None
        
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        conn.rollback()
        return None
    finally:
        cursor.close()
        conn.close()

def authenticate_user(email, password):
    """Authenticate user and return user data if valid."""
    conn = get_db_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if not user:
            return None
            
        user_dict = dict(user)
        
        # Check if account is locked
        if user_dict.get('locked_until') and user_dict['locked_until'] > datetime.utcnow():
            return None
        
        # Check password
        if not check_password_hash(user_dict['password_hash'], password):
            # Increment failed attempts
            cursor.execute(
                "UPDATE users SET failed_login_attempts = failed_login_attempts + 1 WHERE id = %s",
                (user_dict['id'],)
            )
            
            # Lock account after 5 failed attempts
            if user_dict.get('failed_login_attempts', 0) >= 4:
                lock_until = datetime.utcnow() + timedelta(minutes=15)
                cursor.execute(
                    "UPDATE users SET locked_until = %s WHERE id = %s",
                    (lock_until, user_dict['id'])
                )
            
            conn.commit()
            return None
        
        # Successful login - update login info
        cursor.execute('''
            UPDATE users 
            SET last_login_at = %s, failed_login_attempts = 0, locked_until = NULL 
            WHERE id = %s
        ''', (datetime.utcnow(), user_dict['id']))
        
        conn.commit()
        return user_dict
        
    except Exception as e:
        logger.error(f"Error authenticating user: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def get_user_by_id(user_id):
    """Get user by ID."""
    conn = get_db_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        return dict(user) if user else None
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def get_user_subscription(user_id):
    """Get user's subscription."""
    conn = get_db_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM subscriptions WHERE user_id = %s", (user_id,))
        subscription = cursor.fetchone()
        return dict(subscription) if subscription else None
    except Exception as e:
        logger.error(f"Error getting subscription: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def get_models():
    conn = get_db_connection()
    if not conn:
        return {}

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM models")
        models = cursor.fetchall()
        return {str(model['id']): dict(model) for model in models}
    except Exception as e:
        logger.error(f"Error fetching models: {e}")
        return {}
    finally:
        cursor.close()
        conn.close()

def get_conversations():
    conn = get_db_connection()
    if not conn:
        return {}

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM conversations")
        conversations = cursor.fetchall()
        return {str(conv['id']): dict(conv) for conv in conversations}
    except Exception as e:
        logger.error(f"Error fetching conversations: {e}")
        return {}
    finally:
        cursor.close()
        conn.close()

def save_to_fallback(entity_type, entity_id, data):
    """
    Saves data to a JSON file as a fallback mechanism.
    """
    filename = f"{entity_type}_fallback.json"
    try:
        # Read existing data
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                all_data = json.load(f)
        else:
            all_data = {}

        # Update with new data
        all_data[entity_id] = data

        # Write back to file
        with open(filename, 'w') as f:
            json.dump(all_data, f, indent=4)
        logger.info(f"Data saved to fallback file {filename} for {entity_type} id {entity_id}")
    except Exception as e:
        logger.error(f"Error saving to fallback file: {e}")

# Serve React frontend
@app.route('/')
def serve_frontend():
    return send_from_directory('.', 'simple_index.html')

@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(os.path.join('.', path)):
        return send_from_directory('.', path)
    if not path.startswith('api/'):
        return send_from_directory('.', 'simple_index.html')
    return jsonify({'error': 'Not found'}), 404

# Health check
@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

# Real Authentication endpoints
@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login with JWT token generation."""
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

        # Authenticate user
        user = authenticate_user(email, password)
        if not user:
            return jsonify({
                'success': False,
                'error': 'Invalid email or password'
            }), 401

        # Get user's subscription
        subscription = get_user_subscription(user['id'])

        # Create JWT access token
        access_token = create_access_token(identity=str(user['id']))

        # Remove sensitive data
        user_data = {
            'id': str(user['id']),
            'email': user['email'],
            'username': user['username'],
            'first_name': user.get('first_name', ''),
            'last_name': user.get('last_name', ''),
            'is_active': user['is_active'],
            'is_verified': user['is_verified'],
            'created_at': user['created_at'].isoformat() if user['created_at'] else None,
            'last_login_at': user['last_login_at'].isoformat() if user['last_login_at'] else None
        }

        return jsonify({
            'success': True,
            'access_token': access_token,
            'user': user_data,
            'subscription': subscription
        })

    except Exception as e:
        logger.error(f"Error during login: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/auth/register', methods=['POST'])
def register():
    """User registration with secure password hashing."""
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
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')

        if not all([email, username, password]):
            return jsonify({
                'success': False,
                'error': 'Email, username, and password are required'
            }), 400

        # Create user
        user = create_user(email, username, password, first_name, last_name)
        if not user:
            return jsonify({
                'success': False,
                'error': 'Email or username already exists'
            }), 409

        # Get user's subscription
        subscription = get_user_subscription(user['id'])

        # Create JWT access token
        access_token = create_access_token(identity=str(user['id']))

        # Remove sensitive data
        user_data = {
            'id': str(user['id']),
            'email': user['email'],
            'username': user['username'],
            'first_name': user.get('first_name', ''),
            'last_name': user.get('last_name', ''),
            'is_active': user['is_active'],
            'is_verified': user['is_verified'],
            'created_at': user['created_at'].isoformat() if user['created_at'] else None
        }

        return jsonify({
            'success': True,
            'access_token': access_token,
            'user': user_data,
            'subscription': subscription
        }), 201

    except Exception as e:
        logger.error(f"Error during registration: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current authenticated user information."""
    try:
        user_id = get_jwt_identity()
        
        user = get_user_by_id(user_id)
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404

        subscription = get_user_subscription(user_id)

        # Remove sensitive data
        user_data = {
            'id': str(user['id']),
            'email': user['email'],
            'username': user['username'],
            'first_name': user.get('first_name', ''),
            'last_name': user.get('last_name', ''),
            'is_active': user['is_active'],
            'is_verified': user['is_verified'],
            'api_key': user.get('api_key'),
            'created_at': user['created_at'].isoformat() if user['created_at'] else None,
            'last_login_at': user['last_login_at'].isoformat() if user['last_login_at'] else None
        }

        return jsonify({
            'success': True,
            'user': user_data,
            'subscription': subscription
        })

    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Model management
@app.route('/api/models', methods=['GET'])
@jwt_required()
def get_models_list():
    models_data = get_models()
    models_list = list(models_data.values())
    return jsonify({
        'success': True,
        'models': models_list
    })

@app.route('/api/models', methods=['POST'])
@jwt_required()
def create_model():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Check user's subscription limits
        subscription = get_user_subscription(user_id)
        if not subscription or not subscription.get('can_train_models', False):
            return jsonify({
                'success': False,
                'error': 'Model training not available in your subscription'
            }), 403
        
        # Check model count limit
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM models WHERE user_id = %s", (user_id,))
                model_count = cursor.fetchone()[0]
                
                max_models = subscription.get('max_models', 3)
                if model_count >= max_models:
                    return jsonify({
                        'success': False,
                        'error': f'Model limit reached ({max_models} models maximum)'
                    }), 403
                    
                # Create model
                model_id = str(uuid.uuid4())
                cursor.execute('''
                    INSERT INTO models (id, name, description, user_id, status)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (
                    model_id,
                    data.get('name', f'Model {model_count + 1}'),
                    data.get('description', 'User created model'),
                    user_id,
                    'active'
                ))
                
                conn.commit()
                
                # Get created model
                cursor.execute("SELECT * FROM models WHERE id = %s", (model_id,))
                model = dict(cursor.fetchone())
                model['id'] = str(model['id'])
                model['user_id'] = str(model['user_id'])
                model['created_at'] = model['created_at'].isoformat()
                
                return jsonify({
                    'success': True,
                    'message': 'Model created successfully',
                    'model': model
                })
                
            finally:
                cursor.close()
                conn.close()
        
        return jsonify({
            'success': False,
            'error': 'Database connection failed'
        }), 500
        
    except Exception as e:
        logger.error(f"Error creating model: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Chat functionality
@app.route('/api/chat', methods=['POST'])
@jwt_required()
def chat():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        message = data.get('message', '')
        model_id = data.get('model_id', 'default')

        # Check user's subscription limits
        subscription = get_user_subscription(user_id)
        if not subscription:
            return jsonify({
                'success': False,
                'error': 'No active subscription found'
            }), 403

        # Estimate token usage (rough approximation)
        estimated_tokens = len(message.split()) * 2  # Approximate tokens for input + output
        
        # Check token quota
        if subscription['monthly_token_limit'] != -1:  # Not unlimited
            if subscription['monthly_tokens_used'] + estimated_tokens > subscription['monthly_token_limit']:
                return jsonify({
                    'success': False,
                    'error': 'Monthly token limit exceeded. Please upgrade your plan.'
                }), 429

        conversations_data = get_conversations()
        conversation_id = f"conv_{len(conversations_data) + 1}"

        # Simple echo response for demo
        response = f"Echo: {message}"

        # Record usage for billing
        record_usage(
            user_id=user_id,
            operation_type='chat',
            tokens_used=estimated_tokens,
            compute_time=0.5,  # Simulated compute time
            model_id=model_id if model_id != 'default' else None
        )

        conversation = {
            'id': conversation_id,
            'model_id': model_id,
            'messages': [
                {'role': 'user', 'content': message},
                {'role': 'assistant', 'content': response}
            ],
            'created_at': datetime.now().isoformat()
        }

        conversations_data[conversation_id] = conversation
        save_to_fallback('conversations', conversation_id, conversation)

        return jsonify({
            'success': True,
            'response': response,
            'conversation_id': conversation_id,
            'tokens_used': estimated_tokens
        })

    except Exception as e:
        logger.error(f"Error in chat: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/conversations/<conversation_id>')
def get_conversation(conversation_id):
    conversations_data = get_conversations()
    conversation = conversations_data.get(conversation_id, [])
    return jsonify({
        'success': True,
        'conversation': conversation
    })

# Training endpoints
@app.route('/api/training/start', methods=['POST'])
@jwt_required()
def start_training():
    data = request.get_json()
    model_id = data.get('model_id')
    models_data = get_models()

    if model_id in models_data:
        models_data[model_id]['status'] = 'training'
        models_data[model_id]['training_started'] = datetime.now().isoformat()
        # Note: Using old simple format for demo - replace with save_models() for full PostgreSQL integration
        save_to_fallback('models', model_id, models_data[model_id])

        return jsonify({
            'success': True,
            'message': 'Training started',
            'model': models_data[model_id]
        })

    return jsonify({'success': False, 'error': 'Model not found'}), 404

@app.route('/api/training/status/<model_id>')
def training_status(model_id):
    models_data = get_models()
    if model_id in models_data:
        return jsonify({
            'success': True,
            'status': models_data[model_id]['status']
        })

    return jsonify({'success': False, 'error': 'Model not found'}), 404

# Database stats endpoint
@app.route('/api/stats', methods=['GET'])
def get_stats():
    users_data = get_users()
    models_data = get_models()
    conversations_data = get_conversations()

    return jsonify({
        'success': True,
        'stats': {
            'total_users': len(users_data),
            'total_models': len(models_data),
            'total_conversations': len(conversations_data),
            'database_type': 'PostgreSQL'
        }
    })

@app.route('/api/training/progress/<int:model_id>')
def get_training_progress(model_id):
    """Get real-time training progress for a model"""
    try:
        # Simulate training progress data
        progress = {
            'model_id': model_id,
            'status': 'training',
            'epoch': 7,
            'total_epochs': 10,
            'loss': 0.25,
            'accuracy': 0.82,
            'eta_minutes': 15,
            'samples_processed': 850,
            'total_samples': 1200
        }

        return jsonify(progress)
    except Exception as e:
        logger.error(f"Error getting training progress: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/models/<int:model_id>/versions')
def get_model_versions(model_id):
    """Get all versions of a model"""
    try:
        # Simulate model version history
        versions = [
            {
                'version': '1.0.0',
                'created_at': '2025-07-15T10:00:00Z',
                'metrics': {'accuracy': 0.78, 'loss': 0.35},
                'status': 'active'
            },
            {
                'version': '1.1.0',
                'created_at': '2025-07-15T12:30:00Z',
                'metrics': {'accuracy': 0.82, 'loss': 0.25},
                'status': 'latest'
            }
        ]

        return jsonify({
            'model_id': model_id,
            'versions': versions
        })
    except Exception as e:
        logger.error(f"Error getting model versions: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/training/hyperparameters', methods=['POST'])
def optimize_hyperparameters():
    """Auto-optimize hyperparameters for training"""
    try:
        data = request.get_json()
        training_type = data.get('training_type', 'general')

        # Intelligent hyperparameter suggestions
        suggestions = {
            'learning_rate': 0.0001,
            'batch_size': 8,
            'epochs': 10,
            'warmup_steps': 100,
            'weight_decay': 0.01,
            'dropout': 0.1,
            'optimizer': 'adamw',
            'scheduler': 'cosine',
            'reasoning': {
                'learning_rate': 'Conservative rate for stable fine-tuning',
                'batch_size': 'Optimal for memory efficiency with quality gradients',
                'epochs': 'Sufficient for convergence without overfitting'
            }
        }

        if training_type == 'conversational':
            suggestions.update({
                'learning_rate': 0.00005,
                'context_length': 2048,
                'temperature': 0.7
            })
        elif training_type == 'technical':
            suggestions.update({
                'learning_rate': 0.0002,
                'context_length': 4096,
                'temperature': 0.3
            })

        return jsonify({
            'status': 'success',
            'suggestions': suggestions,
            'confidence': 0.85
        })
    except Exception as e:
        logger.error(f"Error optimizing hyperparameters: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/models/<int:model_id>/evaluate', methods=['POST'])
def evaluate_model(model_id):
    """Evaluate model performance with comprehensive metrics"""
    try:
        data = request.get_json()
        test_data = data.get('test_data', [])

        # Simulate comprehensive evaluation
        evaluation_results = {
            'model_id': model_id,
            'timestamp': datetime.utcnow().isoformat(),
            'metrics': {
                'accuracy': 0.85,
                'perplexity': 2.3,
                'bleu_score': 0.78,
                'rouge_l': 0.82,
                'coherence_score': 0.88,
                'relevance_score': 0.91
            },
            'performance_breakdown': {
                'question_answering': 0.87,
                'text_generation': 0.83,
                'summarization': 0.89,
                'reasoning': 0.81
            },
            'benchmark_comparison': {
                'baseline_model': 0.72,
                'industry_average': 0.79,
                'top_performer': 0.93
            },
            'recommendations': [
                'Consider increasing training epochs for better reasoning performance',
                'Model excels at summarization tasks',
                'Strong performance compared to baseline'
            ]
        }

        return jsonify(evaluation_results)
    except Exception as e:
        logger.error(f"Error evaluating model: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/training/datasets/analyze', methods=['POST'])
def analyze_training_data():
    """Analyze training data quality and provide insights"""
    try:
        data = request.get_json()
        dataset_content = data.get('content', '')

        # Simulate data analysis
        analysis = {
            'total_tokens': len(dataset_content.split()),
            'total_lines': len(dataset_content.split('\n')),
            'average_line_length': 45,
            'language_distribution': {
                'english': 0.95,
                'other': 0.05
            },
            'content_types': {
                'technical': 0.60,
                'conversational': 0.25,
                'instructional': 0.15
            },
            'quality_score': 0.88,
            'recommendations': [
                'Good variety in content types',
                'Consider adding more conversational examples',
                'High quality technical content detected'
            ],
            'estimated_training_time': '45 minutes',
            'recommended_epochs': 12
        }

        return jsonify(analysis)
    except Exception as e:
        logger.error(f"Error analyzing training data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/models/<int:model_id>/chat', methods=['POST'])
def chat_with_model(model_id):
    data = request.get_json()
    message = data.get('message', '')

    # Simulate interaction with the model
    response = f"Response from model {model_id}: {message}"

    return jsonify({'response': response})

@app.route('/api/users/<int:user_id>/usage')
def get_user_usage(user_id):
    """Retrieve user-specific usage statistics"""
    try:
        # Simulate usage data
        usage_data = {
            'user_id': user_id,
            'api_calls': 150,
            'data_storage': 2.5,
            'models_trained': 3,
            'last_active': datetime.utcnow().isoformat()
        }

        return jsonify(usage_data)
    except Exception as e:
        logger.error(f"Error getting user usage: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/monitoring/system-health')
def get_system_health():
    """Get comprehensive system health information"""
    try:
        import psutil
        import time

        # Memory information
        memory = psutil.virtual_memory()
        process = psutil.Process()
        process_memory = process.memory_info().rss / (1024**3)  # GB

        warnings = []
        if process_memory > 6:
            warnings.append(f"High memory usage: {process_memory:.2f}GB")

        health_data = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'warning' if warnings else 'healthy',
            'memory': {
                'status': 'warning' if process_memory > 6 else 'healthy',
                'memory_usage': {
                    'system_memory_gb': memory.total / (1024**3),
                    'available_memory_gb': memory.available / (1024**3),
                    'process_memory_gb': process_memory,
                    'memory_percent': process.memory_percent()
                },
                'warnings': warnings
            },
            'dependencies': {
                'psutil_available': True,
                'database_available': get_db_connection() is not None,
                'transformers_available': True,  # Assuming available
                'torch_available': True  # Assuming available
            }
        }

        return jsonify(health_data)
    except ImportError:
        # Fallback if psutil not available
        health_data = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',
            'memory': {
                'status': 'unknown',
                'memory_usage': {},
                'warnings': ['Memory monitoring unavailable - psutil not installed']
            },
            'dependencies': {
                'psutil_available': False,
                'database_available': get_db_connection() is not None,
                'transformers_available': True,
                'torch_available': True
            }
        }
        return jsonify(health_data)
    except Exception as e:
        logger.error(f"Error getting system health: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/monitoring/performance')
def get_performance_metrics():
    """Get performance metrics and statistics"""
    try:
        # Simulate performance data - replace with actual metrics collection
        import time
        import random

        uptime = time.time() - 1642694400  # Simulate uptime from some start time

        performance_data = {
            'uptime_seconds': uptime,
            'total_requests': random.randint(500, 2000),
            'error_count': random.randint(0, 50),
            'error_rate': random.uniform(0.5, 5.0),
            'requests_per_second': random.uniform(1.0, 10.0),
            'avg_response_time': random.uniform(100, 800),
            'min_response_time': random.uniform(50, 150),
            'max_response_time': random.uniform(800, 2000),
            'p50_response_time': random.uniform(150, 400),
            'p95_response_time': random.uniform(400, 800),
            'p99_response_time': random.uniform(800, 1500),
            'model_stats': {
                'model_1': {
                    'requests': random.randint(100, 500),
                    'errors': random.randint(0, 10),
                    'total_time': random.uniform(1000, 5000),
                    'avg_response_time': random.uniform(200, 600)
                },
                'model_2': {
                    'requests': random.randint(50, 300),
                    'errors': random.randint(0, 5),
                    'total_time': random.uniform(500, 3000),
                    'avg_response_time': random.uniform(150, 500)
                }
            }
        }

        return jsonify(performance_data)
    except Exception as e:
        logger.error(f"Error getting performance metrics: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/monitoring/alerts')
def get_alerts():
    """Get system alerts and notifications"""
    try:
        # Simulate alerts - replace with actual alert system
        alerts = [
            {
                'id': 1,
                'type': 'warning',
                'message': 'High memory usage detected',
                'timestamp': datetime.now().isoformat(),
                'severity': 'medium',
                'resolved': False
            },
            {
                'id': 2,
                'type': 'info',
                'message': 'Model training completed successfully',
                'timestamp': (datetime.now() - timedelta(minutes=30)).isoformat(),
                'severity': 'low',
                'resolved': True
            }
        ]

        return jsonify({
            'alerts': alerts,
            'unresolved_count': len([a for a in alerts if not a['resolved']])
        })
    except Exception as e:
        logger.error(f"Error getting alerts: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Analytics endpoints
@app.route('/api/analytics')
def get_analytics():
    time_range = request.args.get('range', '7d')

    # Generate sample analytics data based on time range
    days = {'1d': 1, '7d': 7, '30d': 30, '90d': 90}[time_range]

    # Sample data generation
    import random
    import datetime

    # Generate time series data
    def generate_series(base_value, days, volatility=0.1):
        series = []
        current = base_value
        for i in range(days):
            current += random.uniform(-volatility * base_value, volatility * base_value)
            series.append(max(0, int(current)))
        return series

    # Overview metrics
    total_users = 1250 + random.randint(-50, 100)
    active_users = int(total_users * 0.35) + random.randint(-20, 30)
    total_models = 48 + random.randint(-5, 10)
    total_conversations = 15600 + random.randint(-500, 1000)
    revenue = 12500 + random.randint(-1000, 2000)
    growth = round(random.uniform(2.5, 15.2), 1)

    analytics_data = {
        'overview': {
            'totalUsers': total_users,
            'activeUsers': active_users,
            'totalModels': total_models,
            'totalConversations': total_conversations,
            'revenue': revenue,
            'growth': growth
        },
        'userMetrics': {
            'newUsers': generate_series(25, days, 0.3),
            'activeUsers': generate_series(active_users // days, days, 0.2),
            'retention': generate_series(68, days, 0.05)
        },
        'modelMetrics': {
            'modelUsage': generate_series(150, days, 0.25),
            'performanceStats': [
                {'name': 'Legal Assistant v2', 'usage': 450, 'rating': '4.9', 'type': 'Legal'},
                {'name': 'Medical Advisor', 'usage': 380, 'rating': '4.8', 'type': 'Healthcare'},
                {'name': 'Financial Analyst', 'usage': 320, 'rating': '4.7', 'type': 'Finance'},
                {'name': 'Code Reviewer', 'usage': 280, 'rating': '4.6', 'type': 'Technology'},
                {'name': 'Content Creator', 'usage': 220, 'rating': '4.5', 'type': 'Marketing'}
            ],
            'trainingMetrics': generate_series(8, days, 0.4)
        },
        'revenueMetrics': {
            'revenue': generate_series(revenue // days, days, 0.15),
            'subscriptions': generate_series(85, days, 0.1),
            'churn': generate_series(3.2, days, 0.3)
        },
        'systemMetrics': {
            'apiCalls': generate_series(2500, days, 0.2),
            'responseTime': generate_series(250, days, 0.15),
            'errorRate': generate_series(0.8, days, 0.5)
        }
    }

    return jsonify(analytics_data)

@app.route('/api/analytics/export/<format>')
def export_analytics(format):
    if format not in ['csv', 'pdf', 'json']:
        return jsonify({'error': 'Invalid export format'}), 400

    # Generate export data
    export_data = {
        'exported_at': datetime.datetime.now().isoformat(),
        'format': format,
        'data_url': f'/downloads/analytics_export_{format}_{int(time.time())}.{format}'
    }

    return jsonify(export_data)

@app.route('/api/analytics/users')
def get_user_analytics():
    # Detailed user analytics
    user_data = {
        'demographics': {
            'by_subscription': {
                'Free': 65,
                'Individual': 25,
                'Professional': 8,
                'Enterprise': 2
            },
            'by_region': {
                'North America': 45,
                'Europe': 30,
                'Asia': 20,
                'Other': 5
            }
        },
        'engagement': {
            'daily_active': 45,
            'weekly_active': 120,
            'monthly_active': 280,
            'avg_session_duration': 24.5,
            'avg_messages_per_session': 12.3
        },
        'growth': {
            'new_signups_today': 8,
            'new_signups_this_week': 45,
            'new_signups_this_month': 180
        }
    }

    return jsonify(user_data)

@app.route('/api/analytics/models')
def get_model_analytics():
    # Model performance analytics
    model_data = {
        'performance': {
            'total_models': 48,
            'active_models': 35,
            'training_models': 3,
            'avg_accuracy': 0.92,
            'avg_response_time': 1.8
        },
        'usage': {
            'total_conversations': 15600,
            'total_messages': 186000,
            'total_tokens': 23000000,
            'avg_conversation_length': 12
        },
        'popular_models': [
            {'name': 'Legal Assistant v2', 'conversations': 2400, 'rating': 4.9},
            {'name': 'Medical Advisor', 'conversations': 1950, 'rating': 4.8},
            {'name': 'Financial Analyst', 'conversations': 1600, 'rating': 4.7},
            {'name': 'Code Reviewer', 'conversations': 1200, 'rating': 4.6},
            {'name': 'Content Creator', 'conversations': 980, 'rating': 4.5}
        ]
    }

    return jsonify(model_data)

@app.route('/api/analytics/revenue')
def get_revenue_analytics():
    # Revenue and subscription analytics
    revenue_data = {
        'overview': {
            'mrr': 12500,
            'arr': 150000,
            'total_revenue': 45000,
            'growth_rate': 8.5
        },
        'subscriptions': {
            'total_subscribers': 425,
            'new_this_month': 45,
            'churned_this_month': 12,
            'churn_rate': 2.8,
            'ltv': 450
        },
        'by_tier': {
            'Free': {'count': 275, 'revenue': 0},
            'Individual': {'count': 105,'revenue': 1049},
            'Professional': {'count': 35, 'revenue': 1749},
            'Enterprise': {'count': 10, 'revenue': 1999}
        }
    }

    return jsonify(revenue_data)

# Monitoring endpoints
@app.route('/api/monitoring/metrics')
def get_monitoring_metrics():
    return jsonify({
        'cpu_usage': random.uniform(20, 80),
        'memory_usage': random.uniform(30, 70),
        'disk_usage': random.uniform(10, 60),
        'active_connections': random.randint(50, 200),
        'requests_per_minute': random.randint(100, 500),
        'error_rate': random.uniform(0.1, 2.0)
    })

# Reports endpoints
@app.route('/api/reports')
def get_reports():
    # Sample report history
    sample_reports = [
        {
            'id': 'rpt_001',
            'name': 'User Activity Report - July 2025',
            'type': 'user_activity',
            'generated_at': '2025-07-15 10:30:00',
            'size': '2.4 MB',
            'status': 'completed'
        },
        {
            'id': 'rpt_002',
            'name': 'Model Performance Report - Q2 2025',
            'type': 'model_performance',
            'generated_at': '2025-07-10 14:15:00',
            'size': '1.8 MB',
            'status': 'completed'
        },
        {
            'id': 'rpt_003',
            'name': 'Revenue Analysis - June 2025',
            'type': 'revenue_analysis',
            'generated_at': '2025-07-05 09:00:00',
            'size': '950 KB',
            'status': 'completed'
        }
    ]

    return jsonify({'reports': sample_reports})

@app.route('/api/reports/generate', methods=['POST'])
def generate_report():
    data = request.get_json()
    report_type = data.get('type')

    if not report_type:
        return jsonify({'error': 'Report type is required'}), 400

    # Simulate report generation
    import time
    time.sleep(1)  # Simulate processing time

    report_id = f"rpt_{int(time.time())}"

    return jsonify({
        'success': True,
        'report_id': report_id,
        'message': f'Report generation started for {report_type}',
        'estimated_completion': '2-3 minutes'
    })

@app.route('/api/reports/<report_id>/download')
def download_report(report_id):
    format_type = request.args.get('format', 'pdf')

    # In a real implementation, you would generate or retrieve the actual report
    # For demo purposes, we'll return a simple text response

    if format_type == 'pdf':
        from io import BytesIO
        import time

        # Create a simple text file simulating PDF content
        content = f"""
CUSTOM GPT ANALYTICS REPORT
Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}
Report ID: {report_id}

EXECUTIVE SUMMARY
================
This report provides comprehensive analytics for your Custom GPT platform.

USER METRICS
============
- Total Users: 1,250
- Active Users: 450
- New Users (30 days): 180
- User Retention: 68%

MODEL PERFORMANCE
=================
- Total Models: 48
- Active Models: 35
- Average Accuracy: 92%
- Total Conversations: 15,600

REVENUE ANALYTICS
=================
- Monthly Recurring Revenue: $12,500
- Annual Recurring Revenue: $150,000
- Growth Rate: 8.5%
- Customer Lifetime Value: $450

RECOMMENDATIONS
===============
1. Focus on improving user retention
2. Expand model library in popular categories
3. Implement advanced analytics features
4. Consider enterprise pricing tier

This is a sample report for demonstration purposes.
        """

        response = make_response(content)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=report_{report_id}.pdf'
        return response

    elif format_type == 'csv':
        import csv
        from io import StringIO

        output = StringIO()
        writer = csv.writer(output)

        # Sample CSV data
        writer.writerow(['Metric', 'Value', 'Date'])
        writer.writerow(['Total Users', '1250', '2025-07-16'])
        writer.writerow(['Active Users', '450', '2025-07-16'])
        writer.writerow(['New Users', '180', '2025-07-16'])
        writer.writerow(['Revenue', '12500', '2025-07-16'])

        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=report_{report_id}.csv'
        return response

    return jsonify({'error': 'Unsupported format'}), 400

@app.route('/api/reports/schedule', methods=['POST'])
def schedule_report():
    data = request.get_json()

    schedule_data = {
        'id': f"schedule_{int(time.time())}",
        'report_type': data.get('report_type'),
        'frequency': data.get('frequency'),  # daily, weekly, monthly
        'time': data.get('time'),
        'recipients': data.get('recipients', []),
        'active': True
    }

    return jsonify({
        'success': True,
        'schedule': schedule_data,
        'message': 'Report scheduled successfully'
    })

# Billing and Subscription endpoints
@app.route('/api/billing/subscription', methods=['GET'])
@jwt_required()
def get_subscription():
    """Get user's current subscription details."""
    try:
        user_id = get_jwt_identity()
        subscription = get_user_subscription(user_id)
        
        if not subscription:
            return jsonify({
                'success': False,
                'error': 'No subscription found'
            }), 404

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

@app.route('/api/billing/plans', methods=['GET'])
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
                    '10,000 tokens per month',
                    'Basic chat interface',
                    'Up to 3 custom models',
                    'Community support'
                ],
                'limits': {
                    'tokens_per_month': 10000,
                    'models': 3,
                    'api_calls_per_minute': 10,
                    'training_hours': 1.0
                }
            },
            {
                'id': 'individual',
                'name': 'Individual',
                'price': 19.99,
                'currency': 'USD',
                'interval': 'monthly',
                'features': [
                    '100,000 tokens per month',
                    'Advanced chat features',
                    'Up to 10 custom models',
                    'Model customization',
                    'Email support',
                    'Training analytics'
                ],
                'limits': {
                    'tokens_per_month': 100000,
                    'models': 10,
                    'api_calls_per_minute': 60,
                    'training_hours': 5.0
                }
            },
            {
                'id': 'professional',
                'name': 'Professional',
                'price': 99.99,
                'currency': 'USD',
                'interval': 'monthly',
                'features': [
                    '1,000,000 tokens per month',
                    'Advanced model training',
                    'Up to 50 custom models',
                    'API access',
                    'Priority support',
                    'Analytics dashboard',
                    'Export capabilities'
                ],
                'limits': {
                    'tokens_per_month': 1000000,
                    'models': 50,
                    'api_calls_per_minute': 300,
                    'training_hours': 25.0
                }
            },
            {
                'id': 'enterprise',
                'name': 'Enterprise',
                'price': 499.99,
                'currency': 'USD',
                'interval': 'monthly',
                'features': [
                    'Unlimited tokens',
                    'Custom model training',
                    'Unlimited custom models',
                    'Dedicated support',
                    'SLA guarantees',
                    'Advanced security',
                    'Custom integrations'
                ],
                'limits': {
                    'tokens_per_month': -1,  # Unlimited
                    'models': -1,  # Unlimited
                    'api_calls_per_minute': 1000,
                    'training_hours': -1  # Unlimited
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

@app.route('/api/billing/usage', methods=['GET'])
@jwt_required()
def get_usage():
    """Get user's current usage statistics."""
    try:
        user_id = get_jwt_identity()
        subscription = get_user_subscription(user_id)
        
        if not subscription:
            return jsonify({
                'success': False,
                'error': 'No subscription found'
            }), 404

        # Get usage from current period
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Get current period usage
                cursor.execute('''
                    SELECT 
                        SUM(tokens_used) as total_tokens,
                        COUNT(*) as total_requests,
                        SUM(compute_time_seconds) as total_compute_time
                    FROM usage_records 
                    WHERE user_id = %s 
                    AND created_at >= %s 
                    AND created_at <= %s
                ''', (user_id, subscription['current_period_start'], subscription['current_period_end']))
                
                usage_stats = cursor.fetchone()
                
                usage = {
                    'current_period': {
                        'start_date': subscription['current_period_start'].isoformat(),
                        'end_date': subscription['current_period_end'].isoformat(),
                        'tokens_used': subscription['monthly_tokens_used'],
                        'tokens_limit': subscription['monthly_token_limit'],
                        'training_hours_used': subscription['monthly_training_hours_used'],
                        'training_hours_limit': subscription['monthly_training_hours_limit'],
                        'api_calls': usage_stats['total_requests'] if usage_stats['total_requests'] else 0
                    },
                    'tier': subscription['tier'],
                    'status': subscription['status']
                }
                
                return jsonify({
                    'success': True,
                    'usage': usage
                })
                
            finally:
                cursor.close()
                conn.close()

    except Exception as e:
        logger.error(f"Error getting usage: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/billing/upgrade', methods=['POST'])
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

        # Get plan details
        plan_limits = {
            'free': {'tokens': 10000, 'models': 3, 'training_hours': 1.0},
            'individual': {'tokens': 100000, 'models': 10, 'training_hours': 5.0},
            'professional': {'tokens': 1000000, 'models': 50, 'training_hours': 25.0},
            'enterprise': {'tokens': -1, 'models': -1, 'training_hours': -1}
        }

        if plan_id not in plan_limits:
            return jsonify({
                'success': False,
                'error': 'Invalid plan_id'
            }), 400

        # Update subscription in database
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                limits = plan_limits[plan_id]
                
                cursor.execute('''
                    UPDATE subscriptions 
                    SET tier = %s, 
                        monthly_token_limit = %s,
                        max_models = %s,
                        monthly_training_hours_limit = %s,
                        updated_at = %s
                    WHERE user_id = %s
                ''', (
                    plan_id,
                    limits['tokens'],
                    limits['models'],
                    limits['training_hours'],
                    datetime.utcnow(),
                    user_id
                ))
                
                conn.commit()
                
                # Get updated subscription
                subscription = get_user_subscription(user_id)
                
                return jsonify({
                    'success': True,
                    'message': f'Successfully upgraded to {plan_id} plan',
                    'subscription': subscription
                })
                
            finally:
                cursor.close()
                conn.close()

    except Exception as e:
        logger.error(f"Error upgrading subscription: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/billing/cancel', methods=['POST'])
@jwt_required()
def cancel_subscription():
    """Cancel user subscription."""
    try:
        user_id = get_jwt_identity()
        
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE subscriptions 
                    SET status = 'cancelled', updated_at = %s 
                    WHERE user_id = %s
                ''', (datetime.utcnow(), user_id))
                
                conn.commit()
                
                return jsonify({
                    'success': True,
                    'message': 'Subscription cancelled successfully'
                })
                
            finally:
                cursor.close()
                conn.close()

    except Exception as e:
        logger.error(f"Error cancelling subscription: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/billing/payment-methods', methods=['GET'])
@jwt_required()
def get_payment_methods():
    """Get user's payment methods."""
    try:
        user_id = get_jwt_identity()
        
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM payment_methods 
                    WHERE user_id = %s 
                    ORDER BY is_default DESC, created_at DESC
                ''', (user_id,))
                
                payment_methods = cursor.fetchall()
                methods_list = [dict(method) for method in payment_methods]
                
                # Convert UUIDs to strings and format dates
                for method in methods_list:
                    method['id'] = str(method['id'])
                    method['user_id'] = str(method['user_id'])
                    method['created_at'] = method['created_at'].isoformat()
                
                return jsonify({
                    'success': True,
                    'payment_methods': methods_list
                })
                
            finally:
                cursor.close()
                conn.close()

    except Exception as e:
        logger.error(f"Error getting payment methods: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/billing/payment-methods', methods=['POST'])
@jwt_required()
def add_payment_method():
    """Add a new payment method."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # This would integrate with Stripe in production
        # For demo purposes, we'll create a mock payment method
        
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                payment_method_id = str(uuid.uuid4())
                
                cursor.execute('''
                    INSERT INTO payment_methods 
                    (id, user_id, stripe_payment_method_id, type, last_four, brand, exp_month, exp_year, is_default)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (
                    payment_method_id,
                    user_id,
                    f"pm_{payment_method_id[:24]}",  # Mock Stripe ID
                    data.get('type', 'card'),
                    data.get('last_four', '4242'),
                    data.get('brand', 'visa'),
                    data.get('exp_month', 12),
                    data.get('exp_year', 2025),
                    data.get('is_default', False)
                ))
                
                conn.commit()
                
                return jsonify({
                    'success': True,
                    'message': 'Payment method added successfully'
                })
                
            finally:
                cursor.close()
                conn.close()

    except Exception as e:
        logger.error(f"Error adding payment method: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/billing/invoices', methods=['GET'])
@jwt_required()
def get_invoices():
    """Get user's billing invoices."""
    try:
        user_id = get_jwt_identity()
        
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM billing_invoices 
                    WHERE user_id = %s 
                    ORDER BY created_at DESC
                    LIMIT 12
                ''', (user_id,))
                
                invoices = cursor.fetchall()
                invoices_list = []
                
                for invoice in invoices:
                    invoice_dict = dict(invoice)
                    invoice_dict['id'] = str(invoice_dict['id'])
                    invoice_dict['user_id'] = str(invoice_dict['user_id'])
                    invoice_dict['created_at'] = invoice_dict['created_at'].isoformat()
                    invoice_dict['billing_period_start'] = invoice_dict['billing_period_start'].isoformat()
                    invoice_dict['billing_period_end'] = invoice_dict['billing_period_end'].isoformat()
                    if invoice_dict['paid_at']:
                        invoice_dict['paid_at'] = invoice_dict['paid_at'].isoformat()
                    invoices_list.append(invoice_dict)
                
                return jsonify({
                    'success': True,
                    'invoices': invoices_list
                })
                
            finally:
                cursor.close()
                conn.close()

    except Exception as e:
        logger.error(f"Error getting invoices: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def record_usage(user_id, operation_type, tokens_used=0, compute_time=0.0, model_id=None):
    """Record usage for billing purposes."""
    try:
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Calculate cost (example: $0.002 per 1000 tokens)
                cost_cents = int((tokens_used / 1000) * 0.2 * 100)  # Convert to cents
                
                cursor.execute('''
                    INSERT INTO usage_records 
                    (user_id, model_id, operation_type, tokens_used, compute_time_seconds, cost_cents)
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', (user_id, model_id, operation_type, tokens_used, compute_time, cost_cents))
                
                # Update subscription usage
                cursor.execute('''
                    UPDATE subscriptions 
                    SET monthly_tokens_used = monthly_tokens_used + %s
                    WHERE user_id = %s
                ''', (tokens_used, user_id))
                
                conn.commit()
                
            finally:
                cursor.close()
                conn.close()
                
    except Exception as e:
        logger.error(f"Error recording usage: {e}")

# JWT error handlers
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({
        'success': False,
        'error': 'Token has expired'
    }), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        'success': False,
        'error': 'Invalid token'
    }), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        'success': False,
        'error': 'Authorization token is required'
    }), 401

if __name__ == '__main__':
    logger.info("Starting Simple Custom GPT App")

    # Initialize database tables
    if init_database():
        logger.info("Database initialized successfully")
    else:
        logger.error("Failed to initialize database")

    app.run(host='0.0.0.0', port=5000, debug=True)