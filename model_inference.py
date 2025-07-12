"""
Model Management and Inference Module
====================================

This module handles model loading, inference, and management for the custom GPT system.
Supports both fine-tuned models and base models with efficient inference capabilities.

Author: Manus AI
Date: June 16, 2025
"""

import os
import json
import torch
import logging
from typing import Dict, List, Any, Optional, Union, Generator
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime
import time
import threading
from queue import Queue, Empty
import hashlib

from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    GenerationConfig,
    TextStreamer
)
from peft import PeftModel, PeftConfig

logger = logging.getLogger(__name__)

@dataclass
class InferenceConfig:
    """Configuration for model inference."""
    max_length: int = 512
    max_new_tokens: int = 256
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 50
    repetition_penalty: float = 1.1
    do_sample: bool = True
    num_beams: int = 1
    early_stopping: bool = True
    pad_token_id: Optional[int] = None
    eos_token_id: Optional[int] = None
    use_cache: bool = True

@dataclass
class ModelMetadata:
    """Metadata for a loaded model."""
    model_id: str
    model_name: str
    model_type: str  # 'base' or 'fine_tuned'
    base_model: Optional[str] = None
    training_data: Optional[str] = None
    created_at: str = None
    model_size: Optional[int] = None
    capabilities: List[str] = None
    performance_metrics: Dict[str, float] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.capabilities is None:
            self.capabilities = []
        if self.performance_metrics is None:
            self.performance_metrics = {}

class ModelInferenceError(Exception):
    """Custom exception for model inference errors."""
    pass

class ConversationManager:
    """Manages conversation context and history."""
    
    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self.conversations: Dict[str, List[Dict[str, str]]] = {}
    
    def create_conversation(self, conversation_id: str) -> str:
        """Create a new conversation."""
        self.conversations[conversation_id] = []
        return conversation_id
    
    def add_message(self, conversation_id: str, role: str, content: str):
        """Add a message to the conversation."""
        if conversation_id not in self.conversations:
            self.create_conversation(conversation_id)
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
        self.conversations[conversation_id].append(message)
        
        # Trim history if needed
        if len(self.conversations[conversation_id]) > self.max_history * 2:
            # Keep the most recent messages
            self.conversations[conversation_id] = self.conversations[conversation_id][-self.max_history * 2:]
    
    def get_conversation_context(self, conversation_id: str) -> str:
        """Get formatted conversation context."""
        if conversation_id not in self.conversations:
            return ""
        
        context_parts = []
        for message in self.conversations[conversation_id]:
            role = message["role"]
            content = message["content"]
            context_parts.append(f"{role.title()}: {content}")
        
        return "\n".join(context_parts)
    
    def clear_conversation(self, conversation_id: str):
        """Clear a conversation."""
        if conversation_id in self.conversations:
            self.conversations[conversation_id] = []

class ModelInference:
    """Handles model loading and inference operations."""
    
    def __init__(self, model_path: str, device: str = "auto"):
        self.model_path = Path(model_path)
        self.device = device
        self.model = None
        self.tokenizer = None
        self.metadata = None
        self.is_peft_model = False
        self.generation_config = None
        
        self._load_model()
    
    def _detect_device(self) -> str:
        """Detect the best available device."""
        if self.device == "auto":
            if torch.cuda.is_available():
                return "cuda"
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                return "mps"
            else:
                return "cpu"
        return self.device
    
    def _load_metadata(self):
        """Load model metadata if available."""
        metadata_path = self.model_path / "training_metadata.json"
        if metadata_path.exists():
            with open(metadata_path, 'r') as f:
                data = json.load(f)
                self.metadata = ModelMetadata(**data)
        else:
            # Create basic metadata
            self.metadata = ModelMetadata(
                model_id=hashlib.md5(str(self.model_path).encode()).hexdigest()[:8],
                model_name=self.model_path.name,
                model_type="unknown"
            )
    
    def _load_model(self):
        """Load the model and tokenizer."""
        logger.info(f"Loading model from {self.model_path}")
        
        try:
            # Load metadata
            self._load_metadata()
            
            # Check if it's a PEFT model
            peft_config_path = self.model_path / "adapter_config.json"
            if peft_config_path.exists():
                self.is_peft_model = True
                logger.info("Detected PEFT model")
                
                # Load PEFT config to get base model
                peft_config = PeftConfig.from_pretrained(str(self.model_path))
                base_model_name = peft_config.base_model_name_or_path
                
                # Load base model and tokenizer
                self.tokenizer = AutoTokenizer.from_pretrained(base_model_name)
                base_model = AutoModelForCausalLM.from_pretrained(
                    base_model_name,
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                    device_map=self._detect_device() if torch.cuda.is_available() else None,
                    trust_remote_code=True
                )
                
                # Load PEFT model
                self.model = PeftModel.from_pretrained(base_model, str(self.model_path))
                
            else:
                # Load regular model
                self.tokenizer = AutoTokenizer.from_pretrained(str(self.model_path))
                self.model = AutoModelForCausalLM.from_pretrained(
                    str(self.model_path),
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                    device_map=self._detect_device() if torch.cuda.is_available() else None,
                    trust_remote_code=True
                )
            
            # Set up tokenizer
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Set up generation config
            self.generation_config = GenerationConfig.from_pretrained(
                str(self.model_path),
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                max_new_tokens=256
            )
            
            logger.info("Model loaded successfully")
            
        except Exception as e:
            raise ModelInferenceError(f"Failed to load model: {e}")
    
    def generate_response(self, 
                         prompt: str, 
                         config: InferenceConfig = None,
                         conversation_context: str = None) -> str:
        """Generate a response to a prompt."""
        if config is None:
            config = InferenceConfig()
        
        try:
            # Prepare input
            if conversation_context:
                full_prompt = f"{conversation_context}\nUser: {prompt}\nAssistant:"
            else:
                full_prompt = f"User: {prompt}\nAssistant:"
            
            # Tokenize input
            inputs = self.tokenizer(
                full_prompt,
                return_tensors="pt",
                truncation=True,
                max_length=config.max_length - config.max_new_tokens,
                padding=True
            )
            
            # Move to device
            if torch.cuda.is_available():
                inputs = {k: v.cuda() for k, v in inputs.items()}
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=config.max_new_tokens,
                    temperature=config.temperature,
                    top_p=config.top_p,
                    top_k=config.top_k,
                    repetition_penalty=config.repetition_penalty,
                    do_sample=config.do_sample,
                    num_beams=config.num_beams,
                    early_stopping=config.early_stopping,
                    pad_token_id=config.pad_token_id or self.tokenizer.pad_token_id,
                    eos_token_id=config.eos_token_id or self.tokenizer.eos_token_id,
                    use_cache=config.use_cache
                )
            
            # Decode response
            response = self.tokenizer.decode(
                outputs[0][inputs['input_ids'].shape[1]:],
                skip_special_tokens=True
            ).strip()
            
            return response
            
        except Exception as e:
            raise ModelInferenceError(f"Failed to generate response: {e}")
    
    def generate_streaming_response(self, 
                                  prompt: str, 
                                  config: InferenceConfig = None,
                                  conversation_context: str = None) -> Generator[str, None, None]:
        """Generate a streaming response to a prompt."""
        if config is None:
            config = InferenceConfig()
        
        try:
            # Prepare input
            if conversation_context:
                full_prompt = f"{conversation_context}\nUser: {prompt}\nAssistant:"
            else:
                full_prompt = f"User: {prompt}\nAssistant:"
            
            # Tokenize input
            inputs = self.tokenizer(
                full_prompt,
                return_tensors="pt",
                truncation=True,
                max_length=config.max_length - config.max_new_tokens,
                padding=True
            )
            
            # Move to device
            if torch.cuda.is_available():
                inputs = {k: v.cuda() for k, v in inputs.items()}
            
            # Create a custom streamer
            class CustomStreamer:
                def __init__(self, tokenizer):
                    self.tokenizer = tokenizer
                    self.tokens = []
                    self.queue = Queue()
                    self.finished = False
                
                def put(self, value):
                    if value.shape[-1] == 1:
                        token_id = value[0, -1].item()
                        if token_id != self.tokenizer.eos_token_id:
                            token = self.tokenizer.decode([token_id], skip_special_tokens=True)
                            self.queue.put(token)
                
                def end(self):
                    self.queue.put(None)
                    self.finished = True
                
                def __iter__(self):
                    return self
                
                def __next__(self):
                    while True:
                        try:
                            token = self.queue.get(timeout=1.0)
                            if token is None:
                                raise StopIteration
                            return token
                        except Empty:
                            if self.finished:
                                raise StopIteration
                            continue
            
            streamer = CustomStreamer(self.tokenizer)
            
            # Generate in a separate thread
            def generate():
                with torch.no_grad():
                    self.model.generate(
                        **inputs,
                        max_new_tokens=config.max_new_tokens,
                        temperature=config.temperature,
                        top_p=config.top_p,
                        top_k=config.top_k,
                        repetition_penalty=config.repetition_penalty,
                        do_sample=config.do_sample,
                        num_beams=1,  # Streaming requires num_beams=1
                        pad_token_id=config.pad_token_id or self.tokenizer.pad_token_id,
                        eos_token_id=config.eos_token_id or self.tokenizer.eos_token_id,
                        streamer=streamer
                    )
                streamer.end()
            
            # Start generation thread
            generation_thread = threading.Thread(target=generate)
            generation_thread.start()
            
            # Yield tokens as they become available
            for token in streamer:
                yield token
            
            # Wait for generation to complete
            generation_thread.join()
            
        except Exception as e:
            raise ModelInferenceError(f"Failed to generate streaming response: {e}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        info = {
            "model_path": str(self.model_path),
            "is_peft_model": self.is_peft_model,
            "device": self._detect_device(),
            "metadata": asdict(self.metadata) if self.metadata else None
        }
        
        if self.model:
            # Get model size
            param_count = sum(p.numel() for p in self.model.parameters())
            trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
            
            info.update({
                "total_parameters": param_count,
                "trainable_parameters": trainable_params,
                "model_size_mb": param_count * 4 / (1024 * 1024)  # Assuming float32
            })
        
        return info

class ModelManager:
    """Manages multiple models and provides unified inference interface."""
    
    def __init__(self):
        self.models: Dict[str, ModelInference] = {}
        self.conversation_manager = ConversationManager()
        self.default_model_id: Optional[str] = None
    
    def load_model(self, model_path: str, model_id: str = None) -> str:
        """Load a model and return its ID."""
        if model_id is None:
            model_id = Path(model_path).name
        
        if model_id in self.models:
            logger.warning(f"Model {model_id} already loaded, replacing...")
        
        try:
            model_inference = ModelInference(model_path)
            self.models[model_id] = model_inference
            
            if self.default_model_id is None:
                self.default_model_id = model_id
            
            logger.info(f"Loaded model {model_id} from {model_path}")
            return model_id
            
        except Exception as e:
            logger.error(f"Failed to load model {model_id}: {e}")
            raise
    
    def unload_model(self, model_id: str):
        """Unload a model to free memory."""
        if model_id in self.models:
            del self.models[model_id]
            if self.default_model_id == model_id:
                self.default_model_id = next(iter(self.models.keys())) if self.models else None
            logger.info(f"Unloaded model {model_id}")
    
    def list_models(self) -> List[Dict[str, Any]]:
        """List all loaded models."""
        return [
            {
                "model_id": model_id,
                "is_default": model_id == self.default_model_id,
                **model.get_model_info()
            }
            for model_id, model in self.models.items()
        ]
    
    def set_default_model(self, model_id: str):
        """Set the default model for inference."""
        if model_id not in self.models:
            raise ValueError(f"Model {model_id} not loaded")
        self.default_model_id = model_id
    
    def chat(self, 
             message: str, 
             conversation_id: str = "default",
             model_id: str = None,
             config: InferenceConfig = None) -> str:
        """Send a chat message and get a response."""
        if model_id is None:
            model_id = self.default_model_id
        
        if model_id is None or model_id not in self.models:
            raise ValueError("No model available for inference")
        
        model = self.models[model_id]
        
        # Get conversation context
        context = self.conversation_manager.get_conversation_context(conversation_id)
        
        # Generate response
        response = model.generate_response(message, config, context)
        
        # Update conversation
        self.conversation_manager.add_message(conversation_id, "user", message)
        self.conversation_manager.add_message(conversation_id, "assistant", response)
        
        return response
    
    def chat_streaming(self, 
                      message: str, 
                      conversation_id: str = "default",
                      model_id: str = None,
                      config: InferenceConfig = None) -> Generator[str, None, None]:
        """Send a chat message and get a streaming response."""
        if model_id is None:
            model_id = self.default_model_id
        
        if model_id is None or model_id not in self.models:
            raise ValueError("No model available for inference")
        
        model = self.models[model_id]
        
        # Get conversation context
        context = self.conversation_manager.get_conversation_context(conversation_id)
        
        # Generate streaming response
        full_response = ""
        for token in model.generate_streaming_response(message, config, context):
            full_response += token
            yield token
        
        # Update conversation
        self.conversation_manager.add_message(conversation_id, "user", message)
        self.conversation_manager.add_message(conversation_id, "assistant", full_response)
    
    def clear_conversation(self, conversation_id: str):
        """Clear a conversation."""
        self.conversation_manager.clear_conversation(conversation_id)

# Example usage and testing functions
def test_model_inference():
    """Test model inference with a simple example."""
    print("Model Inference Test")
    print("=" * 20)
    
    # This would require an actual model to test
    # For demonstration purposes only
    
    try:
        # Initialize model manager
        manager = ModelManager()
        
        # In a real scenario, you would load an actual model:
        # model_id = manager.load_model("/path/to/your/model")
        
        print("Model manager initialized successfully!")
        print("To use with a real model:")
        print("1. Train a model using the training pipeline")
        print("2. Load it with: manager.load_model('/path/to/model')")
        print("3. Chat with: manager.chat('Hello, how are you?')")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_model_inference()

