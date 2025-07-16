
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Simple CORS setup for development
CORS(app, origins=['*'], supports_credentials=True)

# Simple in-memory storage (replace with database later)
users = {}
models = {}
conversations = {}

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
    email = data.get('email')
    password = data.get('password')
    
    # Simple authentication (replace with real auth)
    if email and password:
        user_id = f"user_{len(users) + 1}"
        users[user_id] = {
            'id': user_id,
            'email': email,
            'created_at': datetime.now().isoformat()
        }
        return jsonify({
            'success': True,
            'user': users[user_id],
            'token': f"token_{user_id}"
        })
    
    return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if email and password:
        user_id = f"user_{len(users) + 1}"
        users[user_id] = {
            'id': user_id,
            'email': email,
            'created_at': datetime.now().isoformat()
        }
        return jsonify({
            'success': True,
            'user': users[user_id],
            'token': f"token_{user_id}"
        })
    
    return jsonify({'success': False, 'error': 'Invalid data'}), 400

# Models management
@app.route('/api/models', methods=['GET'])
def list_models():
    return jsonify({
        'success': True,
        'models': list(models.values())
    })

@app.route('/api/models', methods=['POST'])
def create_model():
    data = request.get_json()
    model_id = f"model_{len(models) + 1}"
    
    models[model_id] = {
        'id': model_id,
        'name': data.get('name', 'Untitled Model'),
        'description': data.get('description', ''),
        'status': 'created',
        'created_at': datetime.now().isoformat()
    }
    
    return jsonify({
        'success': True,
        'model': models[model_id]
    })

# Chat functionality
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message')
    conversation_id = data.get('conversation_id', 'default')
    
    if conversation_id not in conversations:
        conversations[conversation_id] = []
    
    # Simple echo response (replace with actual AI inference)
    response = f"Echo: {message}"
    
    conversations[conversation_id].append({
        'user': message,
        'assistant': response,
        'timestamp': datetime.now().isoformat()
    })
    
    return jsonify({
        'success': True,
        'response': response,
        'conversation_id': conversation_id
    })

@app.route('/api/conversations/<conversation_id>')
def get_conversation(conversation_id):
    return jsonify({
        'success': True,
        'conversation': conversations.get(conversation_id, [])
    })

# Training endpoints
@app.route('/api/training/start', methods=['POST'])
def start_training():
    data = request.get_json()
    model_id = data.get('model_id')
    
    if model_id in models:
        models[model_id]['status'] = 'training'
        models[model_id]['training_started'] = datetime.now().isoformat()
        
        return jsonify({
            'success': True,
            'message': 'Training started',
            'model': models[model_id]
        })
    
    return jsonify({'success': False, 'error': 'Model not found'}), 404

@app.route('/api/training/status/<model_id>')
def training_status(model_id):
    if model_id in models:
        return jsonify({
            'success': True,
            'status': models[model_id]['status']
        })
    
    return jsonify({'success': False, 'error': 'Model not found'}), 404

if __name__ == '__main__':
    logger.info("Starting Simple Custom GPT App")
    app.run(host='0.0.0.0', port=5000, debug=True)
