#!/usr/bin/env python
# Special setup script for Google Colab
import os
import sys
import subprocess
import platform

def check_colab():
    """Check if we're running in Google Colab."""
    try:
        import google.colab
        return True
    except ImportError:
        return False

def setup_colab():
    """Set up the environment for Google Colab."""
    print("Text-To-Video-AI Colab Setup")
    print("==================================================")
    print(f"Python version: {platform.python_version()}")
    print("==================================================")
    
    # Check if we're actually in Colab
    if not check_colab():
        print("This script is designed to run in Google Colab.")
        print("If you're not in Colab, please use setup.py instead.")
        return
    
    # Install dependencies
    dependencies = [
        "edge-tts",
        "whisper-timestamped",
        "torch",
        "numpy",
        "moviepy",
        "requests"
    ]
    
    for package in dependencies:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"Installed {package}")
        except Exception as e:
            print(f"Error installing {package}: {e}")
    
    # Set up environment variables for audio
    try:
        runtime_dir = '/tmp/runtime-dir'
        os.environ['XDG_RUNTIME_DIR'] = runtime_dir
        os.makedirs(runtime_dir, mode=0o700, exist_ok=True)
    except Exception as e:
        print(f"Warning: Could not set up environment directories: {e}")
    
    # Reminder about Pexels API key
    print("\nREMINDER: Set your Pexels API key in your environment:")
    print("import os")
    print("os.environ['PEXELS_KEY'] = 'your-pexels-api-key-here'")
    
    print("\nSetup completed. You can now run the Text-To-Video-AI application.")

if __name__ == "__main__":
    setup_colab() 