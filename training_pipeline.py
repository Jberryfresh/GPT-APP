"""
Custom GPT System - Data Processing and Training Pipeline
=========================================================

This module provides the core functionality for processing training data
and fine-tuning language models using Parameter-Efficient Fine-Tuning (PEFT)
techniques like LoRA and QLoRA.

Author: Manus AI
Date: June 16, 2025
"""

import os
import json
import logging
import pandas as pd
import torch
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    TrainingArguments, 
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, TaskType
from datasets import Dataset
import re
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DataProcessingConfig:
    """Configuration for data processing pipeline."""
    max_length: int = 512
    min_length: int = 10
    overlap_ratio: float = 0.1
    chunk_size: int = 1000
    validation_split: float = 0.1
    remove_duplicates: bool = True
    language_filter: Optional[str] = "en"

@dataclass
class LoRAConfig:
    """Configuration for LoRA fine-tuning."""
    r: int = 16  # Rank of adaptation
    lora_alpha: int = 32  # LoRA scaling parameter
    target_modules: List[str] = None  # Target modules for LoRA
    lora_dropout: float = 0.1  # LoRA dropout
    bias: str = "none"  # Bias type
    task_type: str = "CAUSAL_LM"  # Task type

class DataProcessor:
    """Handles data ingestion, cleaning, and preprocessing for model training."""
    
    def __init__(self, config: DataProcessingConfig):
        self.config = config
        self.processed_data = []
        
    def load_text_files(self, file_paths: List[str]) -> List[str]:
        """Load text content from multiple files."""
        texts = []
        for file_path in file_paths:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    texts.append(content)
                logger.info(f"Loaded {len(content)} characters from {file_path}")
            except Exception as e:
                logger.error(f"Error loading {file_path}: {e}")
        return texts
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but preserve punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}\"\']+', '', text)
        
        # Normalize quotes
        text = re.sub(r'["""]', '"', text)
        text = re.sub(r'[''']', "'", text)
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        return text.strip()
    
    def chunk_text(self, text: str, chunk_size: int = None) -> List[str]:
        """Split text into overlapping chunks for training."""
        if chunk_size is None:
            chunk_size = self.config.chunk_size
            
        words = text.split()
        chunks = []
        overlap_size = int(chunk_size * self.config.overlap_ratio)
        
        for i in range(0, len(words), chunk_size - overlap_size):
            chunk = ' '.join(words[i:i + chunk_size])
            if len(chunk.split()) >= self.config.min_length:
                chunks.append(chunk)
                
        return chunks
    
    def remove_duplicates(self, texts: List[str]) -> List[str]:
        """Remove duplicate or near-duplicate content."""
        if not self.config.remove_duplicates:
            return texts
            
        unique_texts = []
        seen_hashes = set()
        
        for text in texts:
            # Simple hash-based deduplication
            text_hash = hash(text.lower().replace(' ', ''))
            if text_hash not in seen_hashes:
                seen_hashes.add(text_hash)
                unique_texts.append(text)
                
        logger.info(f"Removed {len(texts) - len(unique_texts)} duplicate texts")
        return unique_texts
    
    def create_training_examples(self, texts: List[str]) -> List[Dict[str, str]]:
        """Create training examples in instruction-following format."""
        examples = []
        
        for text in texts:
            # Create question-answer pairs from text chunks
            chunks = self.chunk_text(text)
            
            for i, chunk in enumerate(chunks):
                # Simple approach: use first sentence as context, rest as completion
                sentences = chunk.split('. ')
                if len(sentences) >= 2:
                    context = sentences[0] + '.'
                    completion = '. '.join(sentences[1:])
                    
                    example = {
                        "instruction": f"Continue the following text: {context}",
                        "input": "",
                        "output": completion
                    }
                    examples.append(example)
                    
        return examples
    
    def process_data(self, file_paths: List[str]) -> Tuple[Dataset, Dataset]:
        """Complete data processing pipeline."""
        logger.info("Starting data processing pipeline...")
        
        # Load raw texts
        raw_texts = self.load_text_files(file_paths)
        
        # Clean texts
        cleaned_texts = [self.clean_text(text) for text in raw_texts]
        
        # Remove duplicates
        unique_texts = self.remove_duplicates(cleaned_texts)
        
        # Create training examples
        examples = self.create_training_examples(unique_texts)
        
        # Split into train/validation
        split_idx = int(len(examples) * (1 - self.config.validation_split))
        train_examples = examples[:split_idx]
        val_examples = examples[split_idx:]
        
        # Convert to datasets
        train_dataset = Dataset.from_list(train_examples)
        val_dataset = Dataset.from_list(val_examples)
        
        logger.info(f"Created {len(train_examples)} training examples and {len(val_examples)} validation examples")
        
        return train_dataset, val_dataset

class ModelTrainer:
    """Handles model loading, LoRA configuration, and fine-tuning."""
    
    def __init__(self, model_name: str, lora_config: LoRAConfig):
        self.model_name = model_name
        self.lora_config = lora_config
        self.tokenizer = None
        self.model = None
        self.peft_model = None
        
    def load_model_and_tokenizer(self):
        """Load the base model and tokenizer."""
        logger.info(f"Loading model and tokenizer: {self.model_name}")
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            
        # Load model
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto" if torch.cuda.is_available() else None,
            trust_remote_code=True
        )
        
        logger.info("Model and tokenizer loaded successfully")
        
    def setup_lora(self):
        """Configure and apply LoRA to the model."""
        logger.info("Setting up LoRA configuration...")
        
        # Default target modules for common architectures
        if self.lora_config.target_modules is None:
            if "llama" in self.model_name.lower():
                self.lora_config.target_modules = ["q_proj", "v_proj", "k_proj", "o_proj"]
            else:
                self.lora_config.target_modules = ["q_proj", "v_proj"]
        
        # Create LoRA configuration
        peft_config = LoraConfig(
            r=self.lora_config.r,
            lora_alpha=self.lora_config.lora_alpha,
            target_modules=self.lora_config.target_modules,
            lora_dropout=self.lora_config.lora_dropout,
            bias=self.lora_config.bias,
            task_type=TaskType.CAUSAL_LM
        )
        
        # Apply LoRA to model
        self.peft_model = get_peft_model(self.model, peft_config)
        self.peft_model.print_trainable_parameters()
        
        logger.info("LoRA configuration applied successfully")
        
    def tokenize_dataset(self, dataset: Dataset) -> Dataset:
        """Tokenize dataset for training."""
        def tokenize_function(examples):
            # Format as instruction-following
            texts = []
            for instruction, input_text, output in zip(
                examples["instruction"], examples["input"], examples["output"]
            ):
                if input_text:
                    text = f"### Instruction:\n{instruction}\n\n### Input:\n{input_text}\n\n### Response:\n{output}"
                else:
                    text = f"### Instruction:\n{instruction}\n\n### Response:\n{output}"
                texts.append(text)
            
            # Tokenize
            tokenized = self.tokenizer(
                texts,
                truncation=True,
                padding=False,
                max_length=512,
                return_tensors=None
            )
            
            # Set labels for language modeling
            tokenized["labels"] = tokenized["input_ids"].copy()
            
            return tokenized
        
        return dataset.map(tokenize_function, batched=True, remove_columns=dataset.column_names)
    
    def train(self, train_dataset: Dataset, val_dataset: Dataset, output_dir: str):
        """Train the model using the prepared datasets."""
        logger.info("Starting model training...")
        
        # Tokenize datasets
        train_tokenized = self.tokenize_dataset(train_dataset)
        val_tokenized = self.tokenize_dataset(val_dataset)
        
        # Data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False
        )
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=3,
            per_device_train_batch_size=4,
            per_device_eval_batch_size=4,
            gradient_accumulation_steps=4,
            warmup_steps=100,
            learning_rate=2e-4,
            fp16=torch.cuda.is_available(),
            logging_steps=10,
            evaluation_strategy="steps",
            eval_steps=100,
            save_steps=500,
            save_total_limit=3,
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            greater_is_better=False,
            report_to=None,  # Disable wandb/tensorboard
            dataloader_pin_memory=False,
        )
        
        # Create trainer
        trainer = Trainer(
            model=self.peft_model,
            args=training_args,
            train_dataset=train_tokenized,
            eval_dataset=val_tokenized,
            data_collator=data_collator,
            tokenizer=self.tokenizer,
        )
        
        # Train the model
        trainer.train()
        
        # Save the final model
        trainer.save_model()
        self.tokenizer.save_pretrained(output_dir)
        
        logger.info(f"Training completed. Model saved to {output_dir}")
        
        return trainer

class TrainingPipeline:
    """Main pipeline orchestrator for the entire training process."""
    
    def __init__(self, 
                 model_name: str = "microsoft/DialoGPT-medium",
                 data_config: DataProcessingConfig = None,
                 lora_config: LoRAConfig = None):
        self.model_name = model_name
        self.data_config = data_config or DataProcessingConfig()
        self.lora_config = lora_config or LoRAConfig()
        
        self.data_processor = DataProcessor(self.data_config)
        self.model_trainer = ModelTrainer(self.model_name, self.lora_config)
        
    def run_training(self, 
                    data_files: List[str], 
                    output_dir: str,
                    experiment_name: str = None) -> Dict[str, Any]:
        """Run the complete training pipeline."""
        if experiment_name is None:
            experiment_name = f"training_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
        logger.info(f"Starting training pipeline: {experiment_name}")
        
        # Create output directory
        output_path = Path(output_dir) / experiment_name
        output_path.mkdir(parents=True, exist_ok=True)
        
        try:
            # Process data
            train_dataset, val_dataset = self.data_processor.process_data(data_files)
            
            # Load model and setup LoRA
            self.model_trainer.load_model_and_tokenizer()
            self.model_trainer.setup_lora()
            
            # Train model
            trainer = self.model_trainer.train(
                train_dataset, 
                val_dataset, 
                str(output_path)
            )
            
            # Save training metadata
            metadata = {
                "experiment_name": experiment_name,
                "model_name": self.model_name,
                "data_files": data_files,
                "train_samples": len(train_dataset),
                "val_samples": len(val_dataset),
                "data_config": self.data_config.__dict__,
                "lora_config": self.lora_config.__dict__,
                "output_dir": str(output_path),
                "timestamp": datetime.now().isoformat()
            }
            
            with open(output_path / "training_metadata.json", "w") as f:
                json.dump(metadata, f, indent=2)
                
            logger.info(f"Training pipeline completed successfully: {experiment_name}")
            
            return {
                "success": True,
                "experiment_name": experiment_name,
                "output_dir": str(output_path),
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"Training pipeline failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "experiment_name": experiment_name
            }

# Example usage and testing functions
def create_sample_data(output_dir: str = "/tmp/sample_data"):
    """Create sample training data for testing."""
    os.makedirs(output_dir, exist_ok=True)
    
    sample_texts = [
        """
        Artificial Intelligence (AI) is a branch of computer science that aims to create 
        intelligent machines that work and react like humans. AI systems can perform tasks 
        that typically require human intelligence, such as visual perception, speech 
        recognition, decision-making, and language translation.
        
        Machine learning is a subset of AI that provides systems the ability to automatically 
        learn and improve from experience without being explicitly programmed. Deep learning 
        is a subset of machine learning that uses neural networks with multiple layers to 
        model and understand complex patterns in data.
        """,
        """
        Natural Language Processing (NLP) is a field of AI that focuses on the interaction 
        between computers and humans through natural language. The ultimate objective of NLP 
        is to read, decipher, understand, and make sense of human languages in a manner that 
        is valuable.
        
        Large Language Models (LLMs) like GPT-3 and GPT-4 have revolutionized NLP by 
        demonstrating remarkable capabilities in text generation, comprehension, and reasoning. 
        These models are trained on vast amounts of text data and can perform a wide variety 
        of language tasks.
        """,
        """
        Fine-tuning is a technique used to adapt pre-trained models to specific tasks or 
        domains. Instead of training a model from scratch, fine-tuning starts with a model 
        that has already been trained on a large dataset and then continues training on a 
        smaller, task-specific dataset.
        
        Parameter-Efficient Fine-Tuning (PEFT) methods like LoRA (Low-Rank Adaptation) 
        allow for efficient fine-tuning by only training a small number of additional 
        parameters while keeping the original model weights frozen. This approach 
        significantly reduces computational requirements and training time.
        """
    ]
    
    for i, text in enumerate(sample_texts):
        with open(f"{output_dir}/sample_{i+1}.txt", "w") as f:
            f.write(text)
    
    return [f"{output_dir}/sample_{i+1}.txt" for i in range(len(sample_texts))]

if __name__ == "__main__":
    # Example usage
    print("Custom GPT Training Pipeline")
    print("=" * 40)
    
    # Create sample data
    sample_files = create_sample_data()
    print(f"Created sample data files: {sample_files}")
    
    # Configure pipeline
    data_config = DataProcessingConfig(
        max_length=256,
        chunk_size=500,
        validation_split=0.2
    )
    
    lora_config = LoRAConfig(
        r=8,
        lora_alpha=16,
        lora_dropout=0.1
    )
    
    # Initialize pipeline
    pipeline = TrainingPipeline(
        model_name="microsoft/DialoGPT-small",  # Smaller model for testing
        data_config=data_config,
        lora_config=lora_config
    )
    
    # Note: Actual training would require GPU and significant time
    print("\nPipeline initialized successfully!")
    print("To run training, call: pipeline.run_training(sample_files, './models')")

