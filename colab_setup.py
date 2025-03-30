#!/usr/bin/env python
# Special setup script for Google Colab
import os
import sys
import subprocess
import platform

def print_header():
    print("=" * 50)
    print("Text-To-Video-AI Colab Setup")
    print("=" * 50)
    print(f"Python version: {platform.python_version()}")
    print("=" * 50)

def setup_colab():
    print("Setting up for Google Colab environment...")
    
    # Install FFmpeg for video processing
    print("\n[1/4] Installing system dependencies...")
    try:
        subprocess.check_call(["apt-get", "update", "-qq"])
        subprocess.check_call(["apt-get", "install", "-y", "-qq", "ffmpeg"])
        print("✓ Successfully installed FFmpeg.")
    except Exception as e:
        print(f"✗ Error installing FFmpeg: {str(e)}")
    
    # Fix audio-related issues
    print("\n[2/4] Setting up audio environment...")
    try:
        # Install audio packages
        subprocess.check_call(["apt-get", "install", "-y", "-qq", "alsa-base", "alsa-utils", "libasound2-dev", "portaudio19-dev"])
        
        # Create dummy ALSA config
        with open("/root/.asoundrc", "w") as f:
            f.write("""
pcm.!default {
    type null
}
ctl.!default {
    type null
}
""")
        print("✓ Successfully set up audio environment.")
    except Exception as e:
        print(f"✗ Error setting up audio: {str(e)}")
    
    # Install Python dependencies
    print("\n[3/4] Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "edge-tts", "whisper-timestamped", "moviepy"])
        print("✓ Successfully installed Python dependencies.")
    except Exception as e:
        print(f"✗ Error installing Python dependencies: {str(e)}")
    
    # Set up runtime directories
    print("\n[4/4] Setting up runtime directories...")
    runtime_dir = '/tmp/runtime-dir'
    os.environ['XDG_RUNTIME_DIR'] = runtime_dir
    try:
        os.makedirs(runtime_dir, mode=0o700, exist_ok=True)
        print(f"✓ Created runtime directory: {runtime_dir}")
    except Exception as e:
        print(f"✗ Error creating runtime directory: {str(e)}")

def main():
    print_header()
    
    # Check if running in Colab
    in_colab = 'google.colab' in sys.modules
    
    if in_colab:
        setup_colab()
        
        print("\n" + "=" * 50)
        print("Colab setup complete!")
        print("You can now run the Text-To-Video-AI with:")
        print("!python app.py --text \"Your script text here\"")
        print("=" * 50)
    else:
        print("This script is designed to run in Google Colab.")
        print("If you're not in Colab, please use setup.py instead.")

if __name__ == "__main__":
    main() 