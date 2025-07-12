# Custom GPT System

A comprehensive system for building, training, and deploying custom GPT models with domain-specific expertise. This system enables you to create specialized AI assistants trained on your own data and monetize them through subscription services.

## Features

- **Data Processing Pipeline**: Ingest data from multiple sources (text files, PDFs, web pages, structured data)
- **Parameter-Efficient Fine-Tuning**: Use LoRA/QLoRA techniques for efficient model training
- **Model Management**: Load, manage, and serve multiple custom models
- **API Interface**: RESTful API with streaming support for real-time interactions
- **Subscription System**: Built-in billing and user management for monetization
- **Scalable Architecture**: Microservices design with cloud deployment support

## Quick Start

### 1. Installation

```bash
# Clone or download the system
cd custom_gpt_system

# Install dependencies
pip install -r requirements.txt

# Create configuration
python main.py config --create-examples
```

### 2. Demo Setup

```bash
# Run the full demo to see the system in action
python main.py demo --full-demo --output-dir ./demo

# This creates sample data, demonstrates ingestion, and prepares training data
```

### 3. Data Ingestion

```bash
# Ingest text files
python main.py ingest --files document1.txt document2.pdf --output ingested.json

# Ingest entire directory
python main.py ingest --directory ./documents --recursive --output ingested.json

# Scrape web content
python main.py ingest --urls https://example.com/article1 https://example.com/article2 --output web_data.json
```

### 4. Model Training

```bash
# Train with specific files
python main.py train --data-files train1.txt train2.txt --model-name microsoft/DialoGPT-small --output-dir ./models

# Train with directory of files
python main.py train --data-dir ./training_data --output-dir ./models --experiment-name my_expert_model

# Advanced training options
python main.py train \
  --data-dir ./training_data \
  --model-name microsoft/DialoGPT-medium \
  --output-dir ./models \
  --experiment-name advanced_model \
  --lora-r 32 \
  --lora-alpha 64 \
  --max-length 1024 \
  --validation-split 0.15
```

### 5. Model Inference

```bash
# Interactive chat
python main.py infer --model-path ./models/my_expert_model --interactive --streaming

# Single prompt
python main.py infer --model-path ./models/my_expert_model --prompt "What is machine learning?"

# Advanced inference options
python main.py infer \
  --model-path ./models/my_expert_model \
  --interactive \
  --streaming \
  --temperature 0.8 \
  --max-tokens 512
```

## System Architecture

### Core Components

1. **Data Ingestion Pipeline** (`data_ingestion.py`)
   - Multi-format support (text, PDF, HTML, JSON, CSV)
   - Web scraping capabilities
   - Data validation and preprocessing
   - Deduplication and quality filtering

2. **Training Pipeline** (`training_pipeline.py`)
   - Parameter-Efficient Fine-Tuning (LoRA/QLoRA)
   - Automated data preparation
   - Distributed training support
   - Comprehensive evaluation and monitoring

3. **Model Inference** (`model_inference.py`)
   - Multi-model management
   - Conversation context handling
   - Streaming response generation
   - Performance optimization

4. **Configuration Management** (`config.py`)
   - Environment-based configuration
   - Production/development profiles
   - Security and validation

5. **CLI Interface** (`main.py`)
   - Complete command-line interface
   - Demo and testing utilities
   - Interactive and batch operations

### Data Flow

```
Raw Data → Ingestion → Processing → Training → Fine-tuned Model → Inference → User
    ↓           ↓           ↓           ↓            ↓            ↓
  Files,     Clean,     Format,    LoRA/QLoRA   Load &      Generate
  URLs,      Validate,  Chunk,     Training     Manage      Responses
  APIs       Dedupe     Tokenize
```

## Configuration

### Environment Variables

```bash
# Database
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=custom_gpt
export DB_USER=postgres
export DB_PASSWORD=your_password

# Redis
export REDIS_HOST=localhost
export REDIS_PORT=6379

# API
export API_HOST=0.0.0.0
export API_PORT=5000
export SECRET_KEY=your-secret-key
export JWT_SECRET_KEY=your-jwt-secret

# Models
export DEFAULT_MODEL=microsoft/DialoGPT-medium
export MODEL_CACHE_DIR=./models
export INFERENCE_DEVICE=auto

# Billing (for production)
export STRIPE_PUBLIC_KEY=pk_test_...
export STRIPE_SECRET_KEY=sk_test_...
export STRIPE_WEBHOOK_SECRET=whsec_...
```

### Configuration Files

```bash
# Create example configurations
python main.py config --create-examples

# Validate current configuration
python main.py config --validate

# View current configuration
python main.py config --show
```

## Training Custom Models

### Data Preparation

1. **Collect Domain Data**: Gather text documents, articles, manuals, or other content relevant to your domain
2. **Organize Files**: Place training data in a directory structure
3. **Quality Check**: Ensure content is high-quality and relevant

### Training Process

```bash
# Basic training
python main.py train --data-dir ./my_domain_data --output-dir ./models --experiment-name my_domain_expert

# Advanced training with custom parameters
python main.py train \
  --data-dir ./my_domain_data \
  --model-name microsoft/DialoGPT-medium \
  --output-dir ./models \
  --experiment-name my_domain_expert_v2 \
  --lora-r 32 \
  --lora-alpha 64 \
  --lora-dropout 0.05 \
  --max-length 1024 \
  --chunk-size 2000 \
  --validation-split 0.2
```

### Training Parameters

- **lora-r**: Rank of LoRA adaptation (higher = more capacity, more memory)
- **lora-alpha**: LoRA scaling parameter (typically 2x the rank)
- **lora-dropout**: Dropout rate for LoRA layers
- **max-length**: Maximum sequence length for training
- **chunk-size**: Size of text chunks for processing
- **validation-split**: Fraction of data used for validation

## Deployment

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set up configuration
cp config_development.json config.json

# Run training
python main.py train --data-dir ./data --output-dir ./models

# Start inference
python main.py infer --model-path ./models/my_model --interactive
```

### Production Deployment

1. **Infrastructure Setup**
   - GPU-enabled compute instances
   - PostgreSQL database
   - Redis cache
   - Load balancer

2. **Configuration**
   ```bash
   # Copy and customize production config
   cp config_production_template.json config_production.json
   # Edit config_production.json with your settings
   ```

3. **Environment Setup**
   ```bash
   # Set production environment
   export ENVIRONMENT=production
   export CONFIG_FILE=config_production.json
   
   # Set security keys
   export SECRET_KEY=$(openssl rand -hex 32)
   export JWT_SECRET_KEY=$(openssl rand -hex 32)
   ```

4. **Database Setup**
   ```bash
   # Initialize database schema
   python -c "from app import create_app; create_app().create_all()"
   ```

5. **Model Deployment**
   ```bash
   # Train production models
   python main.py train --data-dir ./production_data --output-dir ./production_models
   
   # Start API server
   gunicorn --bind 0.0.0.0:5000 --workers 4 app:app
   ```

## API Usage

### Starting the API Server

```bash
# Development
python app.py

# Production
gunicorn --bind 0.0.0.0:5000 --workers 4 app:app
```

### API Endpoints

```bash
# Health check
curl http://localhost:5000/health

# List models
curl http://localhost:5000/api/v1/models

# Chat completion
curl -X POST http://localhost:5000/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "model": "my_expert_model",
    "messages": [{"role": "user", "content": "Hello!"}],
    "stream": false
  }'

# Streaming chat
curl -X POST http://localhost:5000/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "model": "my_expert_model",
    "messages": [{"role": "user", "content": "Hello!"}],
    "stream": true
  }'
```

## Monetization

### Subscription Tiers

1. **Free Tier**
   - 1,000 tokens/month
   - Basic models only
   - Community support

2. **Individual Tier** ($9.99/month)
   - 50,000 tokens/month
   - All models
   - Email support

3. **Professional Tier** ($49.99/month)
   - 500,000 tokens/month
   - Custom model training
   - Priority support
   - API access

4. **Enterprise Tier** ($199.99/month)
   - Unlimited tokens
   - Dedicated infrastructure
   - Custom SLA
   - Phone support

### Payment Integration

```bash
# Set up Stripe keys
export STRIPE_PUBLIC_KEY=pk_live_...
export STRIPE_SECRET_KEY=sk_live_...
export STRIPE_WEBHOOK_SECRET=whsec_...

# Configure billing in config.json
{
  "billing": {
    "stripe_public_key": "pk_live_...",
    "stripe_secret_key": "sk_live_...",
    "webhook_secret": "whsec_...",
    "currency": "usd",
    "free_tier_limit": 1000,
    "individual_tier_price": 999,
    "professional_tier_price": 4999,
    "enterprise_tier_price": 19999
  }
}
```

## Monitoring and Analytics

### Performance Metrics

- Model inference latency
- Token generation rate
- Memory usage
- GPU utilization
- API response times

### Business Metrics

- Monthly Recurring Revenue (MRR)
- Customer Acquisition Cost (CAC)
- Churn rate
- Usage patterns
- Feature adoption

### Logging and Monitoring

```bash
# Enable monitoring
export PROMETHEUS_ENABLED=true
export SENTRY_DSN=your_sentry_dsn

# View metrics
curl http://localhost:9090/metrics
```

## Troubleshooting

### Common Issues

1. **Out of Memory During Training**
   ```bash
   # Reduce batch size and sequence length
   python main.py train --data-dir ./data --max-length 256 --chunk-size 500
   ```

2. **Model Loading Errors**
   ```bash
   # Check model path and permissions
   python main.py infer --model-path ./models/my_model --prompt "test"
   ```

3. **Slow Inference**
   ```bash
   # Use GPU if available
   export INFERENCE_DEVICE=cuda
   
   # Reduce max tokens
   python main.py infer --model-path ./models/my_model --max-tokens 128
   ```

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run with verbose output
python main.py train --data-dir ./data --output-dir ./models --experiment-name debug_run
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Support

- Documentation: [Link to docs]
- Issues: [Link to issue tracker]
- Community: [Link to community forum]
- Email: support@example.com

## Roadmap

### Version 1.1
- [ ] Web-based training interface
- [ ] Advanced model evaluation metrics
- [ ] Multi-language support
- [ ] Enhanced security features

### Version 1.2
- [ ] Federated learning support
- [ ] Advanced billing features
- [ ] Mobile app integration
- [ ] Enterprise SSO

### Version 2.0
- [ ] Multi-modal support (text + images)
- [ ] Advanced reasoning capabilities
- [ ] Automated model optimization
- [ ] Global deployment infrastructure

