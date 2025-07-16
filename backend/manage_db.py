
#!/usr/bin/env python3
"""
Database Management Utility
===========================

Utility script for managing database operations including
initialization, migrations, and user management.
"""

import click
import logging
from flask import Flask
from config import get_config
from database import db, create_admin_user, User, Subscription, Model, Dataset

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@click.group()
def cli():
    """Database management commands."""
    pass

@cli.command()
def init():
    """Initialize database with tables."""
    app = Flask(__name__)
    config = get_config()
    
    # Configure database
    if config.environment == 'production':
        app.config['SQLALCHEMY_DATABASE_URI'] = config.database.url
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///custom_gpt.db'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        logger.info("Database tables created successfully")

@cli.command()
@click.option('--email', prompt=True, help='Admin email address')
@click.option('--username', prompt=True, help='Admin username')
@click.option('--password', prompt=True, hide_input=True, help='Admin password')
def create_admin(email, username, password):
    """Create an admin user."""
    app = Flask(__name__)
    config = get_config()
    
    if config.environment == 'production':
        app.config['SQLALCHEMY_DATABASE_URI'] = config.database.url
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///custom_gpt.db'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    
    with app.app_context():
        try:
            user = create_admin_user(email, username, password)
            logger.info(f"Admin user created successfully")
            logger.info(f"Email: {user.email}")
            logger.info(f"Username: {user.username}")
            logger.info(f"API Key: {user.api_key}")
        except Exception as e:
            logger.error(f"Failed to create admin user: {e}")

@cli.command()
def stats():
    """Show database statistics."""
    app = Flask(__name__)
    config = get_config()
    
    if config.environment == 'production':
        app.config['SQLALCHEMY_DATABASE_URI'] = config.database.url
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///custom_gpt.db'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    
    with app.app_context():
        try:
            users_count = User.query.count()
            models_count = Model.query.count()
            datasets_count = Dataset.query.count()
            subscriptions_count = Subscription.query.count()
            
            logger.info("Database Statistics:")
            logger.info(f"  Users: {users_count}")
            logger.info(f"  Models: {models_count}")
            logger.info(f"  Datasets: {datasets_count}")
            logger.info(f"  Subscriptions: {subscriptions_count}")
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")

@cli.command()
def reset():
    """Reset database (WARNING: This will delete all data!)."""
    if click.confirm('This will delete ALL data. Are you sure?'):
        app = Flask(__name__)
        config = get_config()
        
        if config.environment == 'production':
            app.config['SQLALCHEMY_DATABASE_URI'] = config.database.url
        else:
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///custom_gpt.db'
        
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(app)
        
        with app.app_context():
            db.drop_all()
            db.create_all()
            logger.info("Database reset successfully")

if __name__ == '__main__':
    cli()
