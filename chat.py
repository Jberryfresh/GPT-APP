"""
Chat and Inference Routes
========================

API endpoints for chat completions and model inference.
"""

from flask import Blueprint, jsonify, request, current_app, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
import json
import logging
import uuid
from datetime import datetime

try:
    from model_inference import InferenceConfig
except ImportError:
    # Fallback if model_inference is not available
    class InferenceConfig:
        def __init__(self, max_new_tokens=256, temperature=0.7, top_p=0.9):
            self.max_new_tokens = max_new_tokens
            self.temperature = temperature
            self.top_p = top_p

logger = logging.getLogger(__name__)

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat/completions', methods=['POST'], endpoint='chat_completions')
def chat_completions():
    """OpenAI-compatible chat completions endpoint."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400

        messages = data.get('messages', [])
        model_id = data.get('model')

        if not messages:
            return jsonify({
                'success': False,
                'error': 'messages are required'
            }), 400

        # Configure inference
        config = InferenceConfig(
            max_new_tokens=data.get('max_tokens', 256),
            temperature=data.get('temperature', 0.7),
            top_p=data.get('top_p', 0.9)
        )

        # Get model manager
        model_manager = getattr(current_app, 'model_manager', None)
        if not model_manager:
            return jsonify({
                'success': False,
                'error': 'Model manager not available'
            }), 503

        # Get the last user message
        user_message = ""
        for msg in reversed(messages):
            if msg.get('role') == 'user':
                user_message = msg.get('content', '')
                break

        if not user_message:
            return jsonify({
                'success': False,
                'error': 'No user message found'
            }), 400

        # Generate conversation ID
        conversation_id = get_jwt_identity() or 'anonymous'

        # Generate response
        try:
            response = model_manager.chat(user_message, conversation_id, model_id, config)
        except Exception as e:
            logger.error(f"Model inference error: {e}")
            response = "I apologize, but I'm having trouble processing your request right now."

        return jsonify({
            'id': str(uuid.uuid4()),
            'object': 'chat.completion',
            'created': int(datetime.now().timestamp()),
            'model': model_id or 'default',
            'choices': [{
                'index': 0,
                'message': {
                    'role': 'assistant',
                    'content': response
                },
                'finish_reason': 'stop'
            }],
            'usage': {
                'prompt_tokens': len(user_message.split()),
                'completion_tokens': len(response.split()),
                'total_tokens': len(user_message.split()) + len(response.split())
            }
        })

    except Exception as e:
        logger.error(f"Error in chat completions: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@chat_bp.route('/chat/conversations', methods=['GET'])
@jwt_required()
def chat_completions():
    """OpenAI-compatible chat completions endpoint."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400

        messages = data.get('messages', [])
        model_id = data.get('model', 'default')

        if not messages:
            return jsonify({
                'success': False,
                'error': 'messages are required'
            }), 400

        # Extract the latest user message
        latest_message = messages[-1].get('content', '') if messages else ''

        # Configure inference
        from model_inference import InferenceConfig
        config = InferenceConfig(
            max_new_tokens=data.get('max_tokens', 256),
            temperature=data.get('temperature', 0.7),
            top_p=data.get('top_p', 0.9)
        )

        # Get model manager
        model_manager = current_app.model_manager

        # Generate conversation ID
        conversation_id = get_jwt_identity() or str(uuid.uuid4())

        # Generate response
        response_text = model_manager.chat(latest_message, conversation_id, model_id, config)

        # Return OpenAI-compatible format
        return jsonify({
            'id': f'chatcmpl-{uuid.uuid4()}',
            'object': 'chat.completion',
            'created': int(datetime.now().timestamp()),
            'model': model_id,
            'choices': [{
                'index': 0,
                'message': {
                    'role': 'assistant',
                    'content': response_text
                },
                'finish_reason': 'stop'
            }],
            'usage': {
                'prompt_tokens': len(latest_message.split()),
                'completion_tokens': len(response_text.split()),
                'total_tokens': len(latest_message.split()) + len(response_text.split())
            }
        })

    except Exception as e:
        logger.error(f"Error in chat completions: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@chat_bp.route('/chat/conversations', methods=['GET'])
@jwt_required()
def get_conversations():
    """OpenAI-compatible chat completions endpoint."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'error': {
                    'message': 'No JSON data provided',
                    'type': 'invalid_request_error'
                }
            }), 400

        # Extract parameters
        messages = data.get('messages', [])
        model_id = data.get('model', 'default')
        stream = data.get('stream', False)
        max_tokens = data.get('max_tokens', 256)
        temperature = data.get('temperature', 0.7)
        top_p = data.get('top_p', 0.9)
        top_k = data.get('top_k', 50)

        if not messages:
            return jsonify({
                'error': {
                    'message': 'messages is required',
                    'type': 'invalid_request_error'
                }
            }), 400

        # Get the last user message
        user_message = None
        for msg in reversed(messages):
            if msg.get('role') == 'user':
                user_message = msg.get('content', '')
                break

        if not user_message:
            return jsonify({
                'error': {
                    'message': 'No user message found',
                    'type': 'invalid_request_error'
                }
            }), 400

        # Configure inference
        config = InferenceConfig(
            max_new_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k
        )

        # Get model manager
        model_manager = current_app.model_manager

        # Generate conversation ID
        conversation_id = get_jwt_identity() or 'anonymous'

        if stream:
            return _stream_response(model_manager, user_message, conversation_id, model_id, config)
        else:
            return _non_stream_response(model_manager, user_message, conversation_id, model_id, config)

    except Exception as e:
        logger.error(f"Error in chat completions: {e}")
        return jsonify({
            'error': {
                'message': str(e),
                'type': 'internal_error'
            }
        }), 500

def _non_stream_response(model_manager, user_message, conversation_id, model_id, config):
    """Handle non-streaming response."""
    try:
        # Generate response
        response = model_manager.chat(
            user_message, 
            conversation_id, 
            model_id if model_id != 'default' else None, 
            config
        )

        # Create OpenAI-compatible response
        completion_id = f"chatcmpl-{uuid.uuid4().hex[:29]}"

        return jsonify({
            'id': completion_id,
            'object': 'chat.completion',
            'created': int(datetime.now().timestamp()),
            'model': model_id,
            'choices': [{
                'index': 0,
                'message': {
                    'role': 'assistant',
                    'content': response
                },
                'finish_reason': 'stop'
            }],
            'usage': {
                'prompt_tokens': len(user_message.split()),
                'completion_tokens': len(response.split()),
                'total_tokens': len(user_message.split()) + len(response.split())
            }
        })

    except Exception as e:
        logger.error(f"Error in non-stream response: {e}")
        return jsonify({
            'error': {
                'message': str(e),
                'type': 'internal_error'
            }
        }), 500

def _stream_response(model_manager, user_message, conversation_id, model_id, config):
    """Handle streaming response."""
    def generate():
        try:
            completion_id = f"chatcmpl-{uuid.uuid4().hex[:29]}"
            created = int(datetime.now().timestamp())

            # Send initial chunk
            initial_chunk = {
                'id': completion_id,
                'object': 'chat.completion.chunk',
                'created': created,
                'model': model_id,
                'choices': [{
                    'index': 0,
                    'delta': {
                        'role': 'assistant',
                        'content': ''
                    },
                    'finish_reason': None
                }]
            }
            yield f"data: {json.dumps(initial_chunk)}\n\n"

            # Stream response tokens
            for token in model_manager.chat_streaming(
                user_message, 
                conversation_id, 
                model_id if model_id != 'default' else None, 
                config
            ):
                chunk = {
                    'id': completion_id,
                    'object': 'chat.completion.chunk',
                    'created': created,
                    'model': model_id,
                    'choices': [{
                        'index': 0,
                        'delta': {
                            'content': token
                        },
                        'finish_reason': None
                    }]
                }
                yield f"data: {json.dumps(chunk)}\n\n"

            # Send final chunk
            final_chunk = {
                'id': completion_id,
                'object': 'chat.completion.chunk',
                'created': created,
                'model': model_id,
                'choices': [{
                    'index': 0,
                    'delta': {},
                    'finish_reason': 'stop'
                }]
            }
            yield f"data: {json.dumps(final_chunk)}\n\n"
            yield "data: [DONE]\n\n"

        except Exception as e:
            logger.error(f"Error in stream response: {e}")
            error_chunk = {
                'error': {
                    'message': str(e),
                    'type': 'internal_error'
                }
            }
            yield f"data: {json.dumps(error_chunk)}\n\n"

    return Response(
        generate(),
        mimetype='text/plain',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'text/event-stream'
        }
    )

@chat_bp.route('/chat/conversations', methods=['GET'])
@jwt_required()
def list_conversations():
    """List user's conversations."""
    try:
        user_id = get_jwt_identity()
        # In a real implementation, you would fetch from database
        # For now, return empty list
        return jsonify({
            'success': True,
            'conversations': [],
            'count': 0
        })

    except Exception as e:
        logger.error(f"Error listing conversations: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@chat_bp.route('/chat/conversations/<conversation_id>', methods=['DELETE'])
@jwt_required()
def clear_conversation(conversation_id):
    """Clear a conversation."""
    try:
        model_manager = current_app.model_manager
        model_manager.clear_conversation(conversation_id)

        return jsonify({
            'success': True,
            'message': f'Conversation {conversation_id} cleared'
        })

    except Exception as e:
        logger.error(f"Error clearing conversation: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@chat_bp.route('/chat/simple', methods=['POST'])
@jwt_required(optional=True)
def simple_chat():
    """Simple chat endpoint for quick testing."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400

        message = data.get('message')
        model_id = data.get('model_id')

        if not message:
            return jsonify({
                'success': False,
                'error': 'message is required'
            }), 400

        # Configure inference
        config = InferenceConfig(
            max_new_tokens=data.get('max_tokens', 256),
            temperature=data.get('temperature', 0.7),
            top_p=data.get('top_p', 0.9)
        )

        # Get model manager
        model_manager = current_app.model_manager

        # Generate conversation ID
        conversation_id = get_jwt_identity() or 'anonymous'

        # Generate response
        response = model_manager.chat(message, conversation_id, model_id, config)

        return jsonify({
            'success': True,
            'response': response,
            'model_id': model_id or 'default'
        })

    except Exception as e:
        logger.error(f"Error in simple chat: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500