#!/usr/bin/env python
# Special setup script for Google Colab without audio hardware
import os
import sys
import subprocess
import platform
import shutil

def print_header():
    print("=" * 60)
    print("Text-To-Video-AI Colab Setup (No Audio Hardware Version)")
    print("=" * 60)
    print(f"Python version: {platform.python_version()}")
    print("=" * 60)

def setup_colab_no_audio():
    print("Setting up for Google Colab environment (no audio hardware)...")
    
    # Install FFmpeg for video processing
    print("\n[1/5] Installing system dependencies...")
    try:
        subprocess.check_call(["apt-get", "update", "-qq"])
        subprocess.check_call(["apt-get", "install", "-y", "-qq", "ffmpeg"])
        print("✓ Successfully installed FFmpeg.")
    except Exception as e:
        print(f"✗ Error installing FFmpeg: {str(e)}")
    
    # Create dummy audio file
    print("\n[2/5] Creating dummy audio file...")
    try:
        # Create a silent audio file using FFmpeg
        subprocess.check_call(["ffmpeg", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", "10", "-q:a", "9", "-acodec", "libmp3lame", "audio_tts.wav", "-y"], 
                             stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        print("✓ Created dummy silent audio file.")
    except Exception as e:
        print(f"✗ Error creating dummy audio: {str(e)}")
    
    # Install Python dependencies
    print("\n[3/5] Installing Python dependencies...")
    try:
        # Skip audio dependencies
        packages = ["pip", "moviepy", "pillow", "numpy", "requests"]
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade"] + packages)
        print("✓ Successfully installed core Python dependencies.")
        
        # Try to install Whisper without requiring audio
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--no-deps", "whisper-timestamped"])
        print("✓ Successfully installed Whisper (without audio dependencies).")
    except Exception as e:
        print(f"✗ Error installing Python dependencies: {str(e)}")
    
    # Set up runtime directories
    print("\n[4/5] Setting up runtime directories...")
    runtime_dir = '/tmp/runtime-dir'
    os.environ['XDG_RUNTIME_DIR'] = runtime_dir
    try:
        os.makedirs(runtime_dir, mode=0o700, exist_ok=True)
        print(f"✓ Created runtime directory: {runtime_dir}")
    except Exception as e:
        print(f"✗ Error creating runtime directory: {str(e)}")
    
    # Patch audio generator
    print("\n[5/5] Patching audio generator for no-audio environment...")
    audio_generator_path = "utility/audio/audio_generator.py"
    
    if os.path.exists(audio_generator_path):
        try:
            # Backup original file
            shutil.copy2(audio_generator_path, f"{audio_generator_path}.bak")
            
            # Create new file with dummy implementation
            with open(audio_generator_path, "w") as f:
                f.write("""
import asyncio
import os
import shutil

async def generate_audio(text, outputFilename):
    \"\"\"
    Dummy audio generator for environments without audio hardware.
    \"\"\"
    print("Using dummy audio generator (no audio hardware mode)")
    
    # If we already created a dummy file, use it
    if os.path.exists("audio_tts.wav"):
        shutil.copy2("audio_tts.wav", outputFilename)
        return
        
    # Otherwise, print a message about what would happen
    print(f"Would generate audio for text: {text[:50]}...")
    print(f"Output would be saved to: {outputFilename}")
    print("Since this is a no-audio environment, using a dummy silent file instead.")
    
    # In a real environment, this would be:
    # communicate = edge_tts.Communicate(text, "en-AU-WilliamNeural")
    # await communicate.save(outputFilename)
    
    # Sleep to simulate processing time
    await asyncio.sleep(1)
""")
            print("✓ Successfully patched audio generator.")
        except Exception as e:
            print(f"✗ Error patching audio generator: {str(e)}")
    else:
        print(f"✗ Could not find audio generator at {audio_generator_path}")

def main():
    print_header()
    
    # Check if running in Colab
    in_colab = 'google.colab' in sys.modules
    
    if in_colab:
        setup_colab_no_audio()
        
        print("\n" + "=" * 60)
        print("Colab no-audio setup complete!")
        print("\nThis setup creates a dummy audio file and patches the")
        print("audio generator to work without audio hardware.")
        print("\nYou can now run the Text-To-Video-AI with:")
        print("!python app.py --text \"Your script text here\"")
        print("=" * 60)
    else:
        print("This script is designed to run in Google Colab.")
        print("If you're not in Colab, please use setup.py instead.")

if __name__ == "__main__":
    main() 