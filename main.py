#!/usr/bin/env python3
import os
import subprocess
import sys
import time
from threading import Thread

def build_frontend():
    """Build the React frontend"""
    print("Building React frontend...")
    try:
        # Change to frontend directory and install dependencies
        os.chdir('frontend')

        # Install npm dependencies
        subprocess.run(['npm', 'install'], check=True)

        # Build the frontend
        subprocess.run(['npm', 'run', 'build'], check=True)

        print("Frontend build completed successfully!")

    except subprocess.CalledProcessError as e:
        print(f"Error building frontend: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False
    finally:
        # Change back to root directory
        os.chdir('..')

    return True

def start_backend():
    """Start the backend server"""
    print("Starting backend server...")
    try:
        os.chdir('backend')
        subprocess.run([sys.executable, 'simple_app.py'], check=True)
    except Exception as e:
        print(f"Error starting backend: {e}")
    finally:
        os.chdir('..')

def main():
    print("🚀 Starting Custom GPT System...")

    # Build frontend first
    if not build_frontend():
        print("❌ Frontend build failed. Exiting...")
        sys.exit(1)

    # Start backend in a separate thread
    backend_thread = Thread(target=start_backend, daemon=True)
    backend_thread.start()

    print("✅ System started successfully!")
    print("🌐 Frontend: Built and ready to serve")
    print("🔧 Backend: Running on http://0.0.0.0:5000")
    print("📱 Access your app at the provided URL")

    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")

if __name__ == "__main__":
    import subprocess
    import sys
    import os

    # Run the backend server
    print("Starting Custom GPT System...")
    print("Backend server will be available on port 5000")
    print("Check the webview to see your application.")

    try:
        # Run the backend server directly
        subprocess.run([sys.executable, "backend/simple_app.py"])
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0)