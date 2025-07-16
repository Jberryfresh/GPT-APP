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
        save_users(users_data)

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
        save_users(users_data)
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
    save_models(models_data)

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
    save_conversations(conversations_data)

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
        save_models(models_data)

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

if __name__ == '__main__':
    logger.info("Starting Simple Custom GPT App")
    
    # Initialize database tables
    if init_database():
        logger.info("Database initialized successfully")
    else:
        logger.error("Failed to initialize database")
    
    app.run(host='0.0.0.0', port=5000, debug=True)