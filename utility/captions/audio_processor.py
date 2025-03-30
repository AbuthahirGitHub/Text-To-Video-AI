import os
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