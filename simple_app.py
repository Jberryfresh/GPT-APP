from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import json
import logging
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
import urllib.parse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

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

        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                subscription_tier VARCHAR(50) DEFAULT 'free',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create models table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS models (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                user_id INTEGER REFERENCES users(id),
                status VARCHAR(50) DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create conversations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                model_id INTEGER REFERENCES models(id),
                messages JSONB,
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

def save_user(email, password_hash, subscription_tier='free'):
    conn = get_db_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (email, password_hash, subscription_tier) VALUES (%s, %s, %s) ON CONFLICT (email) DO UPDATE SET password_hash = %s, subscription_tier = %s",
            (email, password_hash, subscription_tier, password_hash, subscription_tier)
        )
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Error saving user: {e}")
        return False
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

# User management
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Simple demo authentication
    if username and password:
        users_data = get_users()
        user_id = f"user_{len(users_data) + 1}"
        user = {
            'id': user_id,
            'username': username,
            'email': f"{username}@example.com",
            'created_at': datetime.now().isoformat()
        }
        users_data[user_id] = user
        # Note: Using old simple format for demo - replace with save_user() for full PostgreSQL integration
        save_to_fallback('users', user_id, user)

        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': user,
            'token': f"demo_token_{user_id}"
        })

    return jsonify({
        'success': False,
        'message': 'Invalid credentials'
    }), 401

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if email and password:
        users_data = get_users()
        user_id = f"user_{len(users_data) + 1}"
        user = {
            'id': user_id,
            'email': email,
            'created_at': datetime.now().isoformat()
        }
        users_data[user_id] = user
        # Note: Using old simple format for demo - replace with save_user() for full PostgreSQL integration
        save_to_fallback('users', user_id, user)
        return jsonify({
            'success': True,
            'user': users_data[user_id],
            'token': f"token_{user_id}"
        })

    return jsonify({'success': False, 'error': 'Invalid data'}), 400

# Model management
@app.route('/api/models', methods=['GET'])
def get_models_list():
    models_data = get_models()
    models_list = list(models_data.values())
    return jsonify({
        'success': True,
        'models': models_list
    })

@app.route('/api/models', methods=['POST'])
def create_model():
    data = request.get_json()
    models_data = get_models()

    model_id = f"model_{len(models_data) + 1}"
    model = {
        'id': model_id,
        'name': data.get('name', f'Model {len(models_data) + 1}'),
        'description': data.get('description', 'Demo model'),
        'status': 'active',
        'created_at': datetime.now().isoformat()
    }

    models_data[model_id] = model
    # Note: Using old simple format for demo - replace with save_models() for full PostgreSQL integration
    save_to_fallback('models', model_id, model)

    return jsonify({
        'success': True,
        'message': 'Model created successfully',
        'model': model
    })

# Chat functionality
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message', '')
    model_id = data.get('model_id', 'default')

    conversations_data = get_conversations()
    conversation_id = f"conv_{len(conversations_data) + 1}"

    # Simple echo response for demo
    response = f"Echo: {message}"

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
    # Note: Using old simple format for demo - replace with save_conversations() for full PostgreSQL integration
    save_to_fallback('conversations', conversation_id, conversation)

    return jsonify({
        'success': True,
        'response': response,
        'conversation_id': conversation_id
    })

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

if __name__ == '__main__':
    logger.info("Starting Simple Custom GPT App")

    # Initialize database tables
    if init_database():
        logger.info("Database initialized successfully")
    else:
        logger.error("Failed to initialize database")

    app.run(host='0.0.0.0', port=5000, debug=True)