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





