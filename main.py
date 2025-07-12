#!/usr/bin/env python3
"""
Custom GPT System - Main CLI Interface
=====================================

This script provides a command-line interface for managing the custom GPT system,
including data ingestion, model training, and inference operations.

Author: Manus AI
Date: June 16, 2025
"""

import argparse
import sys
import os
import json
import logging
from pathlib import Path
from typing import List, Optional

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import get_config, create_example_configs
from data_ingestion import DataIngestionPipeline, IngestionConfig, create_sample_documents
from training_pipeline import TrainingPipeline, DataProcessingConfig, LoRAConfig, create_sample_data
from model_inference import ModelManager, InferenceConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_data_ingestion(args):
    """Handle data ingestion commands."""
    config = IngestionConfig(
        max_file_size=args.max_file_size * 1024 * 1024,  # Convert MB to bytes
        web_scraping_delay=args.scraping_delay
    )
    
    pipeline = DataIngestionPipeline(config)
    
    if args.files:
        logger.info(f"Ingesting {len(args.files)} files...")
        results = pipeline.ingest_files(args.files)
        logger.info(f"Successfully ingested {len(results)} files")
    
    if args.urls:
        logger.info(f"Scraping {len(args.urls)} URLs...")
        results = pipeline.ingest_urls(args.urls)
        logger.info(f"Successfully scraped {len(results)} URLs")
    
    if args.directory:
        logger.info(f"Ingesting directory: {args.directory}")
        results = pipeline.ingest_directory(args.directory, recursive=args.recursive)
        logger.info(f"Successfully ingested {len(results)} files from directory")
    
    # Save results
    if args.output:
        pipeline.save_ingested_data(args.output)
        logger.info(f"Saved ingestion results to {args.output}")
    
    # Show statistics
    stats = pipeline.get_statistics()
    print("\nIngestion Statistics:")
    print(f"Total items: {stats['total_items']}")
    print(f"Total content length: {stats['total_content_length']:,} characters")
    print(f"Average content length: {stats['average_content_length']:.0f} characters")
    print(f"File types: {stats['file_type_distribution']}")

def setup_training(args):
    """Handle model training commands."""
    # Load configuration
    app_config = get_config()
    
    # Configure data processing
    data_config = DataProcessingConfig(
        max_length=args.max_length,
        chunk_size=args.chunk_size,
        validation_split=args.validation_split,
        remove_duplicates=not args.keep_duplicates
    )
    
    # Configure LoRA
    lora_config = LoRAConfig(
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout
    )
    
    # Initialize training pipeline
    pipeline = TrainingPipeline(
        model_name=args.model_name,
        data_config=data_config,
        lora_config=lora_config
    )
    
    # Prepare data files
    if args.data_files:
        data_files = args.data_files
    elif args.data_dir:
        data_dir = Path(args.data_dir)
        data_files = [str(f) for f in data_dir.glob("*.txt")]
        if not data_files:
            logger.error(f"No .txt files found in {args.data_dir}")
            return
    else:
        logger.error("Either --data-files or --data-dir must be specified")
        return
    
    logger.info(f"Training with {len(data_files)} data files")
    logger.info(f"Base model: {args.model_name}")
    logger.info(f"Output directory: {args.output_dir}")
    
    # Run training
    try:
        result = pipeline.run_training(
            data_files=data_files,
            output_dir=args.output_dir,
            experiment_name=args.experiment_name
        )
        
        if result["success"]:
            logger.info("Training completed successfully!")
            logger.info(f"Model saved to: {result['output_dir']}")
            
            # Save training summary
            summary_path = Path(result['output_dir']) / "training_summary.json"
            with open(summary_path, 'w') as f:
                json.dump(result, f, indent=2)
            
        else:
            logger.error(f"Training failed: {result['error']}")
            
    except Exception as e:
        logger.error(f"Training error: {e}")

def setup_inference(args):
    """Handle model inference commands."""
    # Initialize model manager
    manager = ModelManager()
    
    # Load model
    try:
        model_id = manager.load_model(args.model_path, args.model_id)
        logger.info(f"Loaded model: {model_id}")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        return
    
    # Configure inference
    config = InferenceConfig(
        max_new_tokens=args.max_tokens,
        temperature=args.temperature,
        top_p=args.top_p,
        top_k=args.top_k
    )
    
    if args.interactive:
        # Interactive chat mode
        print(f"Starting interactive chat with model: {model_id}")
        print("Type 'quit' to exit, 'clear' to clear conversation")
        print("-" * 50)
        
        conversation_id = "cli_session"
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if user_input.lower() == 'quit':
                    break
                elif user_input.lower() == 'clear':
                    manager.clear_conversation(conversation_id)
                    print("Conversation cleared.")
                    continue
                elif not user_input:
                    continue
                
                if args.streaming:
                    print("Assistant: ", end="", flush=True)
                    for token in manager.chat_streaming(user_input, conversation_id, model_id, config):
                        print(token, end="", flush=True)
                    print()  # New line after streaming
                else:
                    response = manager.chat(user_input, conversation_id, model_id, config)
                    print(f"Assistant: {response}")
                    
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                logger.error(f"Error during inference: {e}")
    
    elif args.prompt:
        # Single prompt mode
        try:
            if args.streaming:
                print("Response: ", end="", flush=True)
                for token in manager.chat_streaming(args.prompt, "single_prompt", model_id, config):
                    print(token, end="", flush=True)
                print()  # New line after streaming
            else:
                response = manager.chat(args.prompt, "single_prompt", model_id, config)
                print(f"Response: {response}")
        except Exception as e:
            logger.error(f"Error during inference: {e}")
    
    else:
        # Show model info
        models = manager.list_models()
        print("\nLoaded Models:")
        for model in models:
            print(f"- {model['model_id']} ({'default' if model['is_default'] else 'loaded'})")
            print(f"  Path: {model['model_path']}")
            print(f"  Type: {model['metadata']['model_type'] if model['metadata'] else 'unknown'}")
            print(f"  Parameters: {model.get('total_parameters', 'unknown'):,}")

def setup_config(args):
    """Handle configuration commands."""
    if args.create_examples:
        create_example_configs()
        print("Created example configuration files")
    
    elif args.show:
        config = get_config()
        print("Current Configuration:")
        print(json.dumps(config.to_dict(), indent=2))
    
    elif args.validate:
        config = get_config()
        errors = config.validate()
        if errors:
            print("Configuration Validation Errors:")
            for error in errors:
                print(f"  - {error}")
            sys.exit(1)
        else:
            print("Configuration is valid")

def setup_demo(args):
    """Handle demo commands."""
    if args.create_sample_data:
        # Create sample training data
        sample_files = create_sample_data(args.output_dir)
        print(f"Created sample training data in: {args.output_dir}")
        print(f"Files: {sample_files}")
    
    elif args.create_sample_docs:
        # Create sample documents for ingestion
        sample_dir = create_sample_documents(args.output_dir)
        print(f"Created sample documents in: {sample_dir}")
    
    elif args.full_demo:
        # Run a complete demo pipeline
        print("Running full demo pipeline...")
        
        # 1. Create sample data
        sample_dir = create_sample_documents(args.output_dir + "/docs")
        print(f"1. Created sample documents in: {sample_dir}")
        
        # 2. Ingest data
        pipeline = DataIngestionPipeline()
        results = pipeline.ingest_directory(sample_dir)
        pipeline.save_ingested_data(args.output_dir + "/ingested_data.json")
        print(f"2. Ingested {len(results)} documents")
        
        # 3. Create training data
        training_files = create_sample_data(args.output_dir + "/training")
        print(f"3. Created training data: {training_files}")
        
        print("\nDemo setup complete!")
        print("Next steps:")
        print(f"1. Review ingested data: {args.output_dir}/ingested_data.json")
        print(f"2. Train a model: python main.py train --data-dir {args.output_dir}/training --output-dir ./models")
        print("3. Test inference: python main.py infer --model-path ./models/[experiment_name] --interactive")

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Custom GPT System - CLI Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Data ingestion
  python main.py ingest --files doc1.txt doc2.pdf --output ingested.json
  python main.py ingest --directory ./documents --recursive --output ingested.json
  python main.py ingest --urls https://example.com/article1 https://example.com/article2
  
  # Model training
  python main.py train --data-files train1.txt train2.txt --model-name microsoft/DialoGPT-small
  python main.py train --data-dir ./training_data --output-dir ./models --experiment-name my_expert
  
  # Model inference
  python main.py infer --model-path ./models/my_expert --interactive
  python main.py infer --model-path ./models/my_expert --prompt "What is machine learning?"
  
  # Configuration
  python main.py config --create-examples
  python main.py config --show
  python main.py config --validate
  
  # Demo
  python main.py demo --full-demo --output-dir ./demo
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Data ingestion command
    ingest_parser = subparsers.add_parser('ingest', help='Ingest data from various sources')
    ingest_parser.add_argument('--files', nargs='+', help='List of files to ingest')
    ingest_parser.add_argument('--urls', nargs='+', help='List of URLs to scrape')
    ingest_parser.add_argument('--directory', help='Directory to ingest (all supported files)')
    ingest_parser.add_argument('--recursive', action='store_true', help='Recursively search directory')
    ingest_parser.add_argument('--output', help='Output file for ingested data (JSON)')
    ingest_parser.add_argument('--max-file-size', type=int, default=100, help='Max file size in MB')
    ingest_parser.add_argument('--scraping-delay', type=float, default=1.0, help='Delay between web requests')
    
    # Training command
    train_parser = subparsers.add_parser('train', help='Train a custom model')
    train_parser.add_argument('--data-files', nargs='+', help='Training data files')
    train_parser.add_argument('--data-dir', help='Directory containing training data')
    train_parser.add_argument('--model-name', default='microsoft/DialoGPT-small', help='Base model name')
    train_parser.add_argument('--output-dir', default='./models', help='Output directory for trained model')
    train_parser.add_argument('--experiment-name', help='Name for this training experiment')
    train_parser.add_argument('--max-length', type=int, default=512, help='Maximum sequence length')
    train_parser.add_argument('--chunk-size', type=int, default=1000, help='Text chunk size for processing')
    train_parser.add_argument('--validation-split', type=float, default=0.1, help='Validation data split ratio')
    train_parser.add_argument('--keep-duplicates', action='store_true', help='Keep duplicate content')
    train_parser.add_argument('--lora-r', type=int, default=16, help='LoRA rank parameter')
    train_parser.add_argument('--lora-alpha', type=int, default=32, help='LoRA alpha parameter')
    train_parser.add_argument('--lora-dropout', type=float, default=0.1, help='LoRA dropout rate')
    
    # Inference command
    infer_parser = subparsers.add_parser('infer', help='Run model inference')
    infer_parser.add_argument('--model-path', required=True, help='Path to trained model')
    infer_parser.add_argument('--model-id', help='Model ID (defaults to directory name)')
    infer_parser.add_argument('--interactive', action='store_true', help='Start interactive chat session')
    infer_parser.add_argument('--prompt', help='Single prompt for inference')
    infer_parser.add_argument('--streaming', action='store_true', help='Enable streaming responses')
    infer_parser.add_argument('--max-tokens', type=int, default=256, help='Maximum tokens to generate')
    infer_parser.add_argument('--temperature', type=float, default=0.7, help='Sampling temperature')
    infer_parser.add_argument('--top-p', type=float, default=0.9, help='Top-p sampling parameter')
    infer_parser.add_argument('--top-k', type=int, default=50, help='Top-k sampling parameter')
    
    # Configuration command
    config_parser = subparsers.add_parser('config', help='Manage configuration')
    config_parser.add_argument('--create-examples', action='store_true', help='Create example config files')
    config_parser.add_argument('--show', action='store_true', help='Show current configuration')
    config_parser.add_argument('--validate', action='store_true', help='Validate configuration')
    
    # Demo command
    demo_parser = subparsers.add_parser('demo', help='Demo and testing utilities')
    demo_parser.add_argument('--create-sample-data', action='store_true', help='Create sample training data')
    demo_parser.add_argument('--create-sample-docs', action='store_true', help='Create sample documents')
    demo_parser.add_argument('--full-demo', action='store_true', help='Run complete demo pipeline')
    demo_parser.add_argument('--output-dir', default='./demo_output', help='Output directory for demo files')
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'ingest':
            setup_data_ingestion(args)
        elif args.command == 'train':
            setup_training(args)
        elif args.command == 'infer':
            setup_inference(args)
        elif args.command == 'config':
            setup_config(args)
        elif args.command == 'demo':
            setup_demo(args)
        else:
            parser.print_help()
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

