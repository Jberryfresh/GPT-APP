from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import logging
import os
from pathlib import Path

# Import configuration
from config import get_config

# Import database
from database import db, migrate, init_db
from auth import create_admin_user

# Import API blueprints
from auth import auth_bp
from chat import chat_bp
from training import training_bp
from billing import billing_bp
from health import health_bp
from api_stats import api_stats_bp
from monitoring import monitoring_bp

# Import model manager
from model_inference import ModelManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # Load configuration
    config = get_config()

    # Configure Flask app
    app.config['SECRET_KEY'] = config.api.secret_key
    app.config['JWT_SECRET_KEY'] = config.api.jwt_secret_key
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = config.api.jwt_access_token_expires
    app.config['MAX_CONTENT_LENGTH'] = config.api.max_request_size

    # Database configuration
    if config.environment == 'production':
        app.config['SQLALCHEMY_DATABASE_URI'] = config.database.url
    else:
        # Use SQLite for development
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///custom_gpt.db'

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = config.debug

    # Initialize extensions with proper CORS settings
    if config.environment == 'development':
        # Allow common development origins and Replit URLs
        dev_origins = [
            'http://localhost:3000',
            'http://127.0.0.1:3000', 
            'http://0.0.0.0:3000',
            f'https://{os.environ.get("REPL_SLUG", "")}.{os.environ.get("REPL_OWNER", "")}.repl.co',
            f'https://{os.environ.get("REPL_ID", "")}.id.repl.co'
        ]
        # Filter out empty URLs
        dev_origins = [origin for origin in dev_origins if origin and not origin.endswith('.repl.co')]
        dev_origins.extend(['*'])  # Allow all in development
        
        CORS(app, 
             origins=dev_origins,
             supports_credentials=True, 
             allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
             methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    else:
        CORS(app, origins=config.api.cors_origins)
    jwt = JWTManager(app)

    # Initialize database
    init_db(app)

    # Initialize model manager
    try:
        app.model_manager = ModelManager()
        logger.info("Model manager initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize model manager: {e}")
        app.model_manager = None

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/v1')
    app.register_blueprint(chat_bp, url_prefix='/api/v1')
    app.register_blueprint(health_bp, url_prefix='/api/v1')
    app.register_blueprint(billing_bp, url_prefix='/api/v1')
    app.register_blueprint(training_bp, url_prefix='/api/v1')
    app.register_blueprint(api_stats_bp, url_prefix='/api/v1')
    app.register_blueprint(monitoring_bp, url_prefix='/api/v1')

    # Serve React frontend
    @app.route('/')
    def serve_frontend():
        """Serve the React frontend."""
        return send_from_directory('.', 'index.html')

    @app.route('/<path:path>')
    def serve_static(path):
        """Serve static files."""
        # Check if file exists in current directory
        if os.path.exists(os.path.join('.', path)):
            return send_from_directory('.', path)
        # For React Router - serve index.html for non-API routes
        if not path.startswith('api/'):
            return send_from_directory('.', 'index.html')
        # Let API routes fall through to 404 handler
        return "Not found", 404

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        if request.path.startswith('/api/'):
            return jsonify({
                'success': False,
                'error': 'API endpoint not found',
                'path': request.path
            }), 404
        # For non-API routes, serve index.html for client-side routing
        return send_from_directory('.', 'index.html')

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

    @app.errorhandler(413)
    def request_too_large(error):
        return jsonify({
            'success': False,
            'error': 'Request too large'
        }), 413

    return app

def main():
    """Main entry point."""
    try:
        app = create_app()
        config = get_config()
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise

    # Create admin user if it doesn't exist (development only)
    if config.environment == 'development':
        with app.app_context():
            try:
                admin = create_admin_user(
                    email='admin@example.com',
                    username='admin',
                    password='admin123'
                )
                logger.info(f"Admin user ready: {admin.email} (API Key: {admin.api_key})")
            except Exception as e:
                logger.warning(f"Admin user creation skipped: {e}")

    logger.info(f"Starting Custom GPT API on {config.api.host}:{config.api.port}")
    logger.info(f"Environment: {config.environment}")
    logger.info(f"Debug mode: {config.debug}")
    logger.info(f"Database: {app.config['SQLALCHEMY_DATABASE_URI']}")

    app.run(
        host=config.api.host,
        port=config.api.port,
        debug=config.debug,
        threaded=True
    )

if __name__ == "__main__":
    main()