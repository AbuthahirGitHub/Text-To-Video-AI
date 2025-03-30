"""
Dummy captions generator for environments where audio processing fails.
"""

def generate_dummy_captions(script, audio_file, duration=30.0):
    """
    Generate dummy timed captions from a script when audio processing fails.
    
    Args:
        script (str): The script text
        audio_file (str): The audio file path (ignored in this implementation)
        duration (float): The total duration to spread captions across
        
    Returns:
        list: A list of timed caption segments in the format [[time_start, time_end], "caption text"]
    """
    # Split the script into sentences
    import re
    sentences = re.split(r'(?<=[.!?])\s+', script)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if not sentences:
        # If no sentences, create a dummy one
        sentences = ["No captions available."]
    
    # Calculate time per sentence
    time_per_sentence = duration / len(sentences)
    
    # Create timed captions
    timed_captions = []
    for i, sentence in enumerate(sentences):
        start_time = i * time_per_sentence
        end_time = (i + 1) * time_per_sentence
        timed_captions.append([[start_time, end_time], sentence])
    
    return timed_captions

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