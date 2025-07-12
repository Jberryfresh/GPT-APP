"""
API Testing Script
=================

Test script for the Custom GPT API endpoints.
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:5000/api/v1"

def test_health_check():
    """Test health check endpoints."""
    print("Testing health check...")
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health check: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    
    response = requests.get(f"{BASE_URL}/health/detailed")
    print(f"Detailed health: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Status: {data['status']}")
        print(f"Models loaded: {data['models']['loaded_count']}")

def test_models_endpoint():
    """Test model management endpoints."""
    print("\nTesting models endpoint...")
    
    response = requests.get(f"{BASE_URL}/models")
    print(f"List models: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_simple_chat():
    """Test simple chat endpoint."""
    print("\nTesting simple chat...")
    
    # This will fail if no models are loaded, but shows the API structure
    data = {
        "message": "Hello, how are you?",
        "max_tokens": 50,
        "temperature": 0.7
    }
    
    response = requests.post(f"{BASE_URL}/chat/simple", json=data)
    print(f"Simple chat: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_chat_completions():
    """Test OpenAI-compatible chat completions."""
    print("\nTesting chat completions...")
    
    data = {
        "model": "default",
        "messages": [
            {"role": "user", "content": "What is artificial intelligence?"}
        ],
        "max_tokens": 100,
        "temperature": 0.7,
        "stream": False
    }
    
    response = requests.post(f"{BASE_URL}/chat/completions", json=data)
    print(f"Chat completions: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_training_validation():
    """Test training data validation."""
    print("\nTesting training data validation...")
    
    # Create a test file
    test_file = "/tmp/test_training.txt"
    with open(test_file, "w") as f:
        f.write("This is test training data for the custom GPT system.")
    
    data = {
        "data_files": [test_file, "/nonexistent/file.txt"]
    }
    
    response = requests.post(f"{BASE_URL}/training/validate-data", json=data)
    print(f"Training validation: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def main():
    """Run all tests."""
    print("Custom GPT API Test Suite")
    print("=" * 40)
    
    try:
        test_health_check()
        test_models_endpoint()
        test_simple_chat()
        test_chat_completions()
        test_training_validation()
        
        print("\n" + "=" * 40)
        print("Test suite completed!")
        print("Note: Some tests may fail if no models are loaded.")
        print("To load a model, use the /api/v1/models/load endpoint.")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to API server.")
        print("Make sure the server is running on http://localhost:5000")
    except Exception as e:
        print(f"Error running tests: {e}")

if __name__ == "__main__":
    main()

