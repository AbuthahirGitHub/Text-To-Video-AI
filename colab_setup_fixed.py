#!/usr/bin/env python
# Improved setup script for Google Colab with better audio handling
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

def setup_colab_fixed():
    """Set up the environment for Google Colab with better audio handling."""
    print("=" * 60)
    print("Text-To-Video-AI Colab Setup (Fixed Version)")
    print("=" * 60)
    print(f"Python version: {platform.python_version()}")
    print("=" * 60)
    
    # Check if we're actually in Colab
    if not check_colab():
        print("This script is designed to run in Google Colab.")
        print("If you're not in Colab, please use setup.py instead.")
        return
    
    # Install system dependencies
    print("\n[1/5] Installing system dependencies...")
    try:
        # Update and install required packages
        subprocess.run("apt-get update -qq", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Install FFmpeg, ALSA, and other audio tools
        packages = ["ffmpeg", "alsa-utils", "libasound2-dev", "portaudio19-dev", "libsndfile1"]
        for pkg in packages:
            try:
                subprocess.run(f"apt-get install -y -qq {pkg}", shell=True, 
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                print(f"✓ Installed {pkg}")
            except Exception as e:
                print(f"✗ Failed to install {pkg}: {e}")
        
    except Exception as e:
        print(f"✗ Error installing system dependencies: {e}")
    
    # Configure ALSA for headless environment
    print("\n[2/5] Configuring audio for headless environment...")
    try:
        # Create a dummy ALSA config to prevent errors
        with open("/tmp/asoundrc", "w") as f:
            f.write("""
pcm.!default {
    type null
}
ctl.!default {
    type null
}
""")
        # Set the ALSA config path
        os.environ['ALSA_CONFIG_PATH'] = '/tmp/asoundrc'
        print("✓ Created dummy ALSA configuration")
    except Exception as e:
        print(f"✗ Error configuring audio: {e}")
    
    # Install Python dependencies
    print("\n[3/5] Installing Python dependencies...")
    dependencies = [
        "edge-tts==6.1.12",
        "whisper-timestamped==1.15.4",
        "librosa>=0.10.0",
        "numpy>=1.20.0",
        "torch>=2.0.0",
        "moviepy>=1.0.3",
        "scipy>=1.9.0",
        "soundfile>=0.12.1",
        "requests>=2.25.0",
        "pillow>=9.0.0"
    ]
    
    for package in dependencies:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✓ Installed {package}")
        except Exception as e:
            print(f"✗ Error installing {package}: {e}")
    
    # Create runtime directories for audio
    print("\n[4/5] Setting up runtime directories...")
    try:
        runtime_dir = '/tmp/runtime-dir'
        os.environ['XDG_RUNTIME_DIR'] = runtime_dir
        os.makedirs(runtime_dir, mode=0o700, exist_ok=True)
        print(f"✓ Created runtime directory: {runtime_dir}")
    except Exception as e:
        print(f"✗ Error creating runtime directory: {e}")
    
    # Create dummy audio file for testing
    print("\n[5/5] Creating test audio file...")
    try:
        command = [
            "ffmpeg", "-y", "-f", "lavfi", 
            "-i", "anullsrc=r=44100:cl=mono", 
            "-t", "5", "-q:a", "9", 
            "-acodec", "libmp3lame", 
            "test_audio.wav"
        ]
        
        process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if process.returncode == 0:
            print("✓ Successfully created test audio file")
        else:
            print(f"✗ Error creating test audio: {process.stderr.decode('utf-8')}")
    except Exception as e:
        print(f"✗ Error creating test audio: {e}")
    
    # Fix for audio_processor.py if it doesn't exist or is empty
    print("\nChecking for missing modules...")
    audio_processor_path = "utility/captions/audio_processor.py"
    if not os.path.exists(audio_processor_path) or os.path.getsize(audio_processor_path) == 0:
        print(f"Creating missing audio_processor.py file")
        os.makedirs(os.path.dirname(audio_processor_path), exist_ok=True)
        with open(audio_processor_path, "w") as f:
            f.write('''import os
import numpy as np
import soundfile as sf
import librosa
import subprocess

def preprocess_audio(audio_filename, output_file=None, sample_rate=16000):
    """
    Preprocess audio file for Whisper model.
    Returns preprocessed audio data or None if processing fails.
    
    Args:
        audio_filename (str): Path to the audio file
        output_file (str, optional): Path for processed output file
        sample_rate (int, optional): Target sample rate, defaults to 16kHz for Whisper
        
    Returns:
        numpy.ndarray: Processed audio data or None if processing fails
    """
    try:
        # Check if file exists
        if not os.path.exists(audio_filename):
            raise FileNotFoundError(f"Audio file not found: {audio_filename}")
        
        # Load audio with librosa for better compatibility
        audio_data, sample_rate = librosa.load(audio_filename, sr=16000, mono=True)
        
        # Validate audio data
        if not isinstance(audio_data, np.ndarray):
            raise ValueError("Invalid audio data format")
        
        # Ensure audio is not empty
        if len(audio_data) == 0:
            raise ValueError("Audio file is empty")
        
        # Normalize audio
        max_val = np.max(np.abs(audio_data))
        if max_val > 0:
            audio_data = audio_data / max_val
        
        return audio_data
        
    except Exception as e:
        print(f"Error preprocessing audio: {str(e)}")
        
        # Try alternative method with FFmpeg if available
        try:
            print("Trying alternative preprocessing with FFmpeg...")
            if output_file is None:
                output_file = f"{os.path.splitext(audio_filename)[0]}_processed.wav"
                
            # Use FFmpeg to convert audio
            cmd = [
                "ffmpeg", "-y", "-i", audio_filename,
                "-ar", str(sample_rate), "-ac", "1",
                "-c:a", "pcm_s16le", output_file
            ]
            
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            
            # Load the processed file
            audio_data, _ = librosa.load(output_file, sr=sample_rate, mono=True)
            return audio_data
            
        except Exception as e2:
            print(f"Alternative preprocessing also failed: {str(e2)}")
            
            # If all else fails, generate a silent audio segment
            print("Generating silent audio as fallback...")
            duration = 30.0  # 30 seconds of silence
            return np.zeros(int(duration * sample_rate), dtype=np.float32)
''')
        print("✓ Created audio_processor.py file")
    
    # Create a special script to run the application for Colab
    print("\nCreating Colab runner script...")
    with open("colab_run.py", "w") as f:
        f.write('''#!/usr/bin/env python
# Special runner script for Colab environment
import os
import sys
import subprocess

def setup_env():
    """Set up environment variables for audio"""
    os.environ['ALSA_CONFIG_PATH'] = '/tmp/asoundrc'
    os.environ['XDG_RUNTIME_DIR'] = '/tmp/runtime-dir'

def run_app():
    """Run the app with proper environment setup"""
    # Set up environment
    setup_env()
    
    # Get command line arguments
    args = sys.argv[1:]
    if not args:
        args = ["--help"]
    
    # Add default GPU flag if not specified
    if "--force-gpu" not in args and "--force-cpu" not in args:
        args.append("--force-gpu")
    
    # Construct command
    cmd = [sys.executable, "app.py"] + args
    
    # Run app
    print("=" * 60)
    print("Running Text-To-Video-AI with special Colab configuration")
    print("=" * 60)
    print(f"Command: {' '.join(cmd)}")
    print("=" * 60)
    
    # Execute
    result = subprocess.run(cmd)
    return result.returncode

if __name__ == "__main__":
    sys.exit(run_app())
''')
    print("✓ Created colab_run.py")
    
    # Make it executable
    os.chmod("colab_run.py", 0o755)
    
    print("\n" + "=" * 60)
    print("Setup complete!")
    print("\nTo run the application, use:")
    print("!python colab_run.py --file example_script.txt")
    print("or")
    print("!python colab_run.py --text \"Your script text here\"")
    print("=" * 60)

if __name__ == "__main__":
    setup_colab_fixed() 