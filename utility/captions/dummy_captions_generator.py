"""
Dummy captions generator for environments where audio processing fails.
"""

import os
import re
import random

def generate_dummy_captions(script_text, audio_filename=None, duration=30.0):
    """
    Generate dummy timed captions when actual transcription fails.
    This provides fallback timing information based on a script.
    
    Args:
        script_text (str): The script text to split into segments
        audio_filename (str, optional): Path to the audio file (for duration estimation)
        duration (float, optional): Default duration if audio file can't be read
        
    Returns:
        list: List of timed captions in the format [[(start_time, end_time), text], ...]
    """
    print("Generating dummy captions as fallback...")
    
    # Try to get duration from audio file if available
    if audio_filename and os.path.exists(audio_filename):
        try:
            import soundfile as sf
            audio_data, samplerate = sf.read(audio_filename)
            duration = len(audio_data) / samplerate
            print(f"Using audio duration: {duration:.2f} seconds")
        except Exception as e:
            print(f"Could not read audio duration: {e}")
            print(f"Using default duration: {duration} seconds")
    
    # Clean up script text
    if not script_text or not isinstance(script_text, str):
        script_text = "Placeholder text for dummy captions."
    
    # Split the script into sentences
    sentences = re.split(r'(?<=[.!?])\s+', script_text.strip())
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # If no sentences found, create a dummy sentence
    if not sentences:
        sentences = ["This is a dummy caption for the video."]
    
    # Calculate timing based on sentence count and duration
    segment_count = len(sentences)
    segment_duration = duration / segment_count
    
    # Generate timed captions
    captions = []
    current_time = 0.0
    
    for sentence in sentences:
        # Vary sentence duration slightly to make it more natural
        # (between 80% and 120% of average)
        variation = random.uniform(0.8, 1.2)
        sentence_duration = segment_duration * variation
        
        # Ensure we don't exceed total duration
        if current_time + sentence_duration > duration:
            sentence_duration = duration - current_time
        
        # Only add if we have a positive duration
        if sentence_duration > 0:
            end_time = current_time + sentence_duration
            captions.append([(current_time, end_time), sentence])
            current_time = end_time
        
        # Stop if we've reached the total duration
        if current_time >= duration:
            break
    
    print(f"Generated {len(captions)} dummy caption segments")
    return captions

def generate_timed_captions(audio_file):
    """
    Drop-in replacement for the real generate_timed_captions function.
    """
    print("Using dummy captions generator")
    
    # In a real implementation, this would analyze the audio file
    # Instead, we'll create dummy captions with a generic script
    dummy_script = """
    Welcome to this video. This is a placeholder caption created by the dummy caption generator.
    These captions are evenly spaced and not based on actual audio timing.
    This is used when audio processing fails or is not available.
    """
    
    return generate_dummy_captions(dummy_script, audio_file, duration=10.0)

# For testing
if __name__ == "__main__":
    test_script = "This is a test script. It has multiple sentences. We're testing the dummy caption generator."
    captions = generate_dummy_captions(test_script, duration=10.0)
    
    for (start, end), text in captions:
        print(f"{start:.2f} - {end:.2f}: {text}") 