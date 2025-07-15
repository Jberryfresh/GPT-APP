"""
Training Management Routes
=========================

API endpoints for managing model training operations.
"""

from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
import json
import logging
import threading
from datetime import datetime
from pathlib import Path
from database import db, TrainingSession, Dataset, User
import uuid

logger = logging.getLogger(__name__)

training_bp = Blueprint('training', __name__)

# Global training status storage (in production, use Redis or database)
training_jobs = {}

@training_bp.route('/training/jobs', methods=['GET'])
@jwt_required()
def list_training_jobs():
    """List all training jobs for the user."""
    try:
        user_id = get_jwt_identity()
        user_jobs = {k: v for k, v in training_jobs.items() if v.get('user_id') == user_id}

        return jsonify({
            'success': True,
            'jobs': list(user_jobs.values()),
            'count': len(user_jobs)
        })

    except Exception as e:
        logger.error(f"Error listing training jobs: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@training_bp.route('/training/jobs/<job_id>', methods=['GET'])
@jwt_required()
def get_training_job(job_id):
    """Get details of a specific training job."""
    try:
        user_id = get_jwt_identity()

        if job_id not in training_jobs:
            return jsonify({
                'success': False,
                'error': f'Training job {job_id} not found'
            }), 404

        job = training_jobs[job_id]
        if job.get('user_id') != user_id:
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403

        return jsonify({
            'success': True,
            'job': job
        })

    except Exception as e:
        logger.error(f"Error getting training job: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@training_bp.route('/training/start', methods=['POST'])
@jwt_required()
def start_training():
    """Start a new training job."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400

        # Validate required parameters
        required_fields = ['experiment_name', 'data_files', 'model_name']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'{field} is required'
                }), 400

        experiment_name = data['experiment_name']
        data_files = data['data_files']
        model_name = data['model_name']
        output_dir = data.get('output_dir', './models')

        # Validate data files exist
        for file_path in data_files:
            if not os.path.exists(file_path):
                return jsonify({
                    'success': False,
                    'error': f'Data file not found: {file_path}'
                }), 400

        # Generate job ID
        job_id = f"train_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Create job record
        job = {
            'job_id': job_id,
            'user_id': user_id,
            'experiment_name': experiment_name,
            'model_name': model_name,
            'data_files': data_files,
            'output_dir': output_dir,
            'status': 'queued',
            'created_at': datetime.now().isoformat(),
            'started_at': None,
            'completed_at': None,
            'error': None,
            'progress': 0,
            'logs': []
        }

        training_jobs[job_id] = job

        # Start training in background thread
        training_thread = threading.Thread(
            target=_run_training_job,
            args=(job_id, data)
        )
        training_thread.daemon = True
        training_thread.start()

        return jsonify({
            'success': True,
            'job_id': job_id,
            'message': 'Training job started'
        })

    except Exception as e:
        logger.error(f"Error starting training: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def _run_training_job(job_id, training_params):
    """Run training job in background."""
    try:
        # Import training modules
        import sys
        import os
        parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        sys.path.insert(0, parent_dir)

        from training_pipeline import TrainingPipeline, DataProcessingConfig, LoRAConfig

        # Update job status
        job = training_jobs[job_id]
        job['status'] = 'running'
        job['started_at'] = datetime.now().isoformat()
        job['logs'].append(f"Training started at {job['started_at']}")

        # Configure training
        data_config = DataProcessingConfig(
            max_length=training_params.get('max_length', 512),
            chunk_size=training_params.get('chunk_size', 1000),
            validation_split=training_params.get('validation_split', 0.1),
            remove_duplicates=not training_params.get('keep_duplicates', False)
        )

        lora_config = LoRAConfig(
            r=training_params.get('lora_r', 16),
            lora_alpha=training_params.get('lora_alpha', 32),
            lora_dropout=training_params.get('lora_dropout', 0.1)
        )

        # Initialize pipeline
        pipeline = TrainingPipeline(
            model_name=training_params['model_name'],
            data_config=data_config,
            lora_config=lora_config
        )

        job['logs'].append("Training pipeline initialized")
        job['progress'] = 10

        # Run training
        result = pipeline.run_training(
            data_files=training_params['data_files'],
            output_dir=training_params['output_dir'],
            experiment_name=training_params['experiment_name']
        )

        if result['success']:
            job['status'] = 'completed'
            job['completed_at'] = datetime.now().isoformat()
            job['progress'] = 100
            job['output_path'] = result['output_dir']
            job['logs'].append(f"Training completed successfully at {job['completed_at']}")
        else:
            job['status'] = 'failed'
            job['completed_at'] = datetime.now().isoformat()
            job['error'] = result['error']
            job['logs'].append(f"Training failed: {result['error']}")

    except Exception as e:
        logger.error(f"Training job {job_id} failed: {e}")
        job = training_jobs[job_id]
        job['status'] = 'failed'
        job['completed_at'] = datetime.now().isoformat()
        job['error'] = str(e)
        job['logs'].append(f"Training failed with error: {str(e)}")

@training_bp.route('/training/jobs/<job_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_training_job(job_id):
    """Cancel a training job."""
    try:
        user_id = get_jwt_identity()

        if job_id not in training_jobs:
            return jsonify({
                'success': False,
                'error': f'Training job {job_id} not found'
            }), 404

        job = training_jobs[job_id]
        if job.get('user_id') != user_id:
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403

        if job['status'] in ['completed', 'failed', 'cancelled']:
            return jsonify({
                'success': False,
                'error': f'Cannot cancel job with status: {job["status"]}'
            }), 400

        # Update job status
        job['status'] = 'cancelled'
        job['completed_at'] = datetime.now().isoformat()
        job['logs'].append(f"Training cancelled at {job['completed_at']}")

        return jsonify({
            'success': True,
            'message': f'Training job {job_id} cancelled'
        })

    except Exception as e:
        logger.error(f"Error cancelling training job: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@training_bp.route('/training/jobs/<job_id>/logs', methods=['GET'])
@jwt_required()
def get_training_logs(job_id):
    """Get logs for a training job."""
    try:
        user_id = get_jwt_identity()

        if job_id not in training_jobs:
            return jsonify({
                'success': False,
                'error': f'Training job {job_id} not found'
            }), 404

        job = training_jobs[job_id]
        if job.get('user_id') != user_id:
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403

        return jsonify({
            'success': True,
            'logs': job.get('logs', []),
            'status': job['status'],
            'progress': job.get('progress', 0)
        })

    except Exception as e:
        logger.error(f"Error getting training logs: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@training_bp.route('/training/validate-data', methods=['POST'])
@jwt_required()
def validate_training_data():
    """Validate training data files."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400

        data_files = data.get('data_files', [])
        if not data_files:
            return jsonify({
                'success': False,
                'error': 'data_files is required'
            }), 400

        validation_results = []
        total_size = 0
        total_files = 0

        for file_path in data_files:
            result = {
                'file_path': file_path,
                'exists': os.path.exists(file_path),
                'size': 0,
                'readable': False,
                'error': None
            }

            if result['exists']:
                try:
                    stat = os.stat(file_path)
                    result['size'] = stat.st_size
                    total_size += stat.st_size
                    total_files += 1

                    # Try to read a small portion
                    with open(file_path, 'r', encoding='utf-8') as f:
                        f.read(1024)  # Read first 1KB
                    result['readable'] = True

                except Exception as e:
                    result['error'] = str(e)

            validation_results.append(result)

        # Summary
        valid_files = sum(1 for r in validation_results if r['exists'] and r['readable'])

        return jsonify({
            'success': True,
            'validation_results': validation_results,
            'summary': {
                'total_files': len(data_files),
                'valid_files': valid_files,
                'total_size_bytes': total_size,
                'total_size_mb': total_size / (1024 * 1024)
            }
        })

    except Exception as e:
        logger.error(f"Error validating training data: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@training_bp.route('/training/sessions', methods=['GET'])
@jwt_required()
def list_training_sessions():
    """List user's training sessions."""
    try:
        user_id = get_jwt_identity()

        sessions = TrainingSession.query.filter_by(user_id=user_id).order_by(
            TrainingSession.created_at.desc()
        ).all()

        return jsonify({
            'success': True,
            'sessions': [session.to_dict() for session in sessions],
            'count': len(sessions)
        })

    except Exception as e:
        logger.error(f"Error listing training sessions: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@training_bp.route('/training/sessions', methods=['POST'])
@jwt_required()
def create_training_session():
    """Create a new training session."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400

        # Validate required fields
        required_fields = ['name', 'base_model', 'dataset_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'{field} is required'
                }), 400

        # Verify dataset exists and belongs to user
        dataset = Dataset.query.filter_by(
            id=data['dataset_id'], 
            user_id=user_id
        ).first()
        if not dataset:
            return jsonify({
                'success': False,
                'error': 'Dataset not found or access denied'
            }), 404

        # Create training session
        session = TrainingSession(
            user_id=user_id,
            dataset_id=data['dataset_id'],
            name=data['name'],
            base_model=data['base_model'],
            training_config=data.get('training_config', {}),
            total_epochs=data.get('epochs', 3),
            status='queued'
        )

        db.session.add(session)
        db.session.commit()

        # TODO: Queue training job
        logger.info(f"Training session {session.id} queued for user {user_id}")

        return jsonify({
            'success': True,
            'session': session.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating training session: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@training_bp.route('/training/sessions/<session_id>', methods=['GET'])
@jwt_required()
def get_training_session(session_id):
    """Get a specific training session."""
    try:
        user_id = get_jwt_identity()

        session = TrainingSession.query.filter_by(
            id=session_id, 
            user_id=user_id
        ).first()

        if not session:
            return jsonify({
                'success': False,
                'error': 'Training session not found'
            }), 404

        return jsonify({
            'success': True,
            'session': session.to_dict()
        })

    except Exception as e:
        logger.error(f"Error getting training session: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@training_bp.route('/datasets', methods=['GET'])
@jwt_required()
def list_datasets():
    """List user's datasets."""
    try:
        user_id = get_jwt_identity()

        datasets = Dataset.query.filter_by(user_id=user_id).order_by(
            Dataset.created_at.desc()
        ).all()

        return jsonify({
            'success': True,
            'datasets': [dataset.to_dict() for dataset in datasets],
            'count': len(datasets)
        })

    except Exception as e:
        logger.error(f"Error listing datasets: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@training_bp.route('/datasets', methods=['POST'])
@jwt_required()
def upload_dataset():
    """Upload a new dataset."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400

        # Create dataset record
        dataset = Dataset(
            user_id=user_id,
            name=data.get('name', 'Untitled Dataset'),
            description=data.get('description', ''),
            data_format=data.get('format', 'json'),
            status='uploaded'
        )

        db.session.add(dataset)
        db.session.commit()

        return jsonify({
            'success': True,
            'dataset': dataset.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error uploading dataset: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500