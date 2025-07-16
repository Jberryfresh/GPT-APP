from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import json
import logging
from datetime import datetime
from replit import db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Simple CORS setup for development
CORS(app, origins=['*'], supports_credentials=True)

# Initialize Replit database (no need for in-memory storage)
def get_users():
    return db.get('users', {})

def save_users(users_data):
    db['users'] = users_data

def get_models():
    return db.get('models', {})

def save_models(models_data):
    db['models'] = models_data

def get_conversations():
    return db.get('conversations', {})

def save_conversations(conversations_data):
    db['conversations'] = conversations_data


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
            'database_keys': list(db.keys())
        }
    })

if __name__ == '__main__':
    logger.info("Starting Simple Custom GPT App")
    app.run(host='0.0.0.0', port=5000, debug=True)