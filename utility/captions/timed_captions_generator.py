import whisper_timestamped as whisper
from whisper_timestamped import load_model, transcribe_timestamped
import re
import os
import numpy as np
import soundfile as sf
from .dummy_captions_generator import generate_dummy_captions
from .audio_processor import preprocess_audio

def validate_audio_file(audio_filename):
    """Validate that the audio file exists and is readable"""
    if not os.path.exists(audio_filename):
        raise FileNotFoundError(f"Audio file not found: {audio_filename}")
    
    try:
        # Try to read the audio file
        data, samplerate = sf.read(audio_filename)
        if len(data) == 0:
            raise ValueError("Audio file is empty")
        return True
    except Exception as e:
        raise ValueError(f"Invalid audio file: {str(e)}")

def generate_timed_captions(audio_filename, model_size="base"):
    """Generate timed captions from audio file with robust error handling"""
    try:
        # Validate audio file first
        validate_audio_file(audio_filename)
        
        # Preprocess audio
        audio_data = preprocess_audio(audio_filename)
        if audio_data is None:
            print("Failed to preprocess audio, falling back to dummy captions")
            return generate_dummy_captions("", audio_filename, duration=30.0)
        
        # Try to load the Whisper model
        try:
            print(f"Loading Whisper model ({model_size})...")
            WHISPER_MODEL = load_model(model_size)
            if WHISPER_MODEL is None:
                raise ValueError("Failed to load Whisper model")
        except Exception as model_error:
            print(f"Failed to load Whisper model: {str(model_error)}")
            return generate_dummy_captions("", audio_filename, duration=30.0)
        
        # Try to transcribe the audio
        try:
            print("Transcribing audio...")
            gen = transcribe_timestamped(
                WHISPER_MODEL, 
                audio_data,  # Use preprocessed audio data
                verbose=True,
                fp16=False,
                language="en"
            )
            
            # Validate transcription results
            if not gen or not isinstance(gen, dict):
                raise ValueError("Invalid transcription results")
            if 'segments' not in gen or not gen['segments']:
                raise ValueError("No segments found in transcription")
                
        except Exception as transcribe_error:
            print(f"Failed to transcribe audio: {str(transcribe_error)}")
            return generate_dummy_captions("", audio_filename, duration=30.0)
        
        # Process the transcription
        try:
            print("Processing transcription...")
            captions = getCaptionsWithTime(gen)
            if not captions:
                raise ValueError("No captions generated")
            return captions
        except Exception as process_error:
            print(f"Failed to process transcription: {str(process_error)}")
            return generate_dummy_captions("", audio_filename, duration=30.0)
            
    except Exception as e:
        print(f"Unexpected error in caption generation: {str(e)}")
        print("Falling back to dummy captions...")
        try:
            # Try to read the script from the audio filename
            script_file = os.path.splitext(audio_filename)[0] + ".txt"
            if os.path.exists(script_file):
                with open(script_file, 'r', encoding='utf-8') as f:
                    script = f.read()
            else:
                script = "No script available. Using placeholder captions."
            return generate_dummy_captions(script, audio_filename, duration=30.0)
        except Exception as dummy_error:
            print(f"Error generating dummy captions: {str(dummy_error)}")
            return generate_dummy_captions("", audio_filename, duration=30.0)

def splitWordsBySize(words, maxCaptionSize):
   
    halfCaptionSize = maxCaptionSize / 2
    captions = []
    while words:
        caption = words[0]
        words = words[1:]
        while words and len(caption + ' ' + words[0]) <= maxCaptionSize:
            caption += ' ' + words[0]
            words = words[1:]
            if len(caption) >= halfCaptionSize and words:
                break
        captions.append(caption)
    return captions

def getTimestampMapping(whisper_analysis):
   
    index = 0
    locationToTimestamp = {}
    for segment in whisper_analysis['segments']:
        for word in segment['words']:
            newIndex = index + len(word['text'])+1
            locationToTimestamp[(index, newIndex)] = word['end']
            index = newIndex
    return locationToTimestamp

def cleanWord(word):
   
    return re.sub(r'[^\w\s\-_"\'\']', '', word)

def interpolateTimeFromDict(word_position, d):
   
    for key, value in d.items():
        if key[0] <= word_position <= key[1]:
            return value
    return None

def getCaptionsWithTime(whisper_analysis, maxCaptionSize=15, considerPunctuation=False):
   
    wordLocationToTime = getTimestampMapping(whisper_analysis)
    position = 0
    start_time = 0
    CaptionsPairs = []
    text = whisper_analysis['text']
    
    if considerPunctuation:
        sentences = re.split(r'(?<=[.!?]) +', text)
        words = [word for sentence in sentences for word in splitWordsBySize(sentence.split(), maxCaptionSize)]
    else:
        words = text.split()
        words = [cleanWord(word) for word in splitWordsBySize(words, maxCaptionSize)]
    
    for word in words:
        position += len(word) + 1
        end_time = interpolateTimeFromDict(position, wordLocationToTime)
        if end_time and word:
            CaptionsPairs.append(((start_time, end_time), word))
            start_time = end_time

    return CaptionsPairs
