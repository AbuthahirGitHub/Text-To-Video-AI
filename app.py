import os
import edge_tts
import json
import asyncio
import whisper_timestamped as whisper
from utility.script.script_generator import generate_script
from utility.audio.audio_generator import generate_audio
from utility.captions.timed_captions_generator import generate_timed_captions
from utility.video.background_video_generator import generate_video_url
from utility.render.render_engine import get_output_media
from utility.video.video_search_query_generator import getVideoSearchQueriesTimed, merge_empty_intervals
import argparse
import sys

def read_script_file(file_path):
    """Read script from a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        raise ValueError(f"Error reading script file: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Generate a video from a script.")
    
    # Require exactly one of these arguments
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--text', type=str, help='Direct text input for the script')
    input_group.add_argument('--file', type=str, help='Path to a text file containing the script')
    
    try:
        args = parser.parse_args()
    except:
        # If there's a problem parsing arguments, print usage and exit
        parser.print_help()
        sys.exit(1)
    
    SAMPLE_FILE_NAME = "audio_tts.wav"
    VIDEO_SERVER = "pexel"
    OUTPUT_VIDEO_NAME = "final_video.mp4"

    try:
        # Get script content either from direct text or file
        script_content = read_script_file(args.file) if args.file else args.text
        
        # Process the input script
        script = generate_script(script_content)
        print("Script to be used:")
        print(script)
        print("\nGenerating audio...")
        
        # Generate audio with error handling
        try:
            asyncio.run(generate_audio(script, SAMPLE_FILE_NAME))
            print("Audio generated successfully")
        except Exception as e:
            print(f"Warning: Audio generation encountered issues: {str(e)}")
            print("Attempting to continue...")

        # Generate captions
        print("\nGenerating captions...")
        timed_captions = generate_timed_captions(SAMPLE_FILE_NAME)
        print("Captions generated successfully")

        # Generate video search terms
        print("\nGenerating video search terms...")
        search_terms = getVideoSearchQueriesTimed(script, timed_captions)
        if search_terms:
            print("Search terms generated successfully")
        else:
            print("No search terms generated")

        # Get background videos
        background_video_urls = None
        if search_terms is not None:
            print("\nFetching background videos...")
            background_video_urls = generate_video_url(search_terms, VIDEO_SERVER)
            if background_video_urls:
                print("Background videos fetched successfully")
            else:
                print("No background videos found")

        background_video_urls = merge_empty_intervals(background_video_urls)

        # Render final video
        if background_video_urls is not None:
            print("\nRendering final video...")
            video = get_output_media(SAMPLE_FILE_NAME, timed_captions, background_video_urls, VIDEO_SERVER)
            print(f"\nVideo generated successfully: {OUTPUT_VIDEO_NAME}")
        else:
            print("\nError: Could not generate video due to missing background videos")

    except Exception as e:
        print(f"\nError: {str(e)}")
        return 1

    return 0

if __name__ == "__main__":
    # Configure environment for audio
    try:
        # Windows-specific path adjustments
        if os.name == 'nt':
            temp_dir = os.environ.get('TEMP', 'C:\\Windows\\Temp')
            runtime_dir = os.path.join(temp_dir, 'runtime-dir')
        else:
            # Linux/Mac paths
            runtime_dir = '/tmp/runtime-dir'
            
        os.environ['XDG_RUNTIME_DIR'] = runtime_dir
        os.makedirs(runtime_dir, mode=0o700, exist_ok=True)
    except Exception as e:
        print(f"Warning: Could not set up environment directories: {str(e)}")
    
    # Exit with the main function's return code
    sys.exit(main())
