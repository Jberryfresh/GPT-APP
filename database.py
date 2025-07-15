
"""
Database Models and Initialization
=================================

SQLAlchemy models for the Custom GPT system including users, models,
training sessions, subscriptions, and audit logging.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import uuid
import json
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import JSON
from sqlalchemy import event, text
import logging

logger = logging.getLogger(__name__)

# Initialize SQLAlchemy
db = SQLAlchemy()
migrate = Migrate()

class TimestampMixin:
    """Mixin for adding timestamp fields to models."""
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class User(db.Model, TimestampMixin):
    """User model for authentication and profile management."""
    __tablename__ = 'users'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    
    # Account status
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    email_verified_at = db.Column(db.DateTime)
    last_login_at = db.Column(db.DateTime)
    failed_login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime)
    
    # Profile information
    bio = db.Column(db.Text)
    avatar_url = db.Column(db.String(500))
    timezone = db.Column(db.String(50), default='UTC')
    
    # API access
    api_key = db.Column(db.String(255), unique=True)
    api_key_created_at = db.Column(db.DateTime)
    
    # Relationships
    models = db.relationship('Model', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    training_sessions = db.relationship('TrainingSession', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    datasets = db.relationship('Dataset', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    subscriptions = db.relationship('Subscription', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    usage_records = db.relationship('UsageRecord', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Set password hash."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash."""
        return check_password_hash(self.password_hash, password)
    
    def generate_api_key(self):
        """Generate a new API key."""
        self.api_key = str(uuid.uuid4()).replace('-', '')
        self.api_key_created_at = datetime.utcnow()
        return self.api_key
    
    def is_locked(self):
        """Check if account is locked."""
        return self.locked_until and self.locked_until > datetime.utcnow()
    
    def lock_account(self, duration_minutes=15):
        """Lock account for specified duration."""
        self.locked_until = datetime.utcnow() + timedelta(minutes=duration_minutes)
        self.failed_login_attempts = 0
    
    def unlock_account(self):
        """Unlock account."""
        self.locked_until = None
        self.failed_login_attempts = 0
    
    @property
    def full_name(self):
        """Get full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': str(self.id),
            'email': self.email,
            'username': self.username,
            'full_name': self.full_name,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat(),
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None
        }

class Model(db.Model, TimestampMixin):
    """AI model registry."""
    __tablename__ = 'models'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    
    # Model identification
    name = db.Column(db.String(255), nullable=False)
    model_id = db.Column(db.String(255), nullable=False, index=True)
    version = db.Column(db.String(50), default='1.0.0')
    
    # Model details
    base_model = db.Column(db.String(255), nullable=False)
    model_type = db.Column(db.String(50), default='fine_tuned')  # base, fine_tuned, adapter
    description = db.Column(db.Text)
    
    # Training information
    training_session_id = db.Column(UUID(as_uuid=True), db.ForeignKey('training_sessions.id'))
    dataset_id = db.Column(UUID(as_uuid=True), db.ForeignKey('datasets.id'))
    
    # Storage and deployment
    model_path = db.Column(db.String(500))
    model_size_mb = db.Column(db.Float)
    is_deployed = db.Column(db.Boolean, default=False)
    is_public = db.Column(db.Boolean, default=False)
    
    # Performance metrics
    training_accuracy = db.Column(db.Float)
    validation_accuracy = db.Column(db.Float)
    training_loss = db.Column(db.Float)
    validation_loss = db.Column(db.Float)
    
    # Usage tracking
    total_inferences = db.Column(db.BigInteger, default=0)
    last_used_at = db.Column(db.DateTime)
    
    # Configuration
    config = db.Column(JSON)
    
    # Relationships
    usage_records = db.relationship('UsageRecord', backref='model', lazy='dynamic')
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': str(self.id),
            'name': self.name,
            'model_id': self.model_id,
            'version': self.version,
            'base_model': self.base_model,
            'model_type': self.model_type,
            'description': self.description,
            'is_deployed': self.is_deployed,
            'is_public': self.is_public,
            'model_size_mb': self.model_size_mb,
            'training_accuracy': self.training_accuracy,
            'validation_accuracy': self.validation_accuracy,
            'total_inferences': self.total_inferences,
            'created_at': self.created_at.isoformat(),
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None
        }

class Dataset(db.Model, TimestampMixin):
    """Training dataset registry."""
    __tablename__ = 'datasets'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    
    # Dataset identification
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    
    # Dataset details
    file_path = db.Column(db.String(500))
    file_size_mb = db.Column(db.Float)
    total_samples = db.Column(db.Integer)
    data_format = db.Column(db.String(50))  # json, csv, txt, parquet
    
    # Processing status
    status = db.Column(db.String(50), default='uploaded')  # uploaded, processing, ready, error
    processing_error = db.Column(db.Text)
    processed_at = db.Column(db.DateTime)
    
    # Quality metrics
    quality_score = db.Column(db.Float)
    duplicate_count = db.Column(db.Integer, default=0)
    average_length = db.Column(db.Float)
    
    # Configuration
    preprocessing_config = db.Column(JSON)
    
    # Relationships
    models = db.relationship('Model', backref='dataset', lazy='dynamic')
    training_sessions = db.relationship('TrainingSession', backref='dataset', lazy='dynamic')
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'file_size_mb': self.file_size_mb,
            'total_samples': self.total_samples,
            'data_format': self.data_format,
            'status': self.status,
            'quality_score': self.quality_score,
            'created_at': self.created_at.isoformat(),
            'processed_at': self.processed_at.isoformat() if self.processed_at else None
        }

class TrainingSession(db.Model, TimestampMixin):
    """Model training session tracking."""
    __tablename__ = 'training_sessions'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    dataset_id = db.Column(UUID(as_uuid=True), db.ForeignKey('datasets.id'), nullable=False)
    
    # Session identification
    name = db.Column(db.String(255), nullable=False)
    experiment_name = db.Column(db.String(255))
    
    # Training configuration
    base_model = db.Column(db.String(255), nullable=False)
    training_config = db.Column(JSON)
    
    # Status tracking
    status = db.Column(db.String(50), default='queued')  # queued, running, completed, failed, cancelled
    progress_percentage = db.Column(db.Float, default=0.0)
    current_epoch = db.Column(db.Integer, default=0)
    total_epochs = db.Column(db.Integer)
    
    # Timing
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    estimated_completion = db.Column(db.DateTime)
    
    # Results
    final_loss = db.Column(db.Float)
    final_accuracy = db.Column(db.Float)
    best_checkpoint_path = db.Column(db.String(500))
    output_model_path = db.Column(db.String(500))
    
    # Logs and errors
    training_logs = db.Column(db.Text)
    error_message = db.Column(db.Text)
    
    # Resource usage
    gpu_hours_used = db.Column(db.Float, default=0.0)
    compute_cost = db.Column(db.Float, default=0.0)
    
    # Relationships
    models = db.relationship('Model', backref='training_session', lazy='dynamic')
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': str(self.id),
            'name': self.name,
            'experiment_name': self.experiment_name,
            'base_model': self.base_model,
            'status': self.status,
            'progress_percentage': self.progress_percentage,
            'current_epoch': self.current_epoch,
            'total_epochs': self.total_epochs,
            'final_loss': self.final_loss,
            'final_accuracy': self.final_accuracy,
            'gpu_hours_used': self.gpu_hours_used,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class Subscription(db.Model, TimestampMixin):
    """User subscription and billing information."""
    __tablename__ = 'subscriptions'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    
    # Subscription details
    tier = db.Column(db.String(50), default='free')  # free, individual, professional, enterprise
    status = db.Column(db.String(50), default='active')  # active, cancelled, past_due, unpaid
    
    # Billing
    stripe_customer_id = db.Column(db.String(255))
    stripe_subscription_id = db.Column(db.String(255))
    current_period_start = db.Column(db.DateTime)
    current_period_end = db.Column(db.DateTime)
    
    # Usage limits
    monthly_token_limit = db.Column(db.BigInteger)
    monthly_tokens_used = db.Column(db.BigInteger, default=0)
    monthly_training_hours_limit = db.Column(db.Float)
    monthly_training_hours_used = db.Column(db.Float, default=0.0)
    
    # Features
    can_train_models = db.Column(db.Boolean, default=False)
    can_use_api = db.Column(db.Boolean, default=False)
    max_models = db.Column(db.Integer, default=1)
    priority_support = db.Column(db.Boolean, default=False)
    
    def reset_monthly_usage(self):
        """Reset monthly usage counters."""
        self.monthly_tokens_used = 0
        self.monthly_training_hours_used = 0.0
    
    def has_token_quota(self, tokens_needed=1):
        """Check if user has available token quota."""
        if self.monthly_token_limit is None:  # Unlimited
            return True
        return (self.monthly_tokens_used + tokens_needed) <= self.monthly_token_limit
    
    def has_training_quota(self, hours_needed=0.1):
        """Check if user has available training quota."""
        if self.monthly_training_hours_limit is None:  # Unlimited
            return True
        return (self.monthly_training_hours_used + hours_needed) <= self.monthly_training_hours_limit
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': str(self.id),
            'tier': self.tier,
            'status': self.status,
            'monthly_token_limit': self.monthly_token_limit,
            'monthly_tokens_used': self.monthly_tokens_used,
            'monthly_training_hours_limit': self.monthly_training_hours_limit,
            'monthly_training_hours_used': self.monthly_training_hours_used,
            'can_train_models': self.can_train_models,
            'can_use_api': self.can_use_api,
            'max_models': self.max_models,
            'current_period_end': self.current_period_end.isoformat() if self.current_period_end else None
        }

class UsageRecord(db.Model, TimestampMixin):
    """Track API usage for billing and analytics."""
    __tablename__ = 'usage_records'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    model_id = db.Column(UUID(as_uuid=True), db.ForeignKey('models.id'))
    
    # Usage details
    operation_type = db.Column(db.String(50), nullable=False)  # inference, training, fine_tuning
    tokens_used = db.Column(db.Integer, default=0)
    compute_time_seconds = db.Column(db.Float, default=0.0)
    
    # Request details
    request_id = db.Column(db.String(255))
    endpoint = db.Column(db.String(255))
    method = db.Column(db.String(10))
    status_code = db.Column(db.Integer)
    
    # Billing
    cost_cents = db.Column(db.Integer, default=0)  # Cost in cents
    
    # Request metadata
    request_metadata = db.Column(JSON)
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': str(self.id),
            'operation_type': self.operation_type,
            'tokens_used': self.tokens_used,
            'compute_time_seconds': self.compute_time_seconds,
            'cost_cents': self.cost_cents,
            'request_metadata': self.request_metadata,
            'created_at': self.created_at.isoformat()
        }

class AuditLog(db.Model, TimestampMixin):
    """Audit log for tracking system activities."""
    __tablename__ = 'audit_logs'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    
    # Event details
    action = db.Column(db.String(100), nullable=False)
    resource_type = db.Column(db.String(50))
    resource_id = db.Column(db.String(255))
    
    # Request details
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    request_id = db.Column(db.String(255))
    
    # Event data
    old_values = db.Column(JSON)
    new_values = db.Column(JSON)
    event_metadata = db.Column(JSON)
    
    # Status
    success = db.Column(db.Boolean, default=True)
    error_message = db.Column(db.Text)

def init_db(app):
    """Initialize database with Flask app."""
    db.init_app(app)
    migrate.init_app(app, db)
    
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Create default subscription tiers
        create_default_subscription_tiers()
        
        logger.info("Database initialized successfully")

def create_default_subscription_tiers():
    """Create default subscription tier configurations."""
    # This would typically be handled by a separate configuration system
    # or migration scripts in production
    pass

def create_admin_user(email, username, password):
    """Create an admin user."""
    try:
        existing_user = User.query.filter(
            (User.email == email) | (User.username == username)
        ).first()
        
        if existing_user:
            logger.warning(f"User already exists: {email}")
            return existing_user
        
        user = User(
            email=email,
            username=username,
            is_active=True,
            is_verified=True,
            email_verified_at=datetime.utcnow()
        )
        user.set_password(password)
        user.generate_api_key()
        
        db.session.add(user)
        
        # Create admin subscription
        subscription = Subscription(
            user_id=user.id,
            tier='enterprise',
            status='active',
            monthly_token_limit=None,  # Unlimited
            monthly_training_hours_limit=None,  # Unlimited
            can_train_models=True,
            can_use_api=True,
            max_models=100,
            priority_support=True,
            current_period_start=datetime.utcnow(),
            current_period_end=datetime.utcnow() + timedelta(days=365)
        )
        
        db.session.add(subscription)
        db.session.commit()
        
        logger.info(f"Admin user created: {email}")
        return user
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating admin user: {e}")
        raise

# Event listeners for automatic updates
@event.listens_for(Model, 'after_insert')
def increment_model_count(mapper, connection, target):
    """Update user's model count after creating a model."""
    # This could be used for subscription enforcement
    pass

@event.listens_for(UsageRecord, 'after_insert')
def update_subscription_usage(mapper, connection, target):
    """Update subscription usage after recording usage."""
    if target.tokens_used > 0:
        connection.execute(
            text("""
                UPDATE subscriptions 
                SET monthly_tokens_used = monthly_tokens_used + :tokens
                WHERE user_id = :user_id
            """),
            {"tokens": target.tokens_used, "user_id": target.user_id}
        )
