# Text-To-Video-AI: Colab Runbook

Follow these steps exactly to run Text-To-Video-AI in Google Colab without errors.

## Step 1: Clone the repository

```python
# Remove any existing copy first
!rm -rf Text-To-Video-AI

# Clone the repository
!git clone https://github.com/AbuthahirGitHub/Text-To-Video-AI
%cd Text-To-Video-AI
```

## Step 2: Install our fixed setup script

Copy/paste this code into a cell to create the fixed setup script:

```python
%%writefile colab_setup_fixed.py
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
        packages = ["ffmpeg", "alsa-utils", "libasound2-dev", "libsndfile1"]
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
    
    # Create the missing audio_processor.py file
    print("\n[5/5] Creating audio processor module...")
    audio_processor_path = "utility/captions/audio_processor.py"
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
    
    print("\n" + "=" * 60)
    print("Setup complete!")
    print("\nTo run the application, use:")
    print("!python app.py --file test_script.txt --force-gpu")
    print("or")
    print("!python app.py --text \"Your script text here\" --force-gpu")
    print("=" * 60)

if __name__ == "__main__":
    setup_colab_fixed()
```

## Step 3: Run the fixed setup

```python
!python colab_setup_fixed.py
```

## Step 4: Fix audio generator

Create an improved audio generator with better error handling:

```python
%%writefile utility/audio/audio_generator.py
import edge_tts
import asyncio
import os
import subprocess
import sys

async def generate_audio(text, outputFilename):
    """
    Generate audio from text using edge_tts.
    Falls back to a silent audio file if text-to-speech fails.
    
    Args:
        text (str): The text to convert to speech
        outputFilename (str): Filename to save the audio to
        
    Returns:
        None
    """
    try:
        # Attempt to use edge_tts for text-to-speech
        print(f"Generating audio using edge-tts... ({len(text.split())} words)")
        communicate = edge_tts.Communicate(text, "en-AU-WilliamNeural")
        await communicate.save(outputFilename)
        print(f"Successfully generated audio with edge-tts: {outputFilename}")
    
    except Exception as e:
        print(f"Error generating audio with edge_tts: {e}")
        print("Falling back to creating a silent audio file...")
        
        try:
            # Create a silent audio file using FFmpeg
            duration = len(text.split()) * 0.3  # Estimate duration based on word count (roughly 3 words per second)
            if duration < 10:
                duration = 10  # Minimum 10 seconds
                
            cmd = [
                "ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=mono", 
                "-t", str(duration),
                "-q:a", "9", "-acodec", "libmp3lame", outputFilename
            ]
            
            # Run FFmpeg silently
            print(f"Creating silent audio file with duration: {duration:.2f} seconds")
            result = subprocess.run(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True
            )
            
            if result.returncode == 0:
                print("Successfully created silent audio file as fallback.")
            else:
                print(f"Error creating silent audio file: {result.stderr}")
                raise RuntimeError("Failed to create audio file")
        
        except Exception as fallback_error:
            print(f"Critical error in audio generation: {fallback_error}")
            
            # Ultimate fallback - create a simple WAV with numpy
            try:
                print("Attempting last-resort audio generation...")
                import numpy as np
                from scipy.io import wavfile
                
                sample_rate = 44100
                duration = len(text.split()) * 0.3
                if duration < 10:
                    duration = 10
                    
                # Generate silent audio
                samples = np.zeros(int(sample_rate * duration), dtype=np.float32)
                
                # Add a short beep at the beginning so it's not completely silent
                beep_freq = 440  # A4 note
                beep_duration = 0.1  # seconds
                t = np.linspace(0, beep_duration, int(beep_duration * sample_rate), False)
                beep = 0.1 * np.sin(2 * np.pi * beep_freq * t)
                samples[:len(beep)] = beep
                
                # Save as WAV
                wavfile.write(outputFilename, sample_rate, samples)
                print(f"Created emergency audio file: {outputFilename}")
                
            except Exception as final_error:
                print(f"All audio generation methods failed: {final_error}")
                raise
```

## Step 5: Set up your Pexels API Key

You need a valid Pexels API key to get videos. [Register for free at Pexels](https://www.pexels.com/api/).

```python
import os
# Replace with your actual Pexels API key
os.environ['PEXELS_KEY'] = "YOUR_PEXELS_API_KEY_HERE"
```

## Step 6: Run the App

```python
# Run with the example script
!python app.py --file test_script.txt --force-gpu
```

Or create your own script:

```python
# Create a custom script
with open("my_script.txt", "w") as f:
    f.write("""
    Text-To-Video AI converts your text into engaging videos.
    It searches for the right visuals based on your content.
    Nature scenes like mountains and oceans look amazing in video.
    Technology continues to advance at an incredible pace.
    The universe contains billions of galaxies with countless stars.
    """)

# Run with your custom script
!python app.py --file my_script.txt --force-gpu
```

## Troubleshooting

If you still encounter issues:

1. **Missing librosa**: Install manually with `!pip install librosa`
2. **CUDA errors**: Use CPU mode with `--force-cpu` flag
3. **File not found errors**: Make sure paths are correct, use absolute paths

## View the Generated Video

After successful generation, you'll find `final_video.mp4` in the working directory. View it with:

```python
from IPython.display import HTML
from base64 import b64encode

# Display the final video
video_path = "final_video.mp4"
if os.path.exists(video_path): 
    mp4 = open(video_path, 'rb').read()
    data_url = "data:video/mp4;base64," + b64encode(mp4).decode()
    display(HTML(f"""
    <video width=640 height=360 controls>
        <source src="{data_url}" type="video/mp4">
    </video>
    """))
else:
    print("Video file not found!")
``` 